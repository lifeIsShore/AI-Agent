from enum import Enum
from typing import Dict, Any, Tuple, Optional
from personal_agent.policy.proposal import ActionProposal

class PermissionLevel(Enum):
    READ_ONLY = 0
    ANALYZE = 1
    PROPOSE = 2
    MODIFY = 3
    ADMIN = 4

class PolicyEngine:
    def __init__(self):
        # Explicit Security Policy Mapping
        self.policies = {
            # READ_ONLY (Level 0)
            "get_current_time": PermissionLevel.READ_ONLY,
            "read_recent_emails": PermissionLevel.READ_ONLY,
            "get_today_events": PermissionLevel.READ_ONLY,
            "get_week_events": PermissionLevel.READ_ONLY,
            "list_tasks": PermissionLevel.READ_ONLY,
            "get_task": PermissionLevel.READ_ONLY,
            
            # ANALYZE (Level 1)
            "get_free_slots": PermissionLevel.ANALYZE,
            "classify_email": PermissionLevel.ANALYZE,
            "evaluate_inbox_zero": PermissionLevel.ANALYZE,
            
            # PROPOSE (Level 2)
            "generate_daily_plan": PermissionLevel.PROPOSE,
            "propose_schedule": PermissionLevel.PROPOSE,
            "propose_task": PermissionLevel.PROPOSE,
            "propose_inbox_zero": PermissionLevel.PROPOSE,
            
            # MODIFY (Level 3 - Requires Explicit Human Approval)
            "create_calendar_event": PermissionLevel.MODIFY,
            "update_calendar_event": PermissionLevel.MODIFY,
            "delete_calendar_event": PermissionLevel.MODIFY,
            "create_task": PermissionLevel.MODIFY,
            "update_task": PermissionLevel.MODIFY,
            "complete_task": PermissionLevel.MODIFY,
            "archive_email": PermissionLevel.MODIFY,
            "trash_email": PermissionLevel.MODIFY,
            "apply_label": PermissionLevel.MODIFY,
            "create_label": PermissionLevel.MODIFY,
            "mark_read": PermissionLevel.MODIFY,
            "mark_unread": PermissionLevel.MODIFY,
            "create_draft": PermissionLevel.MODIFY,
            "delete_email": PermissionLevel.MODIFY,
            "send_email": PermissionLevel.MODIFY
        }

        # Risk Level Mappings
        self.risk_levels = {
            PermissionLevel.READ_ONLY: "LOW",
            PermissionLevel.ANALYZE: "LOW",
            PermissionLevel.PROPOSE: "LOW",
            PermissionLevel.MODIFY: "MEDIUM",
            PermissionLevel.ADMIN: "CRITICAL"
        }

        # High/Critical risk actions override
        self.high_risk_actions = {"trash_email", "delete_email", "delete_calendar_event", "send_email"}

    def get_permission_level(self, tool_name: str) -> PermissionLevel:
        return self.policies.get(tool_name, PermissionLevel.MODIFY)

    def get_risk_level(self, tool_name: str) -> str:
        if tool_name in self.high_risk_actions:
            return "HIGH"
        level = self.get_permission_level(tool_name)
        return self.risk_levels.get(level, "MEDIUM")

    def create_proposal(
        self,
        action: str,
        target: str,
        parameters: Dict[str, Any],
        reason: str = "",
        confidence: float = 1.0
    ) -> ActionProposal:
        """Helper to instantiate a formal ActionProposal with inferred security levels."""
        perm_level = self.get_permission_level(action)
        risk_level = self.get_risk_level(action)
        
        return ActionProposal(
            action=action,
            target=target,
            parameters=parameters,
            reason=reason,
            confidence=confidence,
            risk_level=risk_level,
            required_permission=perm_level.name,
            status="PENDING"
        )

    def check_proposal(self, proposal: ActionProposal, user_approved: bool = False) -> Tuple[bool, str]:
        """Evaluates an ActionProposal object against policy and human approval requirements."""
        perm_level = self.get_permission_level(proposal.action)
        proposal.required_permission = perm_level.name
        proposal.risk_level = self.get_risk_level(proposal.action)

        if perm_level in [PermissionLevel.READ_ONLY, PermissionLevel.ANALYZE, PermissionLevel.PROPOSE]:
            proposal.status = "APPROVED"
            return True, f"Allowed by policy ({perm_level.name})"

        elif perm_level in [PermissionLevel.MODIFY, PermissionLevel.ADMIN]:
            if user_approved:
                proposal.status = "APPROVED"
                return True, f"Allowed by explicit human approval ({proposal.risk_level} risk)"
            else:
                proposal.status = "DENIED"
                return False, f"Requires Human Approval ({proposal.risk_level} risk)"

        return False, "Unknown tool permission level"

    def check_permission(self, tool_name: str, args: Dict[str, Any], user_approved: bool = False) -> Tuple[bool, str]:
        """Legacy helper matching check_proposal behavior."""
        proposal = self.create_proposal(action=tool_name, target=str(args.get("msg_id", args.get("event_id", "target"))), parameters=args)
        return self.check_proposal(proposal, user_approved=user_approved)
