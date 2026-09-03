import time
import hashlib
import json
from typing import Set, Tuple, Dict, Any, Optional
from personal_agent.events.event import AgentEvent

class EventDeduplicator:
    def __init__(self, ttl_seconds: float = 3600.0):
        self.ttl_seconds = ttl_seconds
        self.seen_hashes: Dict[str, float] = {}
        self.executed_idempotency_keys: Dict[str, float] = {}

    def compute_event_hash(self, event: AgentEvent) -> str:
        """Computes deterministic SHA256 hash for event identity."""
        if event.idempotency_key:
            return event.idempotency_key
        source = str(event.source)
        e_type = str(event.event_type)
        e_id = str(event.entity_id)
        payload_str = json.dumps(event.payload, sort_keys=True)

        raw_str = f"{source}:{e_type}:{e_id}:{payload_str}"
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

    def _cleanup_stale(self):
        now = time.time()
        stale_hashes = [h for h, ts in self.seen_hashes.items() if (now - ts) > self.ttl_seconds]
        for h in stale_hashes:
            del self.seen_hashes[h]

        stale_keys = [k for k, ts in self.executed_idempotency_keys.items() if (now - ts) > self.ttl_seconds]
        for k in stale_keys:
            del self.executed_idempotency_keys[k]

    def is_duplicate(self, event: AgentEvent) -> Tuple[bool, str]:
        """Checks if event has already been processed within the TTL window."""
        self._cleanup_stale()
        h = self.compute_event_hash(event)
        now = time.time()

        if h in self.seen_hashes:
            return True, f"Duplicate event suppressed (Hash: {h[:12]})."
        
        self.seen_hashes[h] = now
        return False, f"Unique event accepted (Hash: {h[:12]})."

    def record_execution(self, idempotency_key: str):
        """Records an action execution to guarantee idempotency across duplicate event streams."""
        self.executed_idempotency_keys[idempotency_key] = time.time()

    def is_action_executed(self, idempotency_key: str) -> bool:
        """Returns True if the action associated with this idempotency key was already executed."""
        self._cleanup_stale()
        return idempotency_key in self.executed_idempotency_keys

