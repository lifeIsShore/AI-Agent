import hashlib
import json
from typing import Set, Tuple, Dict, Any
from personal_agent.events.event import AgentEvent

class EventDeduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()

    def compute_event_hash(self, event: AgentEvent) -> str:
        """Computes deterministic SHA256 hash for event identity."""
        source = str(event.source)
        e_type = str(event.event_type)
        e_id = str(event.entity_id)
        payload_str = json.dumps(event.payload, sort_keys=True)

        raw_str = f"{source}:{e_type}:{e_id}:{payload_str}"
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

    def is_duplicate(self, event: AgentEvent) -> Tuple[bool, str]:
        """Checks if event has already been processed."""
        h = self.compute_event_hash(event)
        if h in self.seen_hashes:
            return True, f"Duplicate event suppressed (Hash: {h[:12]})."
        
        self.seen_hashes.add(h)
        return False, f"Unique event accepted (Hash: {h[:12]})."
