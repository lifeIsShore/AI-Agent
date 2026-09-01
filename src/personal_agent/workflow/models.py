import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

STEP_PENDING = "PENDING"
STEP_RUNNING = "RUNNING"
STEP_WAITING_APPROVAL = "WAITING_APPROVAL"
STEP_COMPLETED = "COMPLETED"
STEP_FAILED = "FAILED"

WF_CREATED = "CREATED"
WF_PLANNING = "PLANNING"
WF_RUNNING = "RUNNING"
WF_WAITING_APPROVAL = "WAITING_APPROVAL"
WF_VERIFYING = "VERIFYING"
WF_COMPLETED = "COMPLETED"
WF_FAILED = "FAILED"
WF_PAUSED = "PAUSED"
WF_CANCELLED = "CANCELLED"

@dataclass
class WorkflowStep:
    step_id: str
    objective: str
    dependencies: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    status: str = STEP_PENDING
    checkpoint: bool = True
    deadline: Optional[str] = None
    output_result: Optional[Dict[str, Any]] = None

    def mark_completed(self, result: Optional[Dict[str, Any]] = None):
        self.status = STEP_COMPLETED
        self.output_result = result or {}

    def mark_failed(self, error: str = ""):
        self.status = STEP_FAILED
        self.output_result = {"error": error}

@dataclass
class Workflow:
    workflow_id: str
    objective: str
    status: str = WF_CREATED
    priority: str = "NORMAL"
    steps: List[WorkflowStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def update_status(self, new_status: str):
        valid_statuses = [WF_CREATED, WF_PLANNING, WF_RUNNING, WF_WAITING_APPROVAL, WF_VERIFYING, WF_COMPLETED, WF_FAILED, WF_PAUSED, WF_CANCELLED]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid workflow status '{new_status}'.")
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc).isoformat()
