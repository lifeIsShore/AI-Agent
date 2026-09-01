import time
from typing import List, Dict, Any, Optional, Tuple
from personal_agent.policy.proposal import (
    ActionProposal, STATUS_PENDING_APPROVAL, STATUS_APPROVED, STATUS_REJECTED, STATUS_EXECUTED, STATUS_FAILED, STATUS_EXPIRED
)
from personal_agent.tools.registry import ToolRegistry
from personal_agent.security.audit import AuditLogger

class ApprovalQueue:
    def __init__(self, tool_registry: ToolRegistry, audit_logger: Optional[AuditLogger] = None, memory_loop: Optional[Any] = None):
        self.registry = tool_registry
        self.audit_logger = audit_logger or AuditLogger()
        self.memory_loop = memory_loop
        self.queue: Dict[str, ActionProposal] = {}

    def add_proposal(self, proposal: ActionProposal):
        """Adds an ActionProposal to the approval queue."""
        self.queue[proposal.proposal_id] = proposal

    def list_pending(self) -> List[ActionProposal]:
        """Returns all proposals currently waiting for human approval."""
        return [p for p in self.queue.values() if p.status == STATUS_PENDING_APPROVAL and not p.is_expired()]

    def get_proposal(self, proposal_id: str) -> Optional[ActionProposal]:
        """Retrieves a proposal by its ID."""
        return self.queue.get(proposal_id)

    def get_proposal_details(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Returns detailed explainability breakdown for a proposal."""
        prop = self.get_proposal(proposal_id)
        if not prop:
            return None

        return {
            "proposal_id": prop.proposal_id,
            "action": prop.action,
            "target": prop.target,
            "parameters": prop.parameters,
            "reason": prop.reason,
            "confidence": f"{int(prop.confidence * 100)}%",
            "risk_level": prop.risk_level,
            "required_permission": prop.required_permission,
            "created_at": prop.created_at,
            "expires_at": prop.expires_at,
            "is_expired": prop.is_expired(),
            "why_proposed": prop.why_proposed,
            "target_checksum": prop.target_checksum
        }

    def approve_proposal(
        self,
        proposal_id: str,
        edited_params: Optional[Dict[str, Any]] = None,
        target_validator: Optional[Any] = None
    ) -> Tuple[bool, str, Optional[Any]]:
        """Approves (and optionally edits parameters for) a pending proposal, executes the tool, logs audit, and notifies memory loop."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            return False, f"Proposal ID '{proposal_id}' not found in queue.", None

        # Expiration Check
        if proposal.is_expired():
            proposal.status = STATUS_EXPIRED
            self.audit_logger.log_proposal(
                proposal=proposal,
                policy_decision="Approval attempted after TTL expiration",
                user_approved=True,
                execution_status="EXPIRED",
                execution_result="Execution blocked due to proposal expiration"
            )
            return False, f"Proposal '{proposal_id}' has expired (TTL exceeded). Execution blocked.", None

        if proposal.status != STATUS_PENDING_APPROVAL:
            return False, f"Proposal '{proposal_id}' is not in PENDING_APPROVAL state (current: {proposal.status}).", None

        # Stale Target Validation Check (if target validator callback supplied)
        if target_validator and callable(target_validator):
            isValid, reason = target_validator(proposal.target, proposal.target_checksum)
            if not isValid:
                proposal.status = STATUS_FAILED
                self.audit_logger.log_proposal(
                    proposal=proposal,
                    policy_decision=f"Target state validation failed: {reason}",
                    user_approved=True,
                    execution_status="STALE_TARGET",
                    execution_result=reason
                )
                return False, f"Target state changed: {reason}. Proposal re-evaluation required.", None

        # Apply edited parameters if provided
        if edited_params:
            proposal.parameters.update(edited_params)
            proposal.audit_metadata["edited_by_user"] = True

        proposal.status = STATUS_APPROVED
        func = self.registry.get_tool(proposal.action)
        if not func:
            proposal.status = STATUS_FAILED
            reason = f"Tool function '{proposal.action}' not registered in ToolRegistry."
            self.audit_logger.log_proposal(
                proposal=proposal,
                policy_decision="Approved by user but execution failed",
                user_approved=True,
                execution_status="FAILED",
                execution_result=reason
            )
            return False, reason, None

        # Execute Tool Action
        start_time = time.time()
        try:
            result = func(**proposal.parameters)
            elapsed = time.time() - start_time
            proposal.status = STATUS_EXECUTED

            # Log to Audit Logger
            self.audit_logger.log_proposal(
                proposal=proposal,
                policy_decision="Approved and executed by user request",
                user_approved=True,
                execution_status="SUCCESS",
                execution_result=result,
                latency_sec=elapsed
            )

            # Trigger Memory Learning Feedback Loop if available
            if self.memory_loop:
                try:
                    self.memory_loop.record_feedback(proposal=proposal, user_decision="APPROVED")
                except Exception as e:
                    print(f"[ApprovalQueue] Error recording memory feedback: {e}")

            return True, f"Proposal '{proposal_id}' approved and executed successfully.", result

        except Exception as e:
            elapsed = time.time() - start_time
            proposal.status = STATUS_FAILED
            err_msg = str(e)
            self.audit_logger.log_proposal(
                proposal=proposal,
                policy_decision="Approved by user but execution threw exception",
                user_approved=True,
                execution_status="FAILED",
                execution_result=err_msg,
                latency_sec=elapsed
            )
            return False, f"Tool execution failed: {err_msg}", None

    def reject_proposal(self, proposal_id: str, reason: Optional[str] = None) -> Tuple[bool, str]:
        """Rejects a pending proposal, logs audit record, and triggers memory learning signal."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            return False, f"Proposal ID '{proposal_id}' not found in queue."

        if proposal.status != STATUS_PENDING_APPROVAL:
            return False, f"Proposal '{proposal_id}' is not in PENDING_APPROVAL state (current: {proposal.status})."

        proposal.status = STATUS_REJECTED
        reject_reason = reason or "User explicitly rejected proposal"

        self.audit_logger.log_proposal(
            proposal=proposal,
            policy_decision=f"Rejected by user: {reject_reason}",
            user_approved=False,
            execution_status="REJECTED",
            execution_result=None,
            latency_sec=0.0
        )

        # Trigger Memory Learning Feedback Loop if available
        if self.memory_loop:
            try:
                self.memory_loop.record_feedback(proposal=proposal, user_decision="REJECTED", user_reason=reject_reason)
            except Exception as e:
                print(f"[ApprovalQueue] Error recording memory feedback: {e}")

        return True, f"Proposal '{proposal_id}' rejected."

    def approve_batch(self, proposal_ids: List[str]) -> List[Tuple[bool, str, Optional[Any]]]:
        """Safely approves a batch of proposals by evaluating each item through individual approval checks."""
        results = []
        for pid in proposal_ids:
            res = self.approve_proposal(pid)
            results.append(res)
        return results

    def reject_batch(self, proposal_ids: List[str], reason: Optional[str] = None) -> List[Tuple[bool, str]]:
        """Safely rejects a batch of proposals by processing each item through individual rejection checks."""
        results = []
        for pid in proposal_ids:
            res = self.reject_proposal(pid, reason=reason)
            results.append(res)
        return results
