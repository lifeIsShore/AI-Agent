from typing import Dict, Any, List
from personal_agent.world.personal_simulation_environment import (
    PersonalSimulationEnvironment, SCENARIO_AGGRESSIVE, SCENARIO_BALANCED, SCENARIO_CONSERVATIVE
)

class CounterfactualPlanner:
    def evaluate_counterfactuals(
        self,
        sim_env: PersonalSimulationEnvironment,
        current_workload: Dict[str, Any],
        proposed_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluates simulated scenario outcomes to select optimal execution branches."""
        scenarios: List[Dict[str, Any]] = [
            sim_env.simulate_scenario(current_workload, proposed_action, SCENARIO_AGGRESSIVE),
            sim_env.simulate_scenario(current_workload, proposed_action, SCENARIO_BALANCED),
            sim_env.simulate_scenario(current_workload, proposed_action, SCENARIO_CONSERVATIVE)
        ]

        # Select scenario with best completion probability under low/medium risk
        valid_scenarios = [s for s in scenarios if s.get("risk_level") != "HIGH"]
        if not valid_scenarios:
            valid_scenarios = scenarios

        valid_scenarios.sort(key=lambda s: s.get("predicted_completion_prob", 0.0), reverse=True)
        recommended = valid_scenarios[0]

        return {
            "recommended_scenario": recommended["scenario_mode"],
            "recommended_outcome": recommended,
            "all_scenarios": scenarios
        }
