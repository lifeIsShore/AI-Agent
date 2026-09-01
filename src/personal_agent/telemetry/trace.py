import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional

@dataclass
class TraceContext:
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:12]}")
    request_id: Optional[str] = None
    event_id: Optional[str] = None
    proposal_id: Optional[str] = None
    execution_id: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TraceContext":
        return cls(
            trace_id=data.get("trace_id", f"trace_{uuid.uuid4().hex[:12]}"),
            request_id=data.get("request_id"),
            event_id=data.get("event_id"),
            proposal_id=data.get("proposal_id"),
            execution_id=data.get("execution_id"),
            start_time=data.get("start_time", datetime.now(timezone.utc).isoformat())
        )

    def create_child_span(self, proposal_id: Optional[str] = None, execution_id: Optional[str] = None) -> "TraceContext":
        """Derives a child TraceContext inheriting the root trace_id and request_id."""
        return TraceContext(
            trace_id=self.trace_id,
            request_id=self.request_id,
            event_id=self.event_id,
            proposal_id=proposal_id or self.proposal_id,
            execution_id=execution_id or self.execution_id,
            start_time=datetime.now(timezone.utc).isoformat()
        )
