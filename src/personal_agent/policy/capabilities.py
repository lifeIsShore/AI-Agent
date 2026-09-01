from typing import Dict, Tuple, Optional
from personal_agent.security.principal import Principal, PRINCIPAL_SCHEDULER

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
    "read_recent_emails": CAPABILITY_GMAIL_READ,
    "classify_email": CAPABILITY_GMAIL_READ,
    "evaluate_inbox_zero": CAPABILITY_GMAIL_READ,
    "archive_email": CAPABILITY_GMAIL_ARCHIVE,
    "trash_email": CAPABILITY_GMAIL_TRASH,
    "delete_email": CAPABILITY_GMAIL_TRASH,
    "send_email": CAPABILITY_GMAIL_SEND,
    "create_draft": CAPABILITY_GMAIL_SEND,
    "mark_read": CAPABILITY_GMAIL_LABEL,
    "mark_unread": CAPABILITY_GMAIL_LABEL,
    "apply_label": CAPABILITY_GMAIL_LABEL,
    "create_label": CAPABILITY_GMAIL_LABEL,
    "get_today_events": CAPABILITY_CALENDAR_READ,
    "get_week_events": CAPABILITY_CALENDAR_READ,
    "get_free_slots": CAPABILITY_CALENDAR_READ,
    "create_calendar_event": CAPABILITY_CALENDAR_CREATE,
    "update_calendar_event": CAPABILITY_CALENDAR_UPDATE,
    "delete_calendar_event": CAPABILITY_CALENDAR_DELETE,
    "get_active_tasks": CAPABILITY_TASKS_READ,
    "list_tasks": CAPABILITY_TASKS_READ,
    "get_task": CAPABILITY_TASKS_READ,
    "create_task": CAPABILITY_TASKS_CREATE,
    "update_task": CAPABILITY_TASKS_CREATE,
    "complete_task": CAPABILITY_TASKS_COMPLETE,
    "delete_task": CAPABILITY_TASKS_DELETE,
    "generate_daily_plan": "system.read",
    "propose_schedule": "system.read",
    "propose_task": "system.read",
    "propose_inbox_zero": "system.read",
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

def get_target_aware_capability_risk(capability: str, target: str) -> str:
    """Calculates multi-factor risk based on capability sensitivity and target scope."""
    base_risk = CAPABILITY_RISK_MAP.get(capability, RISK_HIGH)
    
    # Target scope sensitivity escalation
    if target in ["all", "inbox_all", "all_emails", "all_calendars", "*"]:
        if base_risk == RISK_MEDIUM:
            return RISK_HIGH
        elif base_risk == RISK_HIGH:
            return RISK_CRITICAL

    return base_risk

def validate_capability_authorization(
    capability: Optional[str],
    principal: Optional[Principal] = None,
    target: str = "",
    user_approved: bool = False
) -> Tuple[bool, str]:
    """Evaluates capability authorization under Principal Identity and Target-Aware Policy invariants."""
    if not capability:
        return False, "DENIED: Unknown capability scope (fail closed)."

    # Principal scope check for Scheduler
    if principal and principal.is_scheduler():
        if capability in [CAPABILITY_GMAIL_TRASH, CAPABILITY_GMAIL_SEND, CAPABILITY_CALENDAR_DELETE]:
            return False, f"DENIED: Scheduler principal '{principal.principal_id}' is restricted from executing high-risk capability '{capability}'."

    risk = get_target_aware_capability_risk(capability, target)
    if risk == RISK_LOW:
        return True, f"Allowed by capability policy ({capability} - READ_ONLY / LOW risk)"
    
    if risk in [RISK_MEDIUM, RISK_HIGH]:
        if user_approved:
            return True, f"Allowed by explicit human approval for capability ({capability})"
        return False, f"Requires Human Authorization for capability '{capability}' (Risk: {risk})."

    return False, f"DENIED: Capability '{capability}' on target '{target}' is CRITICAL."
