from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from personal_agent.workflow.models import WorkflowStep

VERIFIED_STATUS_VERIFIED = "VERIFIED"
VERIFIED_STATUS_INCONSISTENT = "INCONSISTENT"
VERIFIED_STATUS_FAILED = "FAILED"

@dataclass
class StepVerificationResult:
    status: str                        # VERIFIED | INCONSISTENT | FAILED
    verified: bool
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)

class StepVerifier:
    def verify_step_execution(
        self,
        step: WorkflowStep,
        execution_output: Dict[str, Any],
        expected_state: Optional[Dict[str, Any]] = None
    ) -> StepVerificationResult:
        """Validates tool execution output against expected post-state conditions."""
        if not execution_output or execution_output.get("error"):
            return StepVerificationResult(
                status=VERIFIED_STATUS_FAILED,
                verified=False,
                reason=f"Execution error encountered: {execution_output.get('error', 'Unknown execution error')}"
            )

        if expected_state:
            for k, expected_v in expected_state.items():
                actual_v = execution_output.get(k)
                if actual_v != expected_v:
                    return StepVerificationResult(
                        status=VERIFIED_STATUS_INCONSISTENT,
                        verified=False,
                        reason=f"State mismatch for '{k}': expected '{expected_v}', found '{actual_v}'",
                        details={"expected": expected_state, "actual": execution_output}
                    )

        return StepVerificationResult(
            status=VERIFIED_STATUS_VERIFIED,
            verified=True,
            reason=f"Step '{step.step_id}' post-execution state verified successfully.",
            details=execution_output
        )
