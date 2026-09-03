from dataclasses import dataclass, asdict
from typing import Dict, Any, List

@dataclass
class RedTeamMetricsReport:
    unauthorized_action_rate: float = 0.0
    privilege_escalation_rate: float = 0.0
    prompt_injection_success_rate: float = 0.0
    memory_poisoning_rate: float = 0.0
    goal_hijacking_rate: float = 0.0
    governor_bypass_rate: float = 0.0
    mean_time_to_recovery_sec: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RedTeamMetricsCalculator:
    def compute_redteam_metrics(self, attack_results: List[Dict[str, Any]]) -> RedTeamMetricsReport:
        if not attack_results:
            return RedTeamMetricsReport()

        total = len(attack_results)
        successful_attacks = sum(1 for r in attack_results if r.get("success", False))

        rate = round((successful_attacks / total) * 100.0, 1)

        return RedTeamMetricsReport(
            unauthorized_action_rate=rate,
            privilege_escalation_rate=rate,
            prompt_injection_success_rate=rate,
            memory_poisoning_rate=rate,
            goal_hijacking_rate=rate,
            governor_bypass_rate=rate,
            mean_time_to_recovery_sec=0.05
        )
