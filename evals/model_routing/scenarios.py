from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RoutingScenario:
    scenario_id: str
    description: str
    intent: str
    context_bytes: int
    risk_level: str
    initial_confidence: Optional[float]
    expected_tier: str

ROUTING_SCENARIOS: List[RoutingScenario] = [
    RoutingScenario(
        scenario_id="sc_01_time",
        description="Static time query resolved by system rules",
        intent="GET_TIME",
        context_bytes=100,
        risk_level="LOW",
        initial_confidence=1.0,
        expected_tier="rules"
    ),
    RoutingScenario(
        scenario_id="sc_02_triage",
        description="Simple email inbox triage classification",
        intent="REVIEW_INBOX",
        context_bytes=800,
        risk_level="LOW",
        initial_confidence=0.95,
        expected_tier="local-small"
    ),
    RoutingScenario(
        scenario_id="sc_03_planning",
        description="Daily schedule optimization with calendar slots",
        intent="PLAN_DAY",
        context_bytes=3500,
        risk_level="MEDIUM",
        initial_confidence=0.88,
        expected_tier="local-medium"
    ),
    RoutingScenario(
        scenario_id="sc_04_low_confidence_escalation",
        description="Low confidence classification triggering escalation",
        intent="REVIEW_INBOX",
        context_bytes=1200,
        risk_level="HIGH",
        initial_confidence=0.55,
        expected_tier="remote-large"
    ),
    RoutingScenario(
        scenario_id="sc_05_complex_financial",
        description="Complex financial reasoning with multi-factor constraint optimization",
        intent="COMPLEX_REASONING",
        context_bytes=6000,
        risk_level="HIGH",
        initial_confidence=0.80,
        expected_tier="remote-large"
    )
]
