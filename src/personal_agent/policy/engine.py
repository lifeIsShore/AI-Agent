from enum import Enum
from typing import Dict, Any, Tuple

class PermissionLevel(Enum):
    READ_ONLY = 0
    ANALYZE = 1
    PROPOSE = 2
    MODIFY = 3
    ADMIN = 4

class PolicyEngine:
    def __init__(self):
        # Explicit V0.5 & V0.6 Security Policy Mapping
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

    def get_permission_level(self, tool_name: str) -> PermissionLevel:
        return self.policies.get(tool_name, PermissionLevel.MODIFY)

    def check_permission(self, tool_name: str, args: Dict[str, Any], user_approved: bool = False) -> Tuple[bool, str]:
        level = self.get_permission_level(tool_name)
        
        if level in [PermissionLevel.READ_ONLY, PermissionLevel.ANALYZE, PermissionLevel.PROPOSE]:
            return True, f"Allowed by policy ({level.name})"
            
        elif level in [PermissionLevel.MODIFY, PermissionLevel.ADMIN]:
            if user_approved:
                return True, f"Allowed by explicit human approval ({level.name})"
            return False, f"Requires Human Approval (Level: {level.name})"
            
        return False, "Unknown tool permission level"
