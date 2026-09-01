from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any

@dataclass
class AutonomyCycleRecord:
    cycle_id: str
    goal_id: str
    autonomy_level: str
    status: str
    action_taken: str
    governor_decision: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
