import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

MSG_TYPE_TASK_DELEGATION = "TASK_DELEGATION"
MSG_TYPE_RESULT_REPORT = "RESULT_REPORT"
MSG_TYPE_QUERY = "QUERY"
MSG_TYPE_RESPONSE = "RESPONSE"

@dataclass
class AgentMessage:
    message_id: str
    sender_agent_id: str
    recipient_agent_id: str
    task_id: str
    message_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            message_id=data.get("message_id", f"msg_{uuid.uuid4().hex[:8]}"),
            sender_agent_id=data.get("sender_agent_id", "system"),
            recipient_agent_id=data.get("recipient_agent_id", "all"),
            task_id=data.get("task_id", "t_default"),
            message_type=data.get("message_type", MSG_TYPE_QUERY),
            payload=data.get("payload", {}),
            confidence=data.get("confidence", 1.0),
            evidence=data.get("evidence", []),
            timestamp=data.get("timestamp", time.time())
        )

class AgentMessageBus:
    def __init__(self):
        self.message_history: List[AgentMessage] = []

    def send_message(
        self,
        sender_agent_id: str,
        recipient_agent_id: str,
        task_id: str,
        message_type: str,
        payload: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        evidence: Optional[List[str]] = None
    ) -> AgentMessage:
        msg = AgentMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            sender_agent_id=sender_agent_id,
            recipient_agent_id=recipient_agent_id,
            task_id=task_id,
            message_type=message_type,
            payload=payload or {},
            confidence=confidence,
            evidence=evidence or [],
            timestamp=time.time()
        )
        self.message_history.append(msg)
        return msg

    def get_messages_for_agent(self, agent_id: str) -> List[AgentMessage]:
        return [m for m in self.message_history if m.recipient_agent_id in (agent_id, "all")]

    def get_task_messages(self, task_id: str) -> List[AgentMessage]:
        return [m for m in self.message_history if m.task_id == task_id]
