from typing import Dict, Any, List

SCENARIO_AGGRESSIVE = "AGGRESSIVE"
SCENARIO_BALANCED = "BALANCED"
SCENARIO_CONSERVATIVE = "CONSERVATIVE"

class PersonalSimulationEnvironment:
    def simulate_scenario(
        self,
        current_workload: Dict[str, Any],
        proposed_action: Dict[str, Any],
        scenario_mode: str = SCENARIO_BALANCED
    ) -> Dict[str, Any]:
        """Simulates counterfactual scenario branches in an isolated in-memory sandbox."""
        added_hours = proposed_action.get("estimated_hours", 2.0)
        curr_hours = current_workload.get("total_hours", 20.0)

        simulated_total = curr_hours + added_hours
        max_capacity = current_workload.get("max_capacity", 40.0)

        workload_ratio = simulated_total / max_capacity

        if scenario_mode == SCENARIO_AGGRESSIVE:
            completion_prob = max(0.40, 1.0 - (workload_ratio * 0.4))
            risk_level = "HIGH" if workload_ratio > 0.85 else "MEDIUM"
        elif scenario_mode == SCENARIO_CONSERVATIVE:
            completion_prob = max(0.70, 1.0 - (workload_ratio * 0.15))
            risk_level = "LOW"
        else:  # BALANCED
            completion_prob = max(0.55, 1.0 - (workload_ratio * 0.25))
            risk_level = "MEDIUM" if workload_ratio > 0.80 else "LOW"

        return {
            "scenario_mode": scenario_mode,
            "simulated_workload_hours": round(simulated_total, 1),
            "capacity_utilization": round(workload_ratio, 2),
            "predicted_completion_prob": round(completion_prob, 2),
            "risk_level": risk_level,
            "mutates_live_state": False
        }
