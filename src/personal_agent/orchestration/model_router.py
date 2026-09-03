from typing import Dict, Any

TIER_DETERMINISTIC_RULES = "DETERMINISTIC_RULES"
TIER_SMALL_LOCAL_LLM = "SMALL_LOCAL_LLM"
TIER_STRONG_LOCAL_LLM = "STRONG_LOCAL_LLM"
TIER_STRONG_CLOUD_MODEL = "STRONG_CLOUD_MODEL"

class ModelRouter:
    def select_model_tier(self, task_complexity: str) -> Dict[str, Any]:
        """Dynamically routes tasks to appropriate model execution tiers based on task complexity."""
        comp_clean = task_complexity.lower()

        if "simple" in comp_clean or "metadata" in comp_clean:
            tier = TIER_DETERMINISTIC_RULES
            cost_factor = 0.0
        elif "moderate" in comp_clean or "classification" in comp_clean:
            tier = TIER_SMALL_LOCAL_LLM
            cost_factor = 0.1
        elif "hard" in comp_clean or "planning" in comp_clean or "json" in comp_clean:
            tier = TIER_STRONG_LOCAL_LLM
            cost_factor = 0.4
        elif "complex" in comp_clean or "research" in comp_clean:
            tier = TIER_STRONG_CLOUD_MODEL
            cost_factor = 1.0
        else:
            tier = TIER_SMALL_LOCAL_LLM
            cost_factor = 0.1

        return {
            "selected_tier": tier,
            "task_complexity": task_complexity,
            "relative_cost_factor": cost_factor,
            "governor_independent": True
        }
