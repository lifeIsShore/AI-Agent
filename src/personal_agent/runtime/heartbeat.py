import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class HeartbeatSnapshot:
    heartbeat_id: str
    timestamp: float
    state: str
    active_goal_id: Optional[str] = None
    current_operation: str = "idle"
    latency_ms: float = 0.0
    consecutive_errors: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class HeartbeatMonitor:
    def __init__(self, interval_sec: float = 10.0):
        self.interval_sec = interval_sec
        self.history: List[HeartbeatSnapshot] = []
        self.last_heartbeat: Optional[HeartbeatSnapshot] = None

    def record_heartbeat(
        self,
        state: str,
        active_goal_id: Optional[str] = None,
        current_operation: str = "idle",
        latency_ms: float = 0.0,
        consecutive_errors: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HeartbeatSnapshot:
        hb = HeartbeatSnapshot(
            heartbeat_id=f"hb_{uuid.uuid4().hex[:8]}",
            timestamp=time.time(),
            state=state,
            active_goal_id=active_goal_id,
            current_operation=current_operation,
            latency_ms=latency_ms,
            consecutive_errors=consecutive_errors,
            metadata=metadata or {}
        )
        self.last_heartbeat = hb
        self.history.append(hb)
        if len(self.history) > 100:
            self.history.pop(0)
        return hb

    def get_latest_heartbeat(self) -> Optional[HeartbeatSnapshot]:
        return self.last_heartbeat

    def get_history(self, limit: int = 50) -> List[HeartbeatSnapshot]:
        return self.history[-limit:]

    def is_healthy(self, max_staleness_sec: float = 30.0) -> bool:
        if not self.last_heartbeat:
            return False
        staleness = time.time() - self.last_heartbeat.timestamp
        return staleness <= max_staleness_sec
