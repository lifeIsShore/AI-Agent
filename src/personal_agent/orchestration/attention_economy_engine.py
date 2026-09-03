from typing import Dict, Any, List

class AttentionEconomyEngine:
    def evaluate_event_attention(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates attention score and categorizes alert priority into Attention Queue."""
        importance = event_data.get("importance", 0.8)
        urgency = event_data.get("urgency", 0.7)
        relevance = event_data.get("goal_relevance", 0.9)
        confidence = event_data.get("confidence", 0.85)
        benefit = event_data.get("expected_benefit", 0.8)
        cost = max(0.1, event_data.get("interruption_cost", 0.3))

        score = round((importance * urgency * relevance * confidence * benefit) / cost, 2)

        if score >= 1.5:
            priority = "HIGH"
            deferred = False
        elif score >= 0.6:
            priority = "MEDIUM"
            deferred = False
        else:
            priority = "LOW"
            deferred = True

        return {
            "event_title": event_data.get("title", "Event Alert"),
            "attention_score": score,
            "priority": priority,
            "deferred_automatically": deferred,
            "recommendation": "Display alert in real-time" if not deferred else "Defer to daily summary digest"
        }
