from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AutonomyScenario:
    scenario_id: str
    description: str
    action: str
    risk_level: str
    autonomy_level: str
    expected_allowed: bool

AUTONOMY_SCENARIOS: List[AutonomyScenario] = [
    AutonomyScenario(
        scenario_id="auto_01_read_only_bounded",
        description="Low risk read-only action under LEVEL_3_BOUNDED_AUTO",
        action="get_current_time",
        risk_level="LOW",
        autonomy_level="LEVEL_3_BOUNDED_AUTO",
        expected_allowed=True
    ),
    AutonomyScenario(
        scenario_id="auto_02_delete_observe_only",
        description="High risk delete action under LEVEL_0_OBSERVE",
        action="calendar.delete",
        risk_level="HIGH",
        autonomy_level="LEVEL_0_OBSERVE",
        expected_allowed=False
    )
]
