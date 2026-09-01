from typing import Dict, Tuple, Optional

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

CAPABILITY_GMAIL_READ = "gmail.read"
CAPABILITY_GMAIL_ARCHIVE = "gmail.archive"
CAPABILITY_GMAIL_LABEL = "gmail.label"
CAPABILITY_GMAIL_TRASH = "gmail.trash"
CAPABILITY_GMAIL_SEND = "gmail.send"

CAPABILITY_CALENDAR_READ = "calendar.read"
CAPABILITY_CALENDAR_CREATE = "calendar.create"
CAPABILITY_CALENDAR_UPDATE = "calendar.update"
CAPABILITY_CALENDAR_DELETE = "calendar.delete"

CAPABILITY_TASKS_READ = "tasks.read"
CAPABILITY_TASKS_CREATE = "tasks.create"
CAPABILITY_TASKS_COMPLETE = "tasks.complete"
CAPABILITY_TASKS_DELETE = "tasks.delete"

TOOL_TO_CAPABILITY_MAP: Dict[str, str] = {
    "list_recent_emails": CAPABILITY_GMAIL_READ,
    "archive_email": CAPABILITY_GMAIL_ARCHIVE,
    "trash_email": CAPABILITY_GMAIL_TRASH,
    "send_email": CAPABILITY_GMAIL_SEND,
    "get_today_events": CAPABILITY_CALENDAR_READ,
    "get_free_slots": CAPABILITY_CALENDAR_READ,
    "create_calendar_event": CAPABILITY_CALENDAR_CREATE,
    "delete_calendar_event": CAPABILITY_CALENDAR_DELETE,
    "get_active_tasks": CAPABILITY_TASKS_READ,
    "create_task": CAPABILITY_TASKS_CREATE,
    "complete_task": CAPABILITY_TASKS_COMPLETE,
    "delete_task": CAPABILITY_TASKS_DELETE,
    "get_current_time": "system.read"
}

CAPABILITY_RISK_MAP: Dict[str, str] = {
    CAPABILITY_GMAIL_READ: RISK_LOW,
    CAPABILITY_GMAIL_ARCHIVE: RISK_MEDIUM,
    CAPABILITY_GMAIL_LABEL: RISK_MEDIUM,
    CAPABILITY_GMAIL_TRASH: RISK_HIGH,
    CAPABILITY_GMAIL_SEND: RISK_HIGH,
    CAPABILITY_CALENDAR_READ: RISK_LOW,
    CAPABILITY_CALENDAR_CREATE: RISK_MEDIUM,
    CAPABILITY_CALENDAR_UPDATE: RISK_MEDIUM,
    CAPABILITY_CALENDAR_DELETE: RISK_HIGH,
    CAPABILITY_TASKS_READ: RISK_LOW,
    CAPABILITY_TASKS_CREATE: RISK_MEDIUM,
    CAPABILITY_TASKS_COMPLETE: RISK_MEDIUM,
    CAPABILITY_TASKS_DELETE: RISK_HIGH,
    "system.read": RISK_LOW
}

def resolve_capability(tool_name: str) -> Optional[str]:
    """Resolves tool name to granular capability scope string."""
    return TOOL_TO_CAPABILITY_MAP.get(tool_name)

def get_capability_risk(capability: str) -> str:
    """Returns risk level for a given capability scope."""
    return CAPABILITY_RISK_MAP.get(capability, RISK_HIGH)

def validate_capability_authorization(capability: Optional[str], user_approved: bool = False) -> Tuple[bool, str]:
    """Evaluates whether a capability execution is authorized under PolicyEngine invariants."""
    if not capability:
        return False, "DENIED: Unknown capability scope (fail closed)."

    risk = get_capability_risk(capability)
    if risk == RISK_LOW:
        return True, f"Allowed by capability policy ({capability} - LOW risk)"
    
    if risk in [RISK_MEDIUM, RISK_HIGH]:
        if user_approved:
            return True, f"Allowed by explicit human approval for capability ({capability})"
        return False, f"Capability '{capability}' requires explicit human approval (Risk: {risk})."

    return False, f"DENIED: Capability '{capability}' is CRITICAL."
