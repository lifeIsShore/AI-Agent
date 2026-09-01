from dataclasses import dataclass, field
from typing import List, Dict, Any

ROLE_INBOX_ANALYST = "INBOX_ANALYST"
ROLE_CALENDAR_PLANNER = "CALENDAR_PLANNER"
ROLE_TASK_PLANNER = "TASK_PLANNER"
ROLE_RESEARCH_ANALYST = "RESEARCH_ANALYST"
ROLE_EXECUTION_COORDINATOR = "EXECUTION_COORDINATOR"

@dataclass
class SpecialistRoleConfig:
    role_name: str
    permitted_capabilities: List[str]
    max_token_budget: int
    allowed_context_types: List[str]

ROLE_CONFIGS: Dict[str, SpecialistRoleConfig] = {
    ROLE_INBOX_ANALYST: SpecialistRoleConfig(
        role_name=ROLE_INBOX_ANALYST,
        permitted_capabilities=["gmail.read", "gmail.label", "gmail.archive"],
        max_token_budget=3000,
        allowed_context_types=["emails", "sender_metadata"]
    ),
    ROLE_CALENDAR_PLANNER: SpecialistRoleConfig(
        role_name=ROLE_CALENDAR_PLANNER,
        permitted_capabilities=["calendar.read", "calendar.create", "calendar.update"],
        max_token_budget=3000,
        allowed_context_types=["calendar_events", "free_slots"]
    ),
    ROLE_TASK_PLANNER: SpecialistRoleConfig(
        role_name=ROLE_TASK_PLANNER,
        permitted_capabilities=["tasks.read", "tasks.create", "tasks.update"],
        max_token_budget=2000,
        allowed_context_types=["todo_tasks"]
    ),
    ROLE_RESEARCH_ANALYST: SpecialistRoleConfig(
        role_name=ROLE_RESEARCH_ANALYST,
        permitted_capabilities=["system.read"],
        max_token_budget=4000,
        allowed_context_types=["web_docs", "notes"]
    ),
    ROLE_EXECUTION_COORDINATOR: SpecialistRoleConfig(
        role_name=ROLE_EXECUTION_COORDINATOR,
        permitted_capabilities=["system.read", "calendar.create", "gmail.archive"],
        max_token_budget=5000,
        allowed_context_types=["workflow_state", "approved_proposals"]
    )
}
