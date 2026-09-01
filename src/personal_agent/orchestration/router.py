from typing import Tuple, Dict, Any, Optional

CAPABILITY_TOOL_MAP: Dict[str, str] = {
    "gmail.read": "list_recent_emails",
    "gmail.archive": "archive_email",
    "gmail.label": "mark_read",
    "calendar.read": "get_today_events",
    "calendar.create": "create_calendar_event",
    "tasks.read": "list_tasks",
    "tasks.create": "create_task",
    "system.read": "get_current_time"
}

class ToolRouter:
    def resolve_tool_for_capability(
        self,
        required_capability: str,
        requested_tool: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """Resolves tool selection deterministically. LLM tool proposals NEVER bypass capability routing."""
        mapped_tool = CAPABILITY_TOOL_MAP.get(required_capability)
        if not mapped_tool:
            return False, "", f"No tool registered for capability '{required_capability}'."

        if requested_tool and requested_tool != mapped_tool:
            # Overriding unauthorized tool attempt with deterministic capability tool
            return True, mapped_tool, f"Override: Corrected requested tool '{requested_tool}' to capability tool '{mapped_tool}' for '{required_capability}'."

        return True, mapped_tool, f"Resolved capability '{required_capability}' to tool '{mapped_tool}'."
