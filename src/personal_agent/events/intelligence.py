from typing import Dict, Any, Tuple, Optional
from personal_agent.events.event import AgentEvent
from personal_agent.events.classifier import EventClassifier, EventClassification

class EventIntelligenceEngine:
    def __init__(self):
        self.classifier = EventClassifier()

    def process_incoming_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Runs event intelligence classification and computes recommendation metrics."""
        classification = self.classifier.classify_event(event.event_type, event.payload)
        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "classification": classification,
            "importance": classification.importance,
            "urgency": classification.urgency,
            "actionability": classification.actionability,
            "recommended_action": classification.recommended_action
        }
