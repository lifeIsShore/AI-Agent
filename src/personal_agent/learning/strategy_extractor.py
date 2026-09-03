import uuid
from typing import Dict, Any, List

class StrategyExtractor:
    def extract_strategy(
        self,
        mission_data: Dict[str, Any],
        outcome_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extracts reusable strategy templates from completed mission execution graphs."""
        steps = mission_data.get("steps", [])
        step_names = [s.get("step_name", "step") for s in steps]

        strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
        domain = mission_data.get("domain", "general")
        success_rate = outcome_analysis.get("success_rate", 1.0)

        return {
            "strategy_id": strategy_id,
            "domain": domain,
            "name": f"Strategy for {domain} (extracted)",
            "step_sequence": step_names,
            "success_rate": success_rate,
            "sample_missions": [mission_data.get("mission_id", "m1")],
            "confidence": round(min(1.0, 0.7 + (success_rate * 0.3)), 2)
        }
