from typing import Dict, Any, Optional
from personal_agent.learning.learning_engine import LearningEngine

USER_APPROVED = "USER_APPROVED"
USER_REJECTED = "USER_REJECTED"
USER_MODIFIED = "USER_MODIFIED"

class HumanFeedbackLoop:
    def __init__(self, learning_engine: Optional[LearningEngine] = None):
        self.learning_engine = learning_engine or LearningEngine()
        self.feedback_history = []

    def record_feedback(
        self,
        action_id: str,
        feedback_type: str,
        reason: str = "",
        key: Optional[str] = None,
        value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Captures structured user feedback and safely updates learning preferences."""
        fb_record = {
            "action_id": action_id,
            "feedback_type": feedback_type,
            "reason": reason
        }
        self.feedback_history.append(fb_record)

        if key and value:
            # Register user explicit preference (USER source rank = 100%)
            self.learning_engine.registry.register_preference(key, value, source="USER")

        return {
            "status": "RECORDED",
            "action_id": action_id,
            "feedback_type": feedback_type,
            "permission_expanded": False  # Invariant: Feedback NEVER expands permissions directly
        }
