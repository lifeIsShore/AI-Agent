import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

MS_NOT_STARTED = "NOT_STARTED"
MS_IN_PROGRESS = "IN_PROGRESS"
MS_BLOCKED = "BLOCKED"
MS_COMPLETED = "COMPLETED"
MS_FAILED = "FAILED"
MS_ABANDONED = "ABANDONED"

@dataclass
class MilestoneRecord:
    milestone_id: str
    goal_id: str
    objective: str
    status: str = MS_NOT_STARTED
    progress_pct: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MilestoneRecord":
        return cls(
            milestone_id=data.get("milestone_id", f"ms_{uuid.uuid4().hex[:8]}"),
            goal_id=data.get("goal_id", "g_default"),
            objective=data.get("objective", "Objective"),
            status=data.get("status", MS_NOT_STARTED),
            progress_pct=data.get("progress_pct", 0.0),
            dependencies=data.get("dependencies", []),
            evidence=data.get("evidence", [])
        )

class MilestoneManager:
    def __init__(self):
        self.milestones: Dict[str, MilestoneRecord] = {}

    def create_milestone(
        self,
        goal_id: str,
        objective: str,
        dependencies: Optional[List[str]] = None
    ) -> MilestoneRecord:
        ms_id = f"ms_{uuid.uuid4().hex[:8]}"
        ms = MilestoneRecord(
            milestone_id=ms_id,
            goal_id=goal_id,
            objective=objective,
            dependencies=dependencies or []
        )
        self.milestones[ms_id] = ms
        return ms

    def update_progress(
        self,
        milestone_id: str,
        status: str,
        progress_pct: float,
        evidence: Optional[str] = None
    ) -> Optional[MilestoneRecord]:
        ms = self.milestones.get(milestone_id)
        if not ms:
            return None

        ms.status = status
        ms.progress_pct = max(0.0, min(100.0, progress_pct))
        if evidence:
            ms.evidence.append(evidence)
        return ms

    def get_goal_milestones(self, goal_id: str) -> List[MilestoneRecord]:
        return [m for m in self.milestones.values() if m.goal_id == goal_id]

    def compute_overall_progress(self, goal_id: str) -> float:
        milestones = self.get_goal_milestones(goal_id)
        if not milestones:
            return 0.0
        total = sum(m.progress_pct for m in milestones)
        return round(total / len(milestones), 1)
