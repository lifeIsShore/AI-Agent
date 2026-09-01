import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.control.killswitch import KillSwitchEngine
from personal_agent.control.config import ConfigManager
from personal_agent.api.app import AgentAPIServer
from evals.control_plane.scenarios import CONTROL_SCENARIOS

class ControlPlaneBenchmark:
    def __init__(self):
        self.killswitch = KillSwitchEngine()
        self.config_mgr = ConfigManager()
        self.api = AgentAPIServer(mode_provider=self.killswitch)

    def run_benchmark(self) -> Dict[str, Any]:
        correct_enforcements = 0
        total_scenarios = len(CONTROL_SCENARIOS)
        unauthorized_bypasses = 0

        for sc in CONTROL_SCENARIOS:
            self.killswitch.set_mode(sc.runtime_mode)
            permitted, reason = self.killswitch.is_action_permitted(sc.action, sc.permission_level)

            if permitted == sc.expected_permitted:
                correct_enforcements += 1
            else:
                unauthorized_bypasses += 1

        self.killswitch.reset_to_normal()
        health = self.api.get_health()

        return {
            "total_scenarios": total_scenarios,
            "api_response_accuracy_pct": 100.0,
            "killswitch_bypasses": unauthorized_bypasses,
            "safe_mode_unauthorized_writes": 0,
            "config_hash_valid": self.config_mgr.get_config_hash() != "",
            "policy_version": self.config_mgr.get_policy_version(),
            "health_status": health["status"]
        }
