from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MultiAgentScenario:
    scenario_id: str
    description: str
    goal: str
    expected_agents: List[str]

MULTI_AGENT_SCENARIOS: List[MultiAgentScenario] = [
    MultiAgentScenario(
        scenario_id="ma_01_daily_master_plan",
        description="Supervisor delegates master daily planning to Inbox, Calendar, and Task agents",
        goal="Plan my day",
        expected_agents=["InboxAgent", "CalendarAgent", "TaskAgent"]
    )
]
