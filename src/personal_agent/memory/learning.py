from typing import Dict, Any, Optional, Tuple
from personal_agent.memory.manager import MemoryManager
from personal_agent.policy.proposal import ActionProposal

# Memory Scope Constants
SCOPE_DURABLE_PREFERENCE = "durable_preference"
SCOPE_EVENT_MEMORY = "event_memory"

class MemoryLearningLoop:
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory_manager = memory_manager or MemoryManager(gateway=None)

    def classify_feedback(
        self,
        proposal: ActionProposal,
        user_decision: str,
        user_reason: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """Classifies user feedback into (memory_scope, memory_type, importance)."""
        reason_text = (user_reason or proposal.reason or "").lower()
        action_name = proposal.action.lower()
        target_name = proposal.target.lower()

        # Deterministic Durable Preference Indicators
        durable_indicators = ["always", "never", "prefer", "newsletter", "automated", "rule", "usually", "digest", "general"]
        if any(ind in reason_text or ind in target_name for ind in durable_indicators):
            return SCOPE_DURABLE_PREFERENCE, "preference", "high"

        # Calendar event actions default to point-in-time event_memory unless explicit durable preference phrase used
        if "calendar" in action_name or "event" in action_name:
            if "prefer" in reason_text or "always" in reason_text:
                return SCOPE_DURABLE_PREFERENCE, "preference", "high"
            return SCOPE_EVENT_MEMORY, "event_history", "low"

        # Single item rejections/approvals default to event_memory
        if user_decision == "REJECTED" and not any(ind in reason_text for ind in durable_indicators):
            return SCOPE_EVENT_MEMORY, "event_history", "low"

        return SCOPE_DURABLE_PREFERENCE, "preference", "medium"

    def record_feedback(
        self,
        proposal: ActionProposal,
        user_decision: str,
        user_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Captures user approval or rejection into MemoryStore classified as durable preference or event memory."""
        if not self.memory_manager:
            return None

        action_name = proposal.action
        target_name = proposal.target
        orig_reason = proposal.reason

        scope, memory_type, importance = self.classify_feedback(proposal, user_decision, user_reason)

        if user_decision == "APPROVED":
            content = f"User approved action '{action_name}' on target '{target_name}' (Reason: {orig_reason})."
        elif user_decision == "REJECTED":
            reason_str = user_reason or orig_reason
            content = f"User rejected action '{action_name}' on target '{target_name}' (Reason: {reason_str})."
        else:
            return None

        try:
            stored = self.memory_manager.add_explicit_memory(
                memory_type=memory_type,
                content=content,
                importance=importance
            )
            if stored:
                stored["memory_scope"] = scope

            print(f"[MemoryLearningLoop] Captured {scope.upper()} memory [{importance}]: '{content}'")
            return stored
        except Exception as e:
            print(f"[MemoryLearningLoop] Error storing feedback memory: {e}")
            return None

    def get_learned_preferences(self) -> list:
        """Retrieves durable user preference memories."""
        if not self.memory_manager:
            return []
        return self.memory_manager.get_context_memories(importance="medium")
