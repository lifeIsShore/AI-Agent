import os
import json
import time
import uuid
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
OUTCOME_FAILED = "FAILED"
OUTCOME_USER_MODIFIED = "USER_MODIFIED"
OUTCOME_USER_REJECTED = "USER_REJECTED"
OUTCOME_USER_CORRECTED = "USER_CORRECTED"
OUTCOME_USER_ACCEPTED = "USER_ACCEPTED"
OUTCOME_IGNORED = "IGNORED"

@dataclass
class ActionOutcome:
    action_id: str
    action_type: str
    outcome_type: str
    goal_id: Optional[str] = None
    expected_result: str = "success"
    actual_result: str = "success"
    user_override: bool = False
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionOutcome":
        return cls(
            action_id=data.get("action_id", f"act_{uuid.uuid4().hex[:8]}"),
            action_type=data.get("action_type", "unknown"),
            outcome_type=data.get("outcome_type", OUTCOME_SUCCESS),
            goal_id=data.get("goal_id"),
            expected_result=data.get("expected_result", "success"),
            actual_result=data.get("actual_result", "success"),
            user_override=data.get("user_override", False),
            confidence=data.get("confidence", 1.0),
            timestamp=data.get("timestamp", time.time()),
            details=data.get("details", {})
        )

# Backward compatibility alias
ExecutionOutcomeRecord = ActionOutcome

class OutcomeEngine:
    def __init__(self, storage_dir: Optional[str] = None, filename: str = "outcomes.json"):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
            self.filepath = os.path.join(self.storage_dir, filename)
            os.makedirs(self.storage_dir, exist_ok=True)
            self.records: List[ActionOutcome] = self.load_outcomes()
        else:
            self.storage_dir = None
            self.filepath = None
            self.records: List[ActionOutcome] = []

    def record_outcome(
        self,
        action_id: str,
        action_type: str,
        outcome_type: str,
        goal_id: Optional[str] = None,
        expected_result: str = "success",
        actual_result: str = "success",
        user_override: bool = False,
        confidence: float = 1.0,
        details: Optional[Dict[str, Any]] = None
    ) -> ActionOutcome:
        outcome = ActionOutcome(
            action_id=action_id,
            action_type=action_type,
            outcome_type=outcome_type,
            goal_id=goal_id,
            expected_result=expected_result,
            actual_result=actual_result,
            user_override=user_override,
            confidence=confidence,
            timestamp=time.time(),
            details=details or {}
        )
        self.records.append(outcome)
        if self.filepath:
            self.save_outcomes()
        return outcome

    def save_outcomes(self) -> None:
        """Atomically saves outcomes to JSON file."""
        if not self.filepath or not self.storage_dir:
            return
        data = [r.to_dict() for r in self.records]
        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="outcomes_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[OutcomeEngine ERROR] Failed to save outcomes: {e}")

    def load_outcomes(self) -> List[ActionOutcome]:
        if not self.filepath or not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [ActionOutcome.from_dict(d) for d in data]
        except Exception as e:
            print(f"[OutcomeEngine WARNING] Failed to load outcomes from '{self.filepath}': {e}. Starting fresh.")
            return []

    def get_outcomes_by_action_type(self, action_type: str) -> List[ActionOutcome]:
        return [r for r in self.records if r.action_type == action_type]

    def get_success_rate(self, action_type: str) -> float:
        recs = self.get_outcomes_by_action_type(action_type)
        if not recs:
            return 100.0
        successes = [r for r in recs if r.outcome_type in (OUTCOME_SUCCESS, OUTCOME_USER_ACCEPTED, OUTCOME_PARTIAL_SUCCESS, OUTCOME_USER_CORRECTED)]
        return round((len(successes) / len(recs)) * 100.0, 1)

# Backward compatibility alias
OutcomeLearningEngine = OutcomeEngine
