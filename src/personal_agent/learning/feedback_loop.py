from typing import Tuple, Dict, Any, Optional
from personal_agent.learning.outcome_engine import OutcomeLearningEngine, OUTCOME_SUCCESS, OUTCOME_USER_REJECTED, OUTCOME_USER_CORRECTED
from personal_agent.learning.strategy_store import ExecutionStrategyStore

FEEDBACK_APPROVE = "APPROVE"
FEEDBACK_REJECT = "REJECT"
FEEDBACK_EDIT = "EDIT"
FEEDBACK_CORRECT = "CORRECT"

class FeedbackLoop:
    def __init__(self, outcome_engine: OutcomeLearningEngine, strategy_store: ExecutionStrategyStore):
        self.outcome_engine = outcome_engine
        self.strategy_store = strategy_store

    def process_feedback(
        self,
        proposal_id: str,
        action: str,
        feedback_type: str,
        corrected_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Processes user feedback and adapts future candidate proposal parameters."""
        if feedback_type == FEEDBACK_APPROVE:
            self.outcome_engine.record_outcome(proposal_id, action, OUTCOME_SUCCESS)
            self.strategy_store.update_strategy_outcome(action, success=True, used_parameters=corrected_params)
            return True, f"Feedback 'APPROVE' recorded for '{proposal_id}'."

        elif feedback_type in [FEEDBACK_CORRECT, FEEDBACK_EDIT]:
            self.outcome_engine.record_outcome(proposal_id, action, OUTCOME_USER_CORRECTED, details=corrected_params)
            self.strategy_store.update_strategy_outcome(action, success=True, used_parameters=corrected_params)
            return True, f"Feedback '{feedback_type}' recorded. Candidate parameters updated: {corrected_params}."

        elif feedback_type == FEEDBACK_REJECT:
            self.outcome_engine.record_outcome(proposal_id, action, OUTCOME_USER_REJECTED)
            self.strategy_store.update_strategy_outcome(action, success=False)
            return True, f"Feedback 'REJECT' recorded for '{proposal_id}'."

        return False, f"Unknown feedback type '{feedback_type}'."
