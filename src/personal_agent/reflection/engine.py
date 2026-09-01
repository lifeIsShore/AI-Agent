import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any

@dataclass
class ReflectionRecord:
    reflection_id: str
    workflow_id: str
    expected_outcome: str
    actual_outcome: str
    deviation_reason: str
    recommendation: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SelfReflectionEngine:
    def evaluate_workflow_reflection(
        self,
        workflow_id: str,
        expected_outcome: str,
        actual_outcome: str
    ) -> ReflectionRecord:
        """Evaluates finished workflow deviations and generates strategy improvement recommendations."""
        r_id = f"refl_{uuid.uuid4().hex[:6]}"

        if expected_outcome == actual_outcome:
            return ReflectionRecord(
                reflection_id=r_id,
                workflow_id=workflow_id,
                expected_outcome=expected_outcome,
                actual_outcome=actual_outcome,
                deviation_reason="No deviation observed",
                recommendation="Maintain existing execution strategy"
            )

        return ReflectionRecord(
            reflection_id=r_id,
            workflow_id=workflow_id,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            deviation_reason=f"Actual outcome '{actual_outcome}' diverged from expected '{expected_outcome}'",
            recommendation="Adjust conflict resolution weights and pre-execution resource buffer"
        )
