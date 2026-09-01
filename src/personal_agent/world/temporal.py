from datetime import datetime, timezone

TEMP_BEFORE = "BEFORE"
TEMP_AFTER = "AFTER"
TEMP_OVERLAPS = "OVERLAPS"
TEMP_DEADLINE_APPROACHING = "APPROACHING"
TEMP_EXPIRED = "EXPIRED"

class TemporalReasoningEngine:
    def evaluate_temporal_status(self, timestamp_iso: str) -> str:
        """Evaluates temporal relationship status relative to current timestamp."""
        try:
            target_dt = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            delta_hours = (target_dt - now_dt).total_seconds() / 3600.0

            if delta_hours < 0:
                return TEMP_EXPIRED
            elif delta_hours <= 48:
                return TEMP_DEADLINE_APPROACHING

            return TEMP_BEFORE
        except Exception:
            return TEMP_BEFORE
