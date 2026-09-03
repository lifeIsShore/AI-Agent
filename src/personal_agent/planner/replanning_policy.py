import time
from typing import Tuple, Optional
from personal_agent.events.event import (
    AgentEvent, EVENT_EMAIL_RECEIVED, EVENT_TASK_COMPLETED, EVENT_TASK_CREATED,
    EVENT_CALENDAR_UPDATED, EVENT_CALENDAR_CANCELLED, EVENT_GOAL_CHANGED, EVENT_DEADLINE_APPROACHING
)
from personal_agent.context.situation_model import CurrentSituation

class ReplanningPolicy:
    def __init__(self, min_replan_interval_sec: float = 2.0):
        self.min_replan_interval_sec = min_replan_interval_sec
        self.last_replan_timestamp: float = 0.0

    def should_replan(self, event: AgentEvent, situation: CurrentSituation) -> Tuple[bool, str]:
        """Evaluates whether an incoming event or situation delta materially warrants replanning."""
        now = time.time()
        payload = event.payload or {}
        subj = str(payload.get("subject", payload.get("title", ""))).lower()
        sender = str(payload.get("sender", "")).lower()

        # 1. Non-material event checks (Ignore marketing, newsletters, FYI)
        req_action = payload.get("requires_action", False)
        req_plan = payload.get("requires_planning", False)

        if event.event_type == EVENT_EMAIL_RECEIVED:
            if not req_action and not req_plan and not any(k in subj for k in ("urgent", "deadline", "cancel", "reschedule")):
                return False, "Irrelevant or low-priority email event; replanning ignored."

        # 2. Thrashing throttle check
        time_since_last = now - self.last_replan_timestamp
        is_urgent = (event.priority == "URGENT") or ("urgent" in subj) or (event.event_type == EVENT_DEADLINE_APPROACHING)
        
        if time_since_last < self.min_replan_interval_sec and not is_urgent:
            return False, f"Replanning throttled ({time_since_last:.1f}s since last replan < threshold {self.min_replan_interval_sec}s)."

        # 3. Material Change Triggers
        reasons = []

        if event.event_type == EVENT_TASK_COMPLETED:
            reasons.append("Task completed; re-evaluating dependent tasks")

        elif event.event_type in (EVENT_CALENDAR_UPDATED, EVENT_CALENDAR_CANCELLED):
            reasons.append("Calendar event changed/cancelled; schedule re-alignment needed")

        elif event.event_type == EVENT_DEADLINE_APPROACHING or "deadline" in subj:
            reasons.append("Approaching deadline detected; priority escalation needed")

        elif event.event_type == EVENT_GOAL_CHANGED:
            reasons.append("Goal status or priority updated; plan arbitration needed")

        elif req_action and req_plan:
            reasons.append(f"Actionable email received from '{sender or 'system'}'; planning required")

        elif any(k in subj for k in ("cancel", "reschedule", "room change", "conflict")):
            reasons.append("Schedule modification keyword detected")

        if reasons:
            self.last_replan_timestamp = now
            return True, "; ".join(reasons)

        return False, "No material change threshold met for replanning."
