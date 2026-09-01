from typing import Tuple

ROUTE_QUEUE_BRIEFING = "QUEUE_FOR_BRIEFING"
ROUTE_INLINE_TOAST = "INLINE_TOAST"
ROUTE_URGENT_INTERRUPT = "URGENT_INTERRUPT"

class NotificationIntelligenceEngine:
    def determine_notification_routing(
        self,
        priority: str,
        is_user_busy: bool = False,
        current_hour: int = 14
    ) -> Tuple[str, str]:
        """Routes notification delivery mode based on priority, user activity state, and quiet hours."""
        is_night = (current_hour >= 22 or current_hour < 7)

        if priority == "P5":
            if is_night and not is_user_busy:
                return ROUTE_URGENT_INTERRUPT, "P5 Critical Alert overrides quiet hours."
            return ROUTE_URGENT_INTERRUPT, "P5 Critical Alert triggered immediate interrupt notification."

        if priority == "P4":
            if is_user_busy or is_night:
                return ROUTE_QUEUE_BRIEFING, "P4 Actionable item queued for briefing (User busy or quiet hours)."
            return ROUTE_INLINE_TOAST, "P4 Actionable notification delivered inline."

        if priority in ["P3", "P2"]:
            return ROUTE_QUEUE_BRIEFING, "Queued for morning/evening briefing digest."

        return ROUTE_QUEUE_BRIEFING, "Background item logged."
