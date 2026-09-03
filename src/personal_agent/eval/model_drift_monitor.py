from typing import Dict, Any

class ModelDriftMonitor:
    def monitor_model_drift(self, tier_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitors model tier performance changes across routing policy shifts."""
        model_name = tier_metrics.get("model_name", "local_model")
        accuracy = tier_metrics.get("accuracy", 0.95)

        drift_detected = accuracy < 0.90
        return {
            "model_name": model_name,
            "drift_detected": drift_detected,
            "accuracy": accuracy,
            "recommendation": "REVERT_MODEL_TIER" if drift_detected else "MAINTAIN_MODEL_TIER"
        }
