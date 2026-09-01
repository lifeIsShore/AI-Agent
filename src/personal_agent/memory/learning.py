from typing import Dict, Any, Optional
from personal_agent.memory.manager import MemoryManager
from personal_agent.policy.proposal import ActionProposal

class MemoryLearningLoop:
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory_manager = memory_manager or MemoryManager(gateway=None)

    def record_feedback(
        self,
        proposal: ActionProposal,
        user_decision: str,
        user_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Captures user approval or rejection into MemoryStore as a learned preference."""
        if not self.memory_manager:
            return None

        action_name = proposal.action
        target_name = proposal.target
        orig_reason = proposal.reason

        if user_decision == "APPROVED":
            content = f"User approved action '{action_name}' on target '{target_name}' (Reason: {orig_reason})."
        elif user_decision == "REJECTED":
            reason_str = user_reason or orig_reason
            content = f"User rejected action '{action_name}' on target '{target_name}' (Reason: {reason_str})."
        else:
            return None

        try:
            stored = self.memory_manager.add_explicit_memory(
                memory_type="preference",
                content=content,
                importance="medium"
            )
            print(f"[MemoryLearningLoop] Captured preference memory: '{content}'")
            return stored
        except Exception as e:
            print(f"[MemoryLearningLoop] Error storing feedback memory: {e}")
            return None

    def get_learned_preferences(self) -> list:
        """Retrieves learned user preference memories."""
        if not self.memory_manager:
            return []
        return self.memory_manager.get_context_memories(importance="medium")
