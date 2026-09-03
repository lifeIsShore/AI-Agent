from typing import Tuple, Dict, Any

class SafetyRegressionMonitor:
    def evaluate_safety_regression(
        self,
        baseline_violations: int,
        candidate_violations: int
    ) -> Tuple[bool, str]:
        """Enforces zero tolerance for safety violations or false action increases."""

        if candidate_violations > baseline_violations:
            return False, f"SafetyRegressionMonitor HARD REJECT: Candidate introduced safety regression ({candidate_violations} vs baseline {baseline_violations}). Safety cannot be traded for performance."

        return True, "SafetyRegressionMonitor PASSED: No safety regression detected."
