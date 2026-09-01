import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from personal_agent.memory.manager import MemoryManager
from personal_agent.policy.proposal import ActionProposal

# Memory Scope Constants
SCOPE_DURABLE_PREFERENCE = "durable_preference"
SCOPE_EVENT_MEMORY = "event_memory"

# Preference Scope Hierarchy
PREFERENCE_SCOPE_GLOBAL = "GLOBAL"
PREFERENCE_SCOPE_ACTION = "ACTION"
PREFERENCE_SCOPE_TARGET = "TARGET"
PREFERENCE_SCOPE_CATEGORY = "CATEGORY"
PREFERENCE_SCOPE_SENDER = "SENDER"
PREFERENCE_SCOPE_CONTEXT = "CONTEXT"

class MemoryLearningLoop:
    def __init__(self, memory_manager: Optional[MemoryManager] = None, default_decay_rate: float = 0.95):
        self.memory_manager = memory_manager or MemoryManager(gateway=None)
        self.decay_rate = default_decay_rate

    def infer_preference_scope(self, proposal: ActionProposal, user_reason: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Infers the granular preference scope and condition constraints for a proposal."""
        reason_text = (user_reason or proposal.reason or "").lower()
        target_text = proposal.target.lower()

        condition = {"action": proposal.action}

        if "sender" in proposal.parameters or "email_" in target_text:
            sender = proposal.parameters.get("sender", "automated_service")
            condition["sender"] = sender
            return PREFERENCE_SCOPE_SENDER, condition

        if "newsletter" in reason_text or "digest" in reason_text or "category" in proposal.parameters:
            category = proposal.parameters.get("category", "newsletter")
            condition["category"] = category
            return PREFERENCE_SCOPE_CATEGORY, condition

        if proposal.target and proposal.target != "primary":
            condition["target"] = proposal.target
            return PREFERENCE_SCOPE_TARGET, condition

        return PREFERENCE_SCOPE_ACTION, condition

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

    def update_confidence(self, current_confidence: float, positive_signal: bool) -> float:
        """Updates preference confidence based on positive (approval) or negative (rejection) observation signals."""
        if positive_signal:
            return min(1.0, round(current_confidence * 0.85 + 0.25, 2))
        else:
            return max(0.0, round(current_confidence * 0.85 - 0.25, 2))

    def apply_decay(self, current_confidence: float, days_elapsed: float) -> float:
        """Applies exponential time decay to learned preference confidence score."""
        decay_factor = self.decay_rate ** days_elapsed
        return max(0.0, round(current_confidence * decay_factor, 2))

    def record_feedback(
        self,
        proposal: ActionProposal,
        user_decision: str,
        user_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Captures user approval or rejection into MemoryStore with scope, confidence, and observation tracking."""
        if not self.memory_manager:
            return None

        action_name = proposal.action
        target_name = proposal.target
        orig_reason = proposal.reason

        scope_category, memory_type, importance = self.classify_feedback(proposal, user_decision, user_reason)
        pref_scope, pref_condition = self.infer_preference_scope(proposal, user_reason)

        initial_confidence = 0.50 if user_decision == "APPROVED" else 0.20
        updated_confidence = self.update_confidence(initial_confidence, positive_signal=(user_decision == "APPROVED"))

        if user_decision == "APPROVED":
            content = f"User approved action '{action_name}' on target '{target_name}' (Reason: {orig_reason})."
        elif user_decision == "REJECTED":
            reason_str = user_reason or orig_reason
            content = f"User rejected action '{action_name}' on target '{target_name}' (Reason: {reason_str})."
        else:
            return None

        metadata = {
            "preference_scope": pref_scope,
            "condition": pref_condition,
            "confidence": updated_confidence,
            "observations": 1,
            "last_observed_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            stored = self.memory_manager.store.add_memory(
                memory_type=memory_type,
                content=content,
                source="user",
                importance=importance,
                confidence=updated_confidence,
                metadata=metadata
            )
            if stored:
                stored["memory_scope"] = scope_category

            print(f"[MemoryLearningLoop] Captured {scope_category.upper()} memory ({pref_scope} confidence={updated_confidence}): '{content}'")
            return stored
        except Exception as e:
            print(f"[MemoryLearningLoop] Error storing feedback memory: {e}")
            return None

    def get_learned_preferences(self) -> List[Dict[str, Any]]:
        """Retrieves active preference memories with applied decay."""
        if not self.memory_manager:
            return []

        all_memories = self.memory_manager.store.get_memories(memory_type="preference")
        now = datetime.now(timezone.utc)

        decayed_memories = []
        for mem in all_memories:
            created_str = mem.get("created_at")
            confidence = mem.get("confidence", 0.5)

            if created_str:
                try:
                    c_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    days_elapsed = (now - c_dt).total_seconds() / 86400.0
                    confidence = self.apply_decay(confidence, days_elapsed)
                except ValueError:
                    pass

            mem["decayed_confidence"] = confidence
            decayed_memories.append(mem)

        return decayed_memories
