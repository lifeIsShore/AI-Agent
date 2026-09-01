from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class WorldFact:
    fact_id: str
    value: str
    source: str
    source_id: str
    trust_level: str = "EXTERNAL"
    sensitivity: str = "INTERNAL"
    confidence: float = 0.90
    evidence_count: int = 1
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
