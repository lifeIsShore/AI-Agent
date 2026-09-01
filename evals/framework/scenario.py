from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class EvalScenario:
    scenario_id: str
    name: str
    category: str
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    mock_failures: Dict[str, Any] = field(default_factory=dict)
    expected_actions: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)
