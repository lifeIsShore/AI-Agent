import time
from typing import List, Dict, Any, Optional, Tuple
from personal_agent.policy.proposal import (
    ActionProposal, STATUS_PENDING_APPROVAL, STATUS_APPROVED, STATUS_REJECTED, STATUS_EXECUTED, STATUS_FAILED
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
        return [p for p in self.queue.values() if p.status == STATUS_PENDING_APPROVAL]

    def get_proposal(self, proposal_id: str) -> Optional[ActionProposal]:
        """Retrieves a proposal by its ID."""
        return self.queue.get(proposal_id)

    def approve_proposal(
        self,
        proposal_id: str,
        edited_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Optional[Any]]:
        """Approves (and optionally edits parameters for) a pending proposal, executes the tool, logs audit, and notifies memory loop."""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            return False, f"Proposal ID '{proposal_id}' not found in queue.", None

        if proposal.status != STATUS_PENDING_APPROVAL:
            return False, f"Proposal '{proposal_id}' is not in PENDING_APPROVAL state (current: {proposal.status}).", None

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
