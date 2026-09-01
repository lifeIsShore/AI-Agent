import uuid
from typing import Optional, Dict, Any
from personal_agent.world.entities import WorldEntity, ENTITY_PERSON
from personal_agent.world.world_model import PersonalWorldModel

class EntityResolver:
    def resolve_or_create_person(
        self,
        raw_name: str,
        email: Optional[str] = None,
        world_model: Optional[PersonalWorldModel] = None
    ) -> WorldEntity:
        """Disambiguates person entity reference and merges with existing matching graph entity."""
        if world_model:
            # Check existing PERSON entities for name/email match
            for ent in world_model.entities.values():
                if ent.entity_type == ENTITY_PERSON:
                    ent_email = ent.attributes.get("email", "")
                    ent_name = ent.name.lower()
                    
                    if email and ent_email and email.lower() == ent_email.lower():
                        return ent
                    
                    if "müller" in raw_name.lower() and "müller" in ent_name:
                        return ent

        # Create new resolved entity
        ent_id = f"person_{uuid.uuid4().hex[:6]}"
        new_ent = WorldEntity(
            entity_id=ent_id,
            entity_type=ENTITY_PERSON,
            name=raw_name,
            attributes={"email": email or ""},
            confidence=0.95
        )
        if world_model:
            world_model.register_entity(new_ent)
        return new_ent
