from enum import Enum
from typing import Dict, Any, Tuple

class PermissionLevel(Enum):
    READ_ONLY = 0
    ORGANIZE = 1
    CREATE = 2
    DELETE_SEND = 3
    EXTERNAL = 4

class PolicyEngine:
    def __init__(self):
        # Default policies mapping tool name to required permission level
        self.policies = {
            "get_current_time": PermissionLevel.READ_ONLY,
            "read_recent_emails": PermissionLevel.READ_ONLY,
            "archive_email": PermissionLevel.ORGANIZE,
            "create_event": PermissionLevel.CREATE,
            "delete_email": PermissionLevel.DELETE_SEND,
        }

    def check_permission(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        level = self.policies.get(tool_name, PermissionLevel.EXTERNAL)
        
        if level == PermissionLevel.READ_ONLY:
            return True, "Allowed by policy (READ_ONLY)"
            
        elif level == PermissionLevel.ORGANIZE:
            return True, "Allowed by policy (ORGANIZE)"
            
        elif level in [PermissionLevel.CREATE, PermissionLevel.DELETE_SEND, PermissionLevel.EXTERNAL]:
            return False, f"Requires Human Approval (Level: {level.name})"
            
        return False, "Unknown tool"
