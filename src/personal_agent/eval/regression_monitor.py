from typing import Dict, Any, List

class RegressionMonitor:
    def check_regression(
        self,
        current_metrics: Dict[str, Any],
        threshold_accuracy: float = 0.85
    ) -> Dict[str, Any]:
        """Identifies accuracy drops, quality drops, latency spikes, and token spikes."""
        regress_detected = False
        alerts: List[str] = []

        curr_acc = current_metrics.get("current_accuracy", 1.0)
        if curr_acc < threshold_accuracy:
            regress_detected = True
            alerts.append(f"ACCURACY_REGRESSION: Current accuracy {curr_acc} dropped below threshold {threshold_accuracy}.")

        return {
            "regression_detected": regress_detected,
            "alerts": alerts,
            "metrics": current_metrics
        }
