from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ProactiveScenario:
    scenario_id: str
    description: str
    event_type: str
    payload: Dict[str, Any]
    expected_priority: str
    expected_trigger: bool

PROACTIVE_SCENARIOS: List[ProactiveScenario] = [
    ProactiveScenario(
        scenario_id="pro_01_urgent_deadline",
        description="Urgent thesis submission deadline event triggering P5 workflow",
        event_type="EMAIL_RECEIVED",
        payload={"subject": "Urgent thesis submission deadline", "sender": "advisor@univ.edu"},
        expected_priority="P5",
        expected_trigger=True
    ),
    ProactiveScenario(
        scenario_id="pro_02_newsletter_digest",
        description="Marketing newsletter digest generating P0 ignore rating",
        event_type="EMAIL_RECEIVED",
        payload={"subject": "Weekly job alerts digest", "sender": "news@alerts.com"},
        expected_priority="P0",
        expected_trigger=False
    )
]
