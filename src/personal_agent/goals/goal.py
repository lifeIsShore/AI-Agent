from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

GOAL_ACTIVE = "ACTIVE"
GOAL_BLOCKED = "BLOCKED"
GOAL_STALLED = "STALLED"
GOAL_ACHIEVED = "ACHIEVED"
GOAL_ABANDONED = "ABANDONED"

@dataclass
class Milestone:
    milestone_id: str
    goal_id: str
    objective: str
    status: str = "PENDING"
    deadline: Optional[str] = None
    evidence: List[str] = field(default_factory=list)

@dataclass
class Goal:
    goal_id: str
    objective: str
    priority: str = "NORMAL"
    status: str = GOAL_ACTIVE
    deadline: Optional[str] = None
    progress_pct: float = 0.0
    constraints: List[str] = field(default_factory=list)
    parent_goal_id: Optional[str] = None
    milestones: List[Milestone] = field(default_factory=list)
    provenance: str = "USER_REQUEST"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
