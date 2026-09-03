import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from personal_agent.workspace.workspace_connector import NormalizedWorkspaceItem

@dataclass
class CanonicalEntity:
    entity_id: str
    entity_type: str  # person, organization, project, document
    primary_name: str
    aliases: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.90

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class EntityResolver:
    def __init__(self):
        self.entities: Dict[str, CanonicalEntity] = {}

    def resolve_entities_from_items(self, items: List[NormalizedWorkspaceItem]) -> List[CanonicalEntity]:
        """Resolves cross-system references into canonical entity representations."""
        for item in items:
            if item.author and "@" in item.author:
                email = item.author.lower()
                name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
                entity_key = f"person:{email}"

                if entity_key in self.entities:
                    ent = self.entities[entity_key]
                    if item.source_system not in ent.sources:
                        ent.sources.append(item.source_system)
                else:
                    ent = CanonicalEntity(
                        entity_id=f"ent_{uuid.uuid4().hex[:8]}",
                        entity_type="person",
                        primary_name=name,
                        aliases=[email],
                        sources=[item.source_system],
                        confidence=0.95
                    )
                    self.entities[entity_key] = ent

        return list(self.entities.values())

    def get_canonical_entity(self, alias: str) -> Optional[CanonicalEntity]:
        alias_clean = alias.lower()
        for ent in self.entities.values():
            if alias_clean in [a.lower() for a in ent.aliases] or alias_clean in ent.primary_name.lower():
                return ent
        return None
