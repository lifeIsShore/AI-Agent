import os
import json
import time
import uuid
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class FactProvenance:
    fact_id: str
    statement: str
    source_system: str
    source_id: str
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    deriving_agent_id: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FactProvenance":
        return cls(
            fact_id=data.get("fact_id", f"fact_{uuid.uuid4().hex[:8]}"),
            statement=data.get("statement", ""),
            source_system=data.get("source_system", "unknown"),
            source_id=data.get("source_id", "unknown"),
            confidence=data.get("confidence", 1.0),
            timestamp=data.get("timestamp", time.time()),
            deriving_agent_id=data.get("deriving_agent_id", "system")
        )

class ProvenanceTracker:
    def __init__(self, storage_dir: Optional[str] = None, filename: str = "provenance.json"):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
            self.filepath = os.path.join(self.storage_dir, filename)
            os.makedirs(self.storage_dir, exist_ok=True)
            self.facts: Dict[str, FactProvenance] = self.load_provenance()
        else:
            self.storage_dir = None
            self.filepath = None
            self.facts: Dict[str, FactProvenance] = {}

    def record_fact(
        self,
        statement: str,
        source_system: str,
        source_id: str,
        confidence: float = 1.0,
        deriving_agent_id: str = "system"
    ) -> FactProvenance:
        fact_id = f"fact_{uuid.uuid4().hex[:8]}"
        fact = FactProvenance(
            fact_id=fact_id,
            statement=statement,
            source_system=source_system,
            source_id=source_id,
            confidence=confidence,
            timestamp=time.time(),
            deriving_agent_id=deriving_agent_id
        )
        self.facts[fact_id] = fact
        if self.filepath:
            self.save_provenance()
        return fact

    def get_fact_provenance(self, fact_id: str) -> Optional[FactProvenance]:
        return self.facts.get(fact_id)

    def explain_fact(self, fact_id: str) -> Dict[str, Any]:
        fact = self.get_fact_provenance(fact_id)
        if not fact:
            return {"fact_id": fact_id, "found": False, "explanation": "No provenance record found."}

        explanation = (
            f"Fact '{fact.statement}' originated from source system '{fact.source_system}' "
            f"(item ID '{fact.source_id}') derived by agent '{fact.deriving_agent_id}' "
            f"with {int(fact.confidence * 100)}% confidence."
        )

        return {
            "fact_id": fact_id,
            "found": True,
            "statement": fact.statement,
            "source_system": fact.source_system,
            "source_id": fact.source_id,
            "confidence": fact.confidence,
            "deriving_agent_id": fact.deriving_agent_id,
            "explanation": explanation
        }

    def save_provenance(self) -> None:
        if not self.filepath or not self.storage_dir:
            return
        data = {k: v.to_dict() for k, v in self.facts.items()}
        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="prov_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[ProvenanceTracker ERROR] Failed to save provenance: {e}")

    def load_provenance(self) -> Dict[str, FactProvenance]:
        if not self.filepath or not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {k: FactProvenance.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"[ProvenanceTracker WARNING] Failed to load provenance from '{self.filepath}': {e}. Starting fresh.")
            return {}
