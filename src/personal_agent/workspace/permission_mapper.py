from typing import Tuple, Dict, Any, List

WORKSPACE_SCOPES = {
    "gmail": ["gmail.read", "gmail.send"],
    "calendar": ["calendar.read", "calendar.modify"],
    "drive": ["drive.read", "drive.write", "drive.delete"],
    "browser": ["browser.read", "browser.external_action"]
}

class PermissionMapper:
    def map_workspace_action_permission(
        self,
        source_system: str,
        action_type: str,
        user_approved: bool = False
    ) -> Tuple[bool, str]:
        """Evaluates workspace action permissions against explicit capability rules."""
        sys_scopes = WORKSPACE_SCOPES.get(source_system.lower(), [])

        # Invariant: External write/send/action strictly requires human approval or explicit grant
        if "send" in action_type.lower() or "delete" in action_type.lower() or "external_action" in action_type.lower():
            if not user_approved:
                return False, f"PermissionMapper BLOCKED: '{source_system}.{action_type}' requires explicit human approval."

        return True, f"PermissionMapper ALLOWED: '{source_system}.{action_type}' permitted under workspace policy."
