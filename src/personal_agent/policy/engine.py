from enum import Enum
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional, List
from personal_agent.policy.proposal import (
    ActionProposal, STATUS_PROPOSED, STATUS_AUTO_APPROVED, STATUS_PENDING_APPROVAL, STATUS_DENIED, STATUS_APPROVED, STATUS_EXPIRED
)
from personal_agent.policy.capabilities import (
    resolve_capability, get_target_aware_capability_risk, validate_capability_authorization
)
from personal_agent.policy.authorization import (
    AuthorizationDecision, DECISION_ALLOW, DECISION_DENY, DECISION_REQUIRE_APPROVAL
)
from personal_agent.security.principal import Principal
from personal_agent.security.identity import IdentityProvider

class PermissionLevel(Enum):
    READ_ONLY = 0
    ANALYZE = 1
    PROPOSE = 2
    MODIFY = 3
    ADMIN = 4

class PolicyEngine:
    def __init__(self):
        self.high_risk_actions = {"trash_email", "delete_email", "delete_calendar_event", "send_email"}
        self.policies = {
            "get_current_time": PermissionLevel.READ_ONLY,
            "read_recent_emails": PermissionLevel.READ_ONLY,
            "get_today_events": PermissionLevel.READ_ONLY,
            "get_week_events": PermissionLevel.READ_ONLY,
            "list_tasks": PermissionLevel.READ_ONLY,
            "get_task": PermissionLevel.READ_ONLY,
            "get_free_slots": PermissionLevel.ANALYZE,
            "classify_email": PermissionLevel.ANALYZE,
            "evaluate_inbox_zero": PermissionLevel.ANALYZE,
            "generate_daily_plan": PermissionLevel.PROPOSE,
            "propose_schedule": PermissionLevel.PROPOSE,
            "propose_task": PermissionLevel.PROPOSE,
            "propose_inbox_zero": PermissionLevel.PROPOSE,
            "create_calendar_event": PermissionLevel.MODIFY,
            "update_calendar_event": PermissionLevel.MODIFY,
            "delete_calendar_event": PermissionLevel.MODIFY,
            "create_task": PermissionLevel.MODIFY,
            "update_task": PermissionLevel.MODIFY,
            "complete_task": PermissionLevel.MODIFY,
            "archive_email": PermissionLevel.MODIFY,
            "trash_email": PermissionLevel.MODIFY,
            "apply_label": PermissionLevel.MODIFY,
            "mark_read": PermissionLevel.MODIFY,
            "delete_email": PermissionLevel.MODIFY,
            "send_email": PermissionLevel.MODIFY
        }

    def get_permission_level(self, tool_name: str) -> PermissionLevel:
        return self.policies.get(tool_name, PermissionLevel.MODIFY)

    def evaluate_authorization(
        self,
        proposal: ActionProposal,
        principal: Optional[Principal] = None,
        user_approved: bool = False
    ) -> AuthorizationDecision:
        """Evaluates an ActionProposal against Principal Identity, Target Sensitivity, and Capability Policy."""
        p_obj = principal or IdentityProvider.get_user_principal()
        cap = resolve_capability(proposal.action)
        risk = get_target_aware_capability_risk(cap or proposal.action, proposal.target)
        perm_level = self.get_permission_level(proposal.action)
        proposal.risk_level = risk

        # 1. Expiration check
        if proposal.is_expired():
            proposal.status = STATUS_EXPIRED
            return AuthorizationDecision(
                decision=DECISION_DENY,
                principal_id=p_obj.principal_id,
                principal_type=p_obj.principal_type,
                capability=cap or proposal.action,
                target=proposal.target,
                risk_level=risk,
                policy_rule="proposal_ttl_check",
                approval_required=False,
                reason="Proposal has expired (TTL exceeded)",
                expires_at=proposal.expires_at,
                parameters_hash=proposal.parameters_hash
            )

        # 2. Capability & Target Validation
        allowed, msg = validate_capability_authorization(cap, principal=p_obj, target=proposal.target, user_approved=user_approved)

        if allowed:
            status_val = STATUS_APPROVED if user_approved else STATUS_AUTO_APPROVED
            proposal.status = status_val
            if user_approved:
                full_reason = f"Allowed by explicit human approval for capability ({perm_level.name} - {cap})"
            else:
                full_reason = f"Allowed by capability policy ({perm_level.name} - {cap} - LOW risk)"
            return AuthorizationDecision(
                decision=DECISION_ALLOW,
                principal_id=p_obj.principal_id,
                principal_type=p_obj.principal_type,
                capability=cap or proposal.action,
                target=proposal.target,
                risk_level=risk,
                policy_rule="capability_authorization",
                approval_required=False,
                reason=full_reason,
                expires_at=proposal.expires_at,
                parameters_hash=proposal.parameters_hash
            )

        if "requires human authorization" in msg.lower():
            proposal.status = STATUS_PENDING_APPROVAL
            return AuthorizationDecision(
                decision=DECISION_REQUIRE_APPROVAL,
                principal_id=p_obj.principal_id,
                principal_type=p_obj.principal_type,
                capability=cap or proposal.action,
                target=proposal.target,
                risk_level=risk,
                policy_rule="capability_human_approval",
                approval_required=True,
                reason=msg,
                expires_at=proposal.expires_at,
                parameters_hash=proposal.parameters_hash
            )

        proposal.status = STATUS_DENIED
        return AuthorizationDecision(
            decision=DECISION_DENY,
            principal_id=p_obj.principal_id,
            principal_type=p_obj.principal_type,
            capability=cap or proposal.action,
            target=proposal.target,
            risk_level=risk,
            policy_rule="capability_fail_closed",
            approval_required=False,
            reason=msg,
            expires_at=proposal.expires_at,
            parameters_hash=proposal.parameters_hash
        )

    def create_proposal(
        self,
        action: str,
        target: str,
        parameters: Dict[str, Any],
        reason: str = "",
        confidence: float = 1.0,
        ttl_minutes: int = 60,
        why_proposed: Optional[List[str]] = None,
        target_checksum: Optional[str] = None
    ) -> ActionProposal:
        """Instantiates an ActionProposal with TTL expiration, explainability chain, and parameter hash."""
        cap = resolve_capability(action)
        risk_level = get_target_aware_capability_risk(cap or action, target)
        
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(minutes=ttl_minutes)).isoformat()

        reasons_chain = why_proposed or [
            f"Action '{action}' recommended for target '{target}'.",
            f"Primary reason: {reason or 'Automated task policy recommendation'}.",
            f"Capability Scope: {cap or 'custom'} | Risk Level: {risk_level}."
        ]

        return ActionProposal(
            action=action,
            target=target,
            parameters=parameters,
            reason=reason,
            confidence=confidence,
            risk_level=risk_level,
            required_permission=cap or "READ_ONLY",
            status=STATUS_PROPOSED,
            created_at=now.isoformat(),
            expires_at=expires_at,
            why_proposed=reasons_chain,
            target_checksum=target_checksum
        )

    def check_proposal(self, proposal: ActionProposal, user_approved: bool = False) -> Tuple[bool, str]:
        """Legacy helper evaluating proposal against PolicyEngine."""
        decision = self.evaluate_authorization(proposal, user_approved=user_approved)
        return decision.is_allowed(), decision.reason

    def check_permission(self, tool_name: str, args: Dict[str, Any], user_approved: bool = False) -> Tuple[bool, str]:
        """Legacy helper matching check_proposal behavior."""
        proposal = self.create_proposal(action=tool_name, target=str(args.get("msg_id", args.get("event_id", "target"))), parameters=args)
        return self.check_proposal(proposal, user_approved=user_approved)
