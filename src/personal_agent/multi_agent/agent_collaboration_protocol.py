import uuid
import time
from typing import Dict, Any, List, Optional

class AgentMessage:
    def __init__(self, sender_id: str, receiver_id: str, message_type: str, content: str, payload: Optional[Dict[str, Any]] = None):
        self.msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        self.timestamp = time.strftime("%H:%M:%S")
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.content = content
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "content": self.content,
            "payload": self.payload
        }

class CollaborationProtocol:
    def __init__(self):
        self.message_history: List[AgentMessage] = []

    def send_message(self, sender_id: str, receiver_id: str, message_type: str, content: str, payload: Optional[Dict[str, Any]] = None) -> AgentMessage:
        msg = AgentMessage(sender_id, receiver_id, message_type, content, payload)
        self.message_history.append(msg)
        return msg

    def get_collaboration_stream(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.message_history]

class AgentTaskDelegator:
    def delegate_subtask(self, delegator_agent: str, target_agent: str, subtask_name: str) -> Dict[str, Any]:
        return {
            "delegation_id": f"del_{uuid.uuid4().hex[:8]}",
            "delegator": delegator_agent,
            "target": target_agent,
            "subtask": subtask_name,
            "status": "DELEGATED"
        }
