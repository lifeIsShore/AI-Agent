from typing import Dict, List, Optional
from personal_agent.world.entities import WorldEntity
from personal_agent.world.relationships import WorldRelationship

class PersonalWorldModel:
    def __init__(self):
        self.entities: Dict[str, WorldEntity] = {}
        self.relationships: List[WorldRelationship] = []

    def register_entity(self, entity: WorldEntity):
        """Registers or updates a WorldEntity in the graph model."""
        self.entities[entity.entity_id] = entity

    def add_relationship(self, rel: WorldRelationship):
        """Adds a typed WorldRelationship edge between entities."""
        self.relationships.append(rel)

    def get_entity(self, entity_id: str) -> Optional[WorldEntity]:
        """Retrieves a WorldEntity by its unique ID."""
        return self.entities.get(entity_id)

    def get_related_entities(self, entity_id: str, relation_type: Optional[str] = None) -> List[WorldEntity]:
        """Queries all entities connected to entity_id via relationships."""
        related = []
        for r in self.relationships:
            if r.source_entity_id == entity_id and (relation_type is None or r.relation_type == relation_type):
                target = self.entities.get(r.target_entity_id)
                if target:
                    related.append(target)
            elif r.target_entity_id == entity_id and (relation_type is None or r.relation_type == relation_type):
                source = self.entities.get(r.source_entity_id)
                if source:
                    related.append(source)
        return related
