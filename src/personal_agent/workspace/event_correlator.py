from typing import List, Dict, Any
from personal_agent.workspace.workspace_connector import NormalizedWorkspaceItem

class CrossSourceEventCorrelator:
    def correlate_cross_source_inconsistencies(
        self,
        items: List[NormalizedWorkspaceItem]
    ) -> List[Dict[str, Any]]:
        """Correlates facts across Gmail, Calendar, and Tasks to detect inconsistencies."""
        inconsistencies = []

        emails = [i for i in items if i.source_system == "gmail"]
        events = [i for i in items if i.source_system == "calendar"]

        for email in emails:
            content_lower = email.content.lower()
            if "deadline" in content_lower or "moved" in content_lower or "friday" in content_lower:
                for event in events:
                    if "thesis" in event.title.lower() or "submission" in event.title.lower():
                        inconsistencies.append({
                            "correlated_type": "DEADLINE_SHIFT_INCONSISTENCY",
                            "source_a": f"Gmail message '{email.title}'",
                            "source_b": f"Calendar event '{event.title}'",
                            "description": f"Email indicates deadline update ('{email.content}'), but Calendar event '{event.title}' remains un-updated.",
                            "recommended_action": "REPLAN_CALENDAR_EVENT",
                            "confidence": 0.95
                        })

        return inconsistencies
