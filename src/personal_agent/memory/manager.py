from typing import List, Dict, Any, Optional
from personal_agent.memory.store import MemoryStore
from personal_agent.memory.policy import MemoryPolicy

class MemoryManager:
    def __init__(self, gateway, store_dir: str = "data/memory"):
        self.store = MemoryStore(data_dir=store_dir)
        self.policy = MemoryPolicy(gateway=gateway)

    def process_candidate_fact(self, text: str, source: str = "user") -> Optional[Dict[str, Any]]:
        """Evaluates text through MemoryPolicy and stores it if approved."""
        should_store, eval_data = self.policy.evaluate_candidate(text, source=source)
        if should_store:
            m_type = eval_data.get("memory_type", "preference")
            content = eval_data.get("content", text)
            importance = eval_data.get("importance", "medium")
            
            stored_item = self.store.add_memory(
                memory_type=m_type,
                content=content,
                source=source,
                importance=importance,
                confidence=1.0 if source == "user" else 0.85
            )
            stored_item["policy_reason"] = eval_data.get("reason")
            return stored_item
        return None

    def get_context_memories(self, importance: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves active, non-expired memories for context injection."""
        return self.store.get_memories(importance=importance)

    def add_explicit_memory(self, memory_type: str, content: str, importance: str = "high") -> Dict[str, Any]:
        """Direct user addition without policy filtering."""
        return self.store.add_memory(
            memory_type=memory_type,
            content=content,
            source="user",
            importance=importance,
            confidence=1.0
        )
