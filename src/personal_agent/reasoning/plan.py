import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any

@dataclass
class DecisionPlan:
    objective: str
    subtasks: List[str] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)
    candidate_actions: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    plan_id: str = field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "subtasks": self.subtasks,
            "required_context": self.required_context,
            "candidate_actions": self.candidate_actions,
            "confidence": self.confidence,
            "created_at": self.created_at
        }
