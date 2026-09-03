from typing import Tuple, Dict, Any

DIAGNOSIS_RETRY = "RETRY"
DIAGNOSIS_ALTERNATIVE = "ALTERNATIVE_STRATEGY"
DIAGNOSIS_REPLAN = "REPLAN"
DIAGNOSIS_ABORT = "ABORT"

class FailureDiagnoser:
    def __init__(self, max_retries_per_step: int = 3):
        self.max_retries_per_step = max_retries_per_step

    def diagnose_failure(
        self,
        node_id: str,
        error_message: str,
        current_retry_count: int
    ) -> Tuple[str, str]:
        """Diagnoses workflow step failures and selects recovery strategy."""
        err_clean = error_message.lower()

        # 1. Permanent / Security / Auth Error -> Replan or Abort
        if "permission" in err_clean or "forbidden" in err_clean or "hard block" in err_clean:
            return DIAGNOSIS_REPLAN, f"Permanent security/permission failure on node '{node_id}': {error_message}. Triggering replan."

        # 2. Network / Transient Timeout -> Retry if count < max
        if current_retry_count < self.max_retries_per_step:
            if "timeout" in err_clean or "transient" in err_clean or "503" in err_clean or "connection" in err_clean:
                return DIAGNOSIS_RETRY, f"Transient failure detected. Retry {current_retry_count + 1}/{self.max_retries_per_step} permitted."

        # 3. Exceeded retries -> Alternative Strategy
        if current_retry_count >= self.max_retries_per_step:
            return DIAGNOSIS_ALTERNATIVE, f"Max retries ({self.max_retries_per_step}) exceeded for node '{node_id}'. Switching to alternative strategy."

        # 4. Fallback Alternative Strategy
        return DIAGNOSIS_ALTERNATIVE, f"Step '{node_id}' failed with '{error_message}'. Proposing alternative fallback strategy."
