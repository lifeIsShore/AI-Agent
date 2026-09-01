from typing import List, Dict, Any, Optional
from personal_agent.reasoning.plan import DecisionPlan

class DecisionReasoner:
    def build_decision_plan(
        self,
        user_request: str,
        context_items: List[Dict[str, Any]],
        confidence: float = 0.90
    ) -> DecisionPlan:
        """Constructs a structured DecisionPlan through task decomposition and candidate action planning."""
        subtasks = [
            "Inspect calendar schedule for free slots",
            "Inspect pending email triage items",
            "Identify time conflicts and priority tasks",
            "Formulate candidate schedule and archive proposals"
        ]

        required_context = ["emails", "calendar_events", "free_slots"]
        
        candidate_actions = []
        for item in context_items:
            if "subject" in item and "thesis" in item.get("subject", "").lower():
                candidate_actions.append({
                    "action": "create_calendar_event",
                    "target": "primary_calendar",
                    "reason": "Thesis submission deadline focus slot"
                })
            elif "category" in item and item.get("category") in ["newsletter", "promotional"]:
                candidate_actions.append({
                    "action": "archive_email",
                    "target": f"email_{item.get('id')}",
                    "reason": "Automated newsletter archive recommendation"
                })

        return DecisionPlan(
            objective=user_request,
            subtasks=subtasks,
            required_context=required_context,
            candidate_actions=candidate_actions,
            confidence=confidence
        )
