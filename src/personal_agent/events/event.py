import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional

EVENT_EMAIL_RECEIVED = "EMAIL_RECEIVED"
EVENT_EMAIL_UPDATED = "EMAIL_UPDATED"

EVENT_CALENDAR_CREATED = "CALENDAR_EVENT_CREATED"
EVENT_CALENDAR_UPDATED = "CALENDAR_EVENT_UPDATED"
EVENT_CALENDAR_CANCELLED = "CALENDAR_EVENT_CANCELLED"

EVENT_TASK_CREATED = "TASK_CREATED"
EVENT_TASK_COMPLETED = "TASK_COMPLETED"
EVENT_TASK_UPDATED = "TASK_UPDATED"

EVENT_PROPOSAL_CREATED = "PROPOSAL_CREATED"
EVENT_PROPOSAL_APPROVED = "PROPOSAL_APPROVED"
EVENT_PROPOSAL_REJECTED = "PROPOSAL_REJECTED"
EVENT_PROPOSAL_EXPIRED = "PROPOSAL_EXPIRED"

EVENT_ACTION_EXECUTED = "ACTION_EXECUTED"
EVENT_ACTION_FAILED = "ACTION_FAILED"

EVENT_MEMORY_UPDATED = "MEMORY_UPDATED"

EVENT_GOAL_CHANGED = "GOAL_CHANGED"
EVENT_DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
EVENT_SYSTEM_RESOURCE_WARNING = "SYSTEM_RESOURCE_WARNING"
EVENT_RUNTIME_RECOVERED = "RUNTIME_RECOVERED"

@dataclass
class AgentEvent:
    event_type: str
    source: str
    entity_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processed: bool = False
    correlation_id: Optional[str] = None
    priority: str = "NORMAL"
    idempotency_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentEvent":
        return cls(
            event_id=data.get("event_id", f"evt_{uuid.uuid4().hex[:12]}"),
            event_type=data.get("event_type", "UNKNOWN"),
            source=data.get("source", "system"),
            entity_id=data.get("entity_id", "none"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            processed=data.get("processed", False),
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", "NORMAL"),
            idempotency_key=data.get("idempotency_key")
        )
