from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional

@dataclass
class ProvenanceRecord:
    content_id: str
    source: str                        # gmail | calendar | tasks | RAG
    source_id: str                     # e.g. msg_123
    trust_level: str                   # SYSTEM | USER | TRUSTED_MEMORY | EXTERNAL
    sensitivity: str                   # PUBLIC | PERSONAL | SENSITIVE | HIGHLY_SENSITIVE
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None

class ProvenanceTracker:
    def __init__(self):
        self.records: Dict[str, ProvenanceRecord] = {}

    def tag_provenance(
        self,
        content_id: str,
        source: str,
        source_id: str,
        trust_level: str = "EXTERNAL",
        sensitivity: str = "PERSONAL"
    ) -> ProvenanceRecord:
        """Attaches verifiable lineage record to a context item."""
        record = ProvenanceRecord(
            content_id=content_id,
            source=source,
            source_id=source_id,
            trust_level=trust_level,
            sensitivity=sensitivity
        )
        self.records[content_id] = record
        return record

    def get_provenance(self, content_id: str) -> Optional[ProvenanceRecord]:
        return self.records.get(content_id)

    def explain_lineage(self, content_id: str) -> str:
        """Generates human-readable verifiable data lineage explanation."""
        rec = self.get_provenance(content_id)
        if not rec:
            return f"Lineage for '{content_id}' is unknown."
        return (
            f"Information originated from {rec.source.upper()} item '{rec.source_id}' "
            f"(Trust: {rec.trust_level} | Sensitivity: {rec.sensitivity} | Retrieved: {rec.retrieved_at[:19]})."
        )
