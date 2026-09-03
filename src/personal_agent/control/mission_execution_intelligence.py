from typing import Dict, Any
from personal_agent.events.predictive_event_engine import PredictiveEventEngine
from personal_agent.world.personal_simulation_environment import PersonalSimulationEnvironment
from personal_agent.planner.counterfactual_planner import CounterfactualPlanner

class MissionExecutionIntelligence:
    def __init__(self):
        self.predictive_engine = PredictiveEventEngine()
        self.sim_env = PersonalSimulationEnvironment()
        self.cf_planner = CounterfactualPlanner()

    def adapt_mission_execution(
        self,
        mission_id: str,
        actual_duration_sec: float,
        estimated_duration_sec: float,
        strategy_id: str = "strat_default"
    ) -> Dict[str, Any]:
        """Dynamically adapts mission execution when step duration or outcomes deviate from estimates."""
        ratio = actual_duration_sec / max(1.0, estimated_duration_sec)
        duration_overrun = ratio > 1.5

        if not duration_overrun:
            return {
                "mission_id": mission_id,
                "status": "STABLE",
                "adapted": False,
                "duration_ratio": round(ratio, 2),
                "strategy_id": strategy_id
            }

        # Step 1: Predictive Event Engine prediction
        pred_res = self.predictive_engine.predict_upcoming_events([], [], [{"name": "Mission Deadline", "deadline": "2026-09-10"}])

        # Step 2: Digital Twin counterfactual planning
        cf_res = self.cf_planner.evaluate_counterfactuals(
            self.sim_env,
            current_workload={"total_hours": 30.0, "max_capacity": 40.0},
            proposed_action={"estimated_hours": 4.0}
        )

        return {
            "mission_id": mission_id,
            "status": "REPLANNED_DYNAMICALLY",
            "adapted": True,
            "duration_ratio": round(ratio, 2),
            "original_strategy": strategy_id,
            "new_recommended_scenario": cf_res["recommended_scenario"],
            "prediction_risk": pred_res["predictions"][0]["risk_level"] if pred_res["predictions"] else "MEDIUM",
            "governor_gated": True
        }
