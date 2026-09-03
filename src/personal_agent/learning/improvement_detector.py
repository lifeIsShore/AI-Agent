from typing import Dict, Any, List
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class ImprovementDetector:
    def detect_weaknesses(
        self,
        telemetry_records: List[MissionTelemetryRecord]
    ) -> List[Dict[str, Any]]:
        """Identifies empirical performance weaknesses from telemetry history."""
        weaknesses = []

        if not telemetry_records:
            return weaknesses

        total = len(telemetry_records)
        rejections = sum(r.rejections for r in telemetry_records)
        tokens_sum = sum(r.tokens for r in telemetry_records)

        # 1. High User Rejection Weakness
        if (rejections / max(1, total)) > 0.2:
            weaknesses.append({
                "weakness_type": "HIGH_USER_REJECTION",
                "affected_component": "PlanningSpecialist",
                "metric_value": round(rejections / total, 2),
                "threshold": 0.2,
                "evidence": f"User rejected {rejections} out of {total} proposed actions."
            })

        # 2. Token Inefficiency Weakness
        if (tokens_sum / max(1, total)) > 500:
            weaknesses.append({
                "weakness_type": "TOKEN_INEFFICIENCY",
                "affected_component": "ResearchSpecialist",
                "metric_value": int(tokens_sum / total),
                "threshold": 500,
                "evidence": f"Average token consumption is {int(tokens_sum / total)} tokens/mission."
            })

        return weaknesses
