import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from personal_agent.security.dlp import DataLossPreventionEngine

@dataclass
class AgentMessage:
    message_id: str
    sender_agent: str
    receiver_agent: str
    task_id: str
    payload: Dict[str, Any]
    sensitivity: str = "INTERNAL"
    provenance: str = "A2A_BUS"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class A2AMessageBus:
    def __init__(self, dlp_engine: DataLossPreventionEngine = None):
        self.dlp_engine = dlp_engine or DataLossPreventionEngine()

    def send_message(self, message: AgentMessage) -> Tuple[bool, str]:
        """Validates DLP rules and transmits message between specialist agents."""
        items = [{"content": str(message.payload)}]
        sanitized_items, blocked_count = self.dlp_engine.sanitize_context_payload(items)
        if blocked_count > 0:
            return False, f"A2A Message Blocked by DLP: Sensitive payload detected."

        return True, f"A2A Message [{message.message_id}] delivered successfully from '{message.sender_agent}' to '{message.receiver_agent}'."
