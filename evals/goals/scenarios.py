from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class GoalScenario:
    scenario_id: str
    description: str
    objective: str
    priority: str

GOAL_SCENARIOS: List[GoalScenario] = [
    GoalScenario(
        scenario_id="goal_01_semester_prep",
        description="Master's semester preparation goal tracking",
        objective="Prepare for Master's semester",
        priority="HIGH"
    )
]
