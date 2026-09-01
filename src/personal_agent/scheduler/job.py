from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Callable, Optional, Dict, Any

@dataclass
class Job:
    job_id: str
    name: str
    interval_minutes: int
    handler: Callable[[], Dict[str, Any]]
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_due(self) -> bool:
        """Returns True if current time >= next_run timestamp."""
        if not self.enabled or not self.next_run:
            return False
        try:
            next_dt = datetime.fromisoformat(self.next_run.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) >= next_dt
        except ValueError:
            return False

    def mark_executed(self):
        """Updates last_run and recalculates next_run based on interval_minutes."""
        now = datetime.now(timezone.utc)
        self.last_run = now.isoformat()
        self.next_run = (now + timedelta(minutes=self.interval_minutes)).isoformat()
