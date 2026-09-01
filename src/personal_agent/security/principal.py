from dataclasses import dataclass, field
from typing import List, Dict, Any

PRINCIPAL_SYSTEM = "SYSTEM"
PRINCIPAL_USER = "USER"
PRINCIPAL_AGENT = "AGENT"
PRINCIPAL_SCHEDULER = "SCHEDULER"
PRINCIPAL_EXTERNAL_CONTENT = "EXTERNAL_CONTENT"
PRINCIPAL_TOOL = "TOOL"

@dataclass
class Principal:
    principal_id: str
    principal_type: str
    assigned_capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_user(self) -> bool:
        return self.principal_type == PRINCIPAL_USER

    def is_scheduler(self) -> bool:
        return self.principal_type == PRINCIPAL_SCHEDULER
