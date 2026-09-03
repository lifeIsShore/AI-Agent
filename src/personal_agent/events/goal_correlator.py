from typing import List, Dict, Any, Tuple, Optional
from personal_agent.events.event import AgentEvent
from personal_agent.goals.goal import Goal, GOAL_ACTIVE, GOAL_STALLED

class EventGoalCorrelator:
    def __init__(self, goal_manager: Optional[Any] = None, world_model: Optional[Any] = None):
        self.goal_manager = goal_manager
        self.world_model = world_model

    def correlate_event_to_goals(
        self,
        event: AgentEvent,
        goals: List[Goal]
    ) -> List[Tuple[Goal, str, float]]:
        """Correlates an incoming event with active Goal objects and returns correlation results."""
        correlations: List[Tuple[Goal, str, float]] = []
        if not goals:
            return correlations

        payload_str = str(event.payload).lower()
        event_type = event.event_type.upper()
        sender = str(event.payload.get("sender", "")).lower()
        subject = str(event.payload.get("subject", "")).lower()

        for goal in goals:
            if goal.status not in (GOAL_ACTIVE, GOAL_STALLED):
                continue

            goal_text = f"{goal.objective} {' '.join(goal.constraints)}".lower()
            correlation_score = 0.0
            reasons = []

            # 1. Direct Goal ID match in payload
            if event.payload.get("goal_id") == goal.goal_id or event.entity_id == goal.goal_id:
                correlation_score += 1.0
                reasons.append(f"Direct goal ID match '{goal.goal_id}'")

            # Check keyword associations (e.g. thesis, advisor, exam, project)
            keywords = [w for w in goal.objective.lower().split() if len(w) > 3]
            matched_keywords = [w for w in keywords if w in payload_str or w in subject]
            if matched_keywords:
                correlation_score += 0.4 * len(matched_keywords)
                reasons.append(f"Keyword match ({', '.join(matched_keywords)})")

            # High-priority sender / deadline correlation
            if any(k in sender for k in ("prof", "advisor", "bank")) and correlation_score > 0:
                correlation_score += 0.3
                reasons.append("High-authority sender context")

            if correlation_score > 0.0:
                reason_msg = "; ".join(reasons)
                correlations.append((goal, reason_msg, round(correlation_score, 2)))

                # Dynamically boost goal priority if correlation is strong
                if correlation_score >= 0.7:
                    if goal.priority == "NORMAL":
                        goal.priority = "HIGH"
                    elif goal.priority == "HIGH" and ("urgent" in subject or "deadline" in payload_str):
                        goal.priority = "URGENT"

        # Sort by correlation score descending
        correlations.sort(key=lambda x: x[2], reverse=True)
        return correlations
