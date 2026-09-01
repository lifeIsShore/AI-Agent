from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any

ENTITY_PERSON = "PERSON"
ENTITY_ORGANIZATION = "ORGANIZATION"
ENTITY_PROJECT = "PROJECT"
ENTITY_MEETING = "MEETING"
ENTITY_TASK = "TASK"
ENTITY_EMAIL_THREAD = "EMAIL_THREAD"
ENTITY_DEADLINE = "DEADLINE"
ENTITY_LOCATION = "LOCATION"
ENTITY_DOCUMENT = "DOCUMENT"
ENTITY_WORKFLOW = "WORKFLOW"

@dataclass
class WorldEntity:
    entity_id: str
    entity_type: str
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    sensitivity: str = "INTERNAL"
    trust_level: str = "SYSTEM"
    confidence: float = 1.0
    provenance: str = "WORLD_MODEL"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
