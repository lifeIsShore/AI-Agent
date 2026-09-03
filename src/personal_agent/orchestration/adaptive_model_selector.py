from typing import Dict, Any

class AdaptiveModelSelector:
    def select_adaptive_model(
        self,
        task_characteristics: Dict[str, Any],
        historical_outcomes: Dict[str, Any],
        user_preferences: Dict[str, Any],
        resource_budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dynamically selects model tier based on task, outcomes, preferences, and resources."""
        complexity = task_characteristics.get("complexity", "low").lower()
        domain = task_characteristics.get("domain", "general").lower()

        pref_mode = user_preferences.get("model_preference", "BALANCED").upper()
        cpu_pct = resource_budget.get("cpu_percent", 0)
        gpu_mem = resource_budget.get("gpu_mem_mb", None)
        res_constrained = cpu_pct > 85 or (gpu_mem is not None and gpu_mem < 1000)

        if complexity == "low" or domain == "simple_regex":
            selected_tier = "DETERMINISTIC"
            reason = "Task is simple or pattern-based; deterministic rule engine chosen for 0 latency."
        elif res_constrained or pref_mode == "LOCAL_ONLY":
            selected_tier = "SMALL_LOCAL_LLM"
            reason = "Resource constraints or strict local privacy preference active; routing to small local model."
        elif complexity == "medium":
            selected_tier = "STRONG_LOCAL_LLM"
            reason = "Medium complexity task; routing to strong local model for balanced accuracy and speed."
        else:
            selected_tier = "STRONG_CLOUD_LLM"
            reason = "High complexity multi-domain task requiring advanced reasoning."

        return {
            "selected_tier": selected_tier,
            "reason": reason,
            "governor_decoupled": True,
            "task": task_characteristics,
            "resource_budget": resource_budget
        }
