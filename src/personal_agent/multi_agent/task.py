import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any

TASK_PENDING = "PENDING"
TASK_RUNNING = "RUNNING"
TASK_COMPLETED = "COMPLETED"
TASK_FAILED = "FAILED"

@dataclass
class AgentTask:
    task_id: str
    workflow_id: str
    parent_agent: str
    assigned_agent: str
    objective: str
    required_capabilities: List[str] = field(default_factory=list)
    budget_tokens: int = 2000
    status: str = TASK_PENDING
    result: Dict[str, Any] = field(default_factory=dict)
