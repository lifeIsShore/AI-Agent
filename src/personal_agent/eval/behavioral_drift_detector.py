from typing import Dict, Any, List
from personal_agent.eval.performance_baseline_manager import PerformanceBaseline

class BehavioralDriftDetector:
    def detect_behavioral_drift(
        self,
        current_metrics: Dict[str, Any],
        baseline: PerformanceBaseline
    ) -> Dict[str, Any]:
        """Measures statistical deviations from established baselines."""
        drift_detected = False
        drift_reasons: List[str] = []

        curr_acc = current_metrics.get("current_accuracy", 1.0)
        curr_acc_accept = current_metrics.get("current_user_acceptance", 1.0)
        curr_tokens = current_metrics.get("avg_tokens_per_task", 0)

        # Accuracy Drift Check (> 5% drop)
        if (baseline.accuracy - curr_acc) > 0.05:
            drift_detected = True
            drift_reasons.append(f"Accuracy drift detected: {curr_acc} vs baseline {baseline.accuracy}")

        # User Acceptance Drift Check (> 10% drop)
        if (baseline.user_acceptance_rate - curr_acc_accept) > 0.10:
            drift_detected = True
            drift_reasons.append(f"User acceptance drift detected: {curr_acc_accept} vs baseline {baseline.user_acceptance_rate}")

        # Token Drift Check (> 50% increase)
        if curr_tokens > (baseline.tokens_per_task * 1.5):
            drift_detected = True
            drift_reasons.append(f"Token consumption drift detected: {curr_tokens} vs baseline {baseline.tokens_per_task}")

        return {
            "drift_detected": drift_detected,
            "specialist_id": baseline.specialist_id,
            "drift_reasons": drift_reasons,
            "baseline": baseline.to_dict(),
            "current": current_metrics
        }
