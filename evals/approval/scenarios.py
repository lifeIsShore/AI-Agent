from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class HITLScenario:
    scenario_id: str
    description: str
    action: str
    target: str
    risk_level: str
    expected_mode: str

HITL_SCENARIOS: List[HITLScenario] = [
    HITLScenario(
        scenario_id="hitl_01_low_risk",
        description="Low risk static reading action",
        action="get_today_events",
        target="primary_calendar",
        risk_level="LOW",
        expected_mode="AUTOMATIC"
    ),
    HITLScenario(
        scenario_id="hitl_02_medium_risk",
        description="Medium risk calendar creation requiring quick review",
        action="create_calendar_event",
        target="primary_calendar",
        risk_level="MEDIUM",
        expected_mode="QUICK_REVIEW"
    ),
    HITLScenario(
        scenario_id="hitl_03_high_risk_external",
        description="High risk external email sending requiring detailed review",
        action="send_email",
        target="recipient@domain.com",
        risk_level="HIGH",
        expected_mode="DETAILED_REVIEW"
    ),
    HITLScenario(
        scenario_id="hitl_04_critical",
        description="Critical risk action prohibited by policy",
        action="admin_override_policy",
        target="system_core",
        risk_level="CRITICAL",
        expected_mode="CRITICAL_DENIAL"
    )
]
