P0_IGNORE = "P0"
P1_BACKGROUND = "P1"
P2_INFORMATIONAL = "P2"
P3_ATTENTION = "P3"
P4_ACTION_RECOMMENDED = "P4"
P5_CRITICAL = "P5"

class EventPriorityEngine:
    def calculate_priority(self, importance: float, urgency: float, actionability: float) -> str:
        """Calculates priority level P0-P5 based on importance, urgency, and actionability."""
        composite_score = (importance * 0.45) + (urgency * 0.35) + (actionability * 0.20)

        if composite_score >= 0.85:
            return P5_CRITICAL
        elif composite_score >= 0.70:
            return P4_ACTION_RECOMMENDED
        elif composite_score >= 0.55:
            return P3_ATTENTION
        elif composite_score >= 0.40:
            return P2_INFORMATIONAL
        elif composite_score >= 0.25:
            return P1_BACKGROUND

        return P0_IGNORE
