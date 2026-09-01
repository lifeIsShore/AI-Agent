from dataclasses import dataclass, field
from typing import Dict, Any

ACTION_IGNORE = "IGNORE"
ACTION_INFORMATIONAL = "INFORMATIONAL"
ACTION_REVIEW = "REVIEW"
ACTION_NOTIFY = "NOTIFY"
ACTION_WORKFLOW = "WORKFLOW"

@dataclass
class EventClassification:
    importance: float
    urgency: float
    actionability: float
    risk: str
    category: str
    recommended_action: str

class EventClassifier:
    def classify_event(self, event_type: str, payload: Dict[str, Any]) -> EventClassification:
        """Evaluates importance, urgency, actionability, and recommended action for an incoming event."""
        subject = str(payload.get("subject", payload.get("summary", ""))).lower()
        sender = str(payload.get("sender", "")).lower()

        importance = 0.50
        urgency = 0.40
        actionability = 0.50
        risk = "LOW"
        category = "GENERAL"
        recommended_action = ACTION_INFORMATIONAL

        if "deadline" in subject or "urgent" in subject or "room change" in subject:
            importance = 0.92
            urgency = 0.88
            actionability = 0.90
            category = "UNIVERSITY"
            recommended_action = ACTION_WORKFLOW
            if "deadline" in subject:
                risk = "MEDIUM"
        elif "meeting" in subject or "schedule" in subject:
            importance = 0.75
            urgency = 0.70
            actionability = 0.80
            category = "CALENDAR"
            recommended_action = ACTION_REVIEW
        elif "newsletter" in subject or "job alerts" in subject or "digest" in subject:
            importance = 0.30
            urgency = 0.10
            actionability = 0.20
            category = "MARKETING"
            recommended_action = ACTION_IGNORE

        return EventClassification(
            importance=importance,
            urgency=urgency,
            actionability=actionability,
            risk=risk,
            category=category,
            recommended_action=recommended_action
        )
