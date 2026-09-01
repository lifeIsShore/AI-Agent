from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
OUTCOME_FAILED = "FAILED"
OUTCOME_USER_REJECTED = "USER_REJECTED"
OUTCOME_USER_CORRECTED = "USER_CORRECTED"

@dataclass
class ExecutionOutcomeRecord:
    target_id: str
    action: str
    outcome_status: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)

class OutcomeLearningEngine:
    def __init__(self):
        self.records: List[ExecutionOutcomeRecord] = []

    def record_outcome(
        self,
        target_id: str,
        action: str,
        outcome_status: str,
        details: Dict[str, Any] = None
    ) -> ExecutionOutcomeRecord:
        """Records workflow or proposal execution outcome."""
        rec = ExecutionOutcomeRecord(
            target_id=target_id,
            action=action,
            outcome_status=outcome_status,
            details=details or {}
        )
        self.records.append(rec)
        return rec

    def get_success_rate(self, action: str) -> float:
        """Calculates success rate percentage for a given action type."""
        action_recs = [r for r in self.records if r.action == action]
        if not action_recs:
            return 100.0

        successes = [r for r in action_recs if r.outcome_status in [OUTCOME_SUCCESS, OUTCOME_PARTIAL_SUCCESS]]
        return round((len(successes) / len(action_recs)) * 100.0, 1)
