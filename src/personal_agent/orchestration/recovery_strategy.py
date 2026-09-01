from typing import Tuple, Dict, Any
from personal_agent.workflow.models import WorkflowStep

FAIL_TRANSIENT = "TRANSIENT"
FAIL_RATE_LIMITED = "RATE_LIMITED"
FAIL_SERVICE_OUTAGE = "SERVICE_OUTAGE"
FAIL_PERMISSION_DENIED = "PERMISSION_DENIED"
FAIL_INVALID_OUTPUT = "INVALID_OUTPUT"
FAIL_CRITICAL = "CRITICAL"

class FailureClassifier:
    def classify_failure(self, error_msg: str) -> str:
        """Classifies execution errors to determine workflow-aware recovery policy."""
        err_lower = error_msg.lower()

        if "429" in err_lower or "rate limit" in err_lower:
            return FAIL_RATE_LIMITED
        elif "permission" in err_lower or "unauthorized" in err_lower or "403" in err_lower or "denied" in err_lower:
            return FAIL_PERMISSION_DENIED
        elif "503" in err_lower or "outage" in err_lower or "unavailable" in err_lower:
            return FAIL_SERVICE_OUTAGE
        elif "timeout" in err_lower or "connection" in err_lower or "reset" in err_lower:
            return FAIL_TRANSIENT
        elif "mismatch" in err_lower or "invalid format" in err_lower:
            return FAIL_INVALID_OUTPUT
        return FAIL_CRITICAL

class WorkflowRecoveryEngine:
    def __init__(self):
        self.classifier = FailureClassifier()

    def handle_step_failure(self, step: WorkflowStep, error_msg: str) -> Tuple[str, str, bool]:
        """Determines recovery action based on error classification."""
        fail_class = self.classifier.classify_failure(error_msg)

        if fail_class in [FAIL_TRANSIENT, FAIL_RATE_LIMITED]:
            return fail_class, "RETRY_WITH_BACKOFF", True
        elif fail_class == FAIL_SERVICE_OUTAGE:
            return fail_class, "CIRCUIT_BREAKER_FALLBACK", False
        elif fail_class == FAIL_PERMISSION_DENIED:
            return fail_class, "STOP_NO_RETRY", False
        elif fail_class == FAIL_INVALID_OUTPUT:
            return fail_class, "REPLAN_STEP", True

        return fail_class, "SAFE_STOP", False
