from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class ManagedMemory:
    memory_id: str
    content: str
    category: str
    confidence: float = 0.80
    evidence_count: int = 1
    last_observed: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContradictionDetector:
    def detect_contradiction(
        self,
        existing_memory: ManagedMemory,
        new_action: str
    ) -> Tuple[bool, str, float]:
        """Detects contradictions between existing learned preferences and new user feedback."""
        content_lower = existing_memory.content.lower()
        action_lower = new_action.lower()

        # Check opposing time preference
        if "afternoon" in content_lower and "morning" in action_lower:
            new_conf = max(0.40, existing_memory.confidence - 0.30)
            return True, f"Contradiction detected: User approved '{new_action}' contradicting stored preference '{existing_memory.content}'.", round(new_conf, 2)
        elif "morning" in content_lower and "afternoon" in action_lower:
            new_conf = max(0.40, existing_memory.confidence - 0.30)
            return True, f"Contradiction detected: User approved '{new_action}' contradicting stored preference '{existing_memory.content}'.", round(new_conf, 2)

        return False, "No contradiction detected.", existing_memory.confidence

class MemoryLifecycleManager:
    def __init__(self):
        self.memories: Dict[str, ManagedMemory] = {}
        self.contradiction_detector = ContradictionDetector()

    def add_memory(self, memory_id: str, content: str, category: str, confidence: float = 0.80) -> ManagedMemory:
        mem = ManagedMemory(
            memory_id=memory_id,
            content=content,
            category=category,
            confidence=confidence,
            evidence_count=1
        )
        self.memories[memory_id] = mem
        return mem

    def update_with_feedback(self, memory_id: str, new_action: str) -> Tuple[bool, str]:
        """Updates memory lifecycle based on user feedback and contradiction checks."""
        mem = self.memories.get(memory_id)
        if not mem:
            return False, "Memory not found."

        has_contradiction, reason, updated_conf = self.contradiction_detector.detect_contradiction(mem, new_action)
        if has_contradiction:
            mem.confidence = updated_conf
            return True, f"[Contradiction Handling] {reason} Confidence demoted to {updated_conf}."

        mem.evidence_count += 1
        mem.confidence = min(0.99, mem.confidence + 0.05)
        return True, f"Evidence count promoted to {mem.evidence_count} (Confidence {mem.confidence:.2f})."
