from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class WorldModelScenario:
    scenario_id: str
    description: str
    raw_entity_ref: str
    expected_type: str

WORLD_MODEL_SCENARIOS: List[WorldModelScenario] = [
    WorldModelScenario(
        scenario_id="wm_01_person_resolution",
        description="Resolve Prof. Müller reference to graph entity",
        raw_entity_ref="Prof. Müller",
        expected_type="PERSON"
    )
]
