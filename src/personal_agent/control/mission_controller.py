import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from personal_agent.control.autonomy_profile import AutonomyProfile
from personal_agent.autonomy.autonomy_policy import LEVEL_3_BOUNDED_AUTO

@dataclass
class MissionRecord:
    mission_id: str
    name: str
    status: str = "IN_PROGRESS"
    goals: List[str] = field(default_factory=list)
    autonomy_profile: AutonomyProfile = field(default_factory=lambda: AutonomyProfile("prof_default", "m_default"))
    progress_pct: float = 0.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MissionController:
    def __init__(self):
        self.missions: Dict[str, MissionRecord] = {}

    def create_mission(
        self,
        name: str,
        goals: Optional[List[str]] = None,
        max_autonomy_level: str = LEVEL_3_BOUNDED_AUTO
    ) -> MissionRecord:
        m_id = f"mission_{uuid.uuid4().hex[:8]}"
        profile = AutonomyProfile(
            profile_id=f"prof_{m_id}",
            mission_id=m_id,
            max_autonomy_level=max_autonomy_level
        )
        mission = MissionRecord(
            mission_id=m_id,
            name=name,
            goals=goals or [],
            autonomy_profile=profile,
            created_at=time.time()
        )
        self.missions[m_id] = mission
        return mission

    def update_mission_progress(
        self,
        mission_id: str,
        progress_pct: float,
        status: str = "IN_PROGRESS"
    ) -> Optional[MissionRecord]:
        m = self.missions.get(mission_id)
        if not m:
            return None
        m.progress_pct = max(0.0, min(100.0, progress_pct))
        m.status = status
        return m

    def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        return self.missions.get(mission_id)
