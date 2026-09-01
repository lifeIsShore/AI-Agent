from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class IntelligenceScenario:
    scenario_id: str
    description: str
    request: str
    context_count: int
    expected_subtask_count: int

INTELLIGENCE_SCENARIOS: List[IntelligenceScenario] = [
    IntelligenceScenario(
        scenario_id="intel_01_daily_planning",
        description="Structured plan decomposition for daily assistant schedule",
        request="Plan my day",
        context_count=5,
        expected_subtask_count=4
    ),
    IntelligenceScenario(
        scenario_id="intel_02_inbox_triage",
        description="Structured plan decomposition for inbox triage",
        request="Triage my inbox emails",
        context_count=8,
        expected_subtask_count=4
    )
]
