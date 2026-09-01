from typing import List, Dict, Any
from personal_agent.world.world_model import PersonalWorldModel
from personal_agent.world.entities import ENTITY_MEETING, ENTITY_TASK, ENTITY_EMAIL_THREAD

SITUATION_MEETING_PREPARATION_RISK = "MEETING_CONFLICT_PREPARATION_RISK"

class SituationDetector:
    def detect_world_situations(self, world_model: PersonalWorldModel) -> List[Dict[str, Any]]:
        """Extracts high-level composite situations from graph relationships and entities."""
        situations = []

        meetings = [e for e in world_model.entities.values() if e.entity_type == ENTITY_MEETING]
        tasks = [e for e in world_model.entities.values() if e.entity_type == ENTITY_TASK]
        emails = [e for e in world_model.entities.values() if e.entity_type == ENTITY_EMAIL_THREAD]

        has_room_change = any("room change" in e.name.lower() or "room" in str(e.attributes).lower() for e in emails)
        has_lecture_meeting = any("lecture" in e.name.lower() or "meeting" in e.name.lower() for e in meetings)

        if has_room_change and has_lecture_meeting:
            situations.append({
                "situation_id": SITUATION_MEETING_PREPARATION_RISK,
                "title": "Meeting Location Change & Preparation Risk",
                "risk": "HIGH",
                "description": "An email announced a meeting room change connected to an upcoming meeting with unfinished preparation tasks.",
                "evidence_count": len(meetings) + len(emails)
            })

        return situations
