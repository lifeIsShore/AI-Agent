from typing import Dict, Any, List, Optional

class MemoryProvenanceGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def add_memory_node(
        self,
        memory_id: str,
        source: str,
        evidence: List[str],
        confidence: float = 0.85,
        observations: int = 1
    ):
        self.nodes[memory_id] = {
            "memory_id": memory_id,
            "source": source,
            "evidence": evidence,
            "confidence": confidence,
            "observations": observations,
            "superseded_by": None
        }

    def mark_superseded(self, old_memory_id: str, new_memory_id: str):
        if old_memory_id in self.nodes:
            self.nodes[old_memory_id]["superseded_by"] = new_memory_id

    def get_lineage(self, memory_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(memory_id)
