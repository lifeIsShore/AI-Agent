from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AutonomyMetricsReport:
    autonomy_success_rate: float
    intervention_rate: float
    false_action_rate: float
    goal_completion_rate: float
    recovery_rate: float
    replanning_efficiency: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AutonomyMetricsCalculator:
    def compute_metrics(self, run_data: Dict[str, Any]) -> AutonomyMetricsReport:
        auto_actions = run_data.get("autonomous_actions", 0)
        success_actions = run_data.get("successful_actions", 0)
        total_decisions = run_data.get("total_decisions", 1)
        human_interventions = run_data.get("human_interventions", 0)
        false_actions = run_data.get("false_actions", 0)
        initiated_goals = run_data.get("initiated_goals", 1)
        completed_goals = run_data.get("completed_goals", 0)
        total_failures = run_data.get("total_failures", 0)
        recovered_failures = run_data.get("recovered_failures", 0)
        useful_replans = run_data.get("useful_replans", 0)
        total_replans = run_data.get("total_replans", 1)

        auto_success = round((success_actions / auto_actions) * 100.0, 1) if auto_actions > 0 else 100.0
        intervent_rate = round((human_interventions / total_decisions) * 100.0, 1) if total_decisions > 0 else 0.0
        false_rate = round((false_actions / auto_actions) * 100.0, 1) if auto_actions > 0 else 0.0
        goal_rate = round((completed_goals / initiated_goals) * 100.0, 1) if initiated_goals > 0 else 100.0
        rec_rate = round((recovered_failures / total_failures) * 100.0, 1) if total_failures > 0 else 100.0
        replan_eff = round((useful_replans / total_replans) * 100.0, 1) if total_replans > 0 else 100.0

        return AutonomyMetricsReport(
            autonomy_success_rate=auto_success,
            intervention_rate=intervent_rate,
            false_action_rate=false_rate,
            goal_completion_rate=goal_rate,
            recovery_rate=rec_rate,
            replanning_efficiency=replan_eff
        )
