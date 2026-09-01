from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ControlScenario:
    scenario_id: str
    description: str
    runtime_mode: str
    action: str
    permission_level: str
    expected_permitted: bool

CONTROL_SCENARIOS: List[ControlScenario] = [
    ControlScenario(
        scenario_id="ctrl_01_normal_read",
        description="Normal mode static reading action",
        runtime_mode="NORMAL",
        action="get_today_events",
        permission_level="READ_ONLY",
        expected_permitted=True
    ),
    ControlScenario(
        scenario_id="ctrl_02_read_only_blocked_write",
        description="Read-Only safe mode blocking modification action",
        runtime_mode="READ_ONLY",
        action="create_calendar_event",
        permission_level="MODIFY",
        expected_permitted=False
    ),
    ControlScenario(
        scenario_id="ctrl_03_emergency_stop_block_all",
        description="Emergency stop mode blocking all action proposals out-of-band",
        runtime_mode="EMERGENCY_STOP",
        action="get_today_events",
        permission_level="READ_ONLY",
        expected_permitted=False
    )
]
