from typing import List, Dict, Any
from personal_agent.events.event import AgentEvent

SITUATION_SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT_CREATED"
SITUATION_DEADLINE_APPROACHING = "DEADLINE_APPROACHING_OVERLOADED"

class EventCorrelator:
    def detect_composite_situations(
        self,
        events: List[AgentEvent],
        calendar_events: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Correlates multiple domain events to identify composite situation alerts."""
        situations = []

        # Check for room change email + existing calendar event
        has_room_change_email = any("room change" in str(e.payload.get("subject", "")).lower() for e in events)
        has_lecture_event = any("lecture" in str(c.get("summary", "")).lower() for c in calendar_events)

        if has_room_change_email and has_lecture_event:
            situations.append({
                "situation_id": SITUATION_SCHEDULE_CONFLICT,
                "title": "Lecture room change conflict detected",
                "risk": "MEDIUM",
                "description": "An email announced a lecture room change that conflicts with your existing calendar lecture slot.",
                "action_required": True
            })

        # Check for approaching deadline + overloaded calendar
        has_deadline_email = any("deadline" in str(e.payload.get("subject", "")).lower() for e in events)
        if has_deadline_email and len(calendar_events) >= 2:
            situations.append({
                "situation_id": SITUATION_DEADLINE_APPROACHING,
                "title": "Approaching deadline on overloaded schedule",
                "risk": "HIGH",
                "description": "A deadline is approaching while your calendar schedule has multiple conflicting events.",
                "action_required": True
            })

        return situations
