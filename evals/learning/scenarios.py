from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class LearningScenario:
    scenario_id: str
    description: str
    action: str
    feedback_signal: str
    corrected_params: Optional[Dict[str, Any]]

LEARNING_SCENARIOS: List[LearningScenario] = [
    LearningScenario(
        scenario_id="learn_01_time_correction",
        description="User corrects proposed meeting time from 15:00 to 16:00",
        action="create_calendar_event",
        feedback_signal="CORRECT",
        corrected_params={"start_time": "16:00"}
    ),
    LearningScenario(
        scenario_id="learn_02_archive_approval",
        description="User approves automated newsletter archive proposal",
        action="archive_email",
        feedback_signal="APPROVE",
        corrected_params=None
    )
]
