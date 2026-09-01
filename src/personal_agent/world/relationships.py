from dataclasses import dataclass

RELATION_PARTICIPATES_IN = "PARTICIPATES_IN"
RELATION_AUTHORED = "AUTHORED"
RELATION_REFERENCES = "REFERENCES"
RELATION_DEPENDS_ON = "DEPENDS_ON"
RELATION_LOCATED_AT = "LOCATED_AT"
RELATION_ASSOCIATED_WITH = "ASSOCIATED_WITH"

@dataclass
class WorldRelationship:
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float = 1.0
    provenance: str = "WORLD_MODEL"
