from typing import Dict, Any, List
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class ContinuousEvaluationEngine:
    def evaluate_telemetry_stream(
        self,
        telemetry_records: List[MissionTelemetryRecord]
    ) -> Dict[str, Any]:
        """Runs continuous evaluation over live telemetry streams."""
        if not telemetry_records:
            return {
                "eval_status": "NO_DATA",
                "sample_size": 0,
                "current_accuracy": 1.0,
                "current_user_acceptance": 1.0,
                "avg_tokens_per_task": 0
            }

        total = len(telemetry_records)
        rejections = sum(r.rejections for r in telemetry_records)
        tokens = sum(r.tokens for r in telemetry_records)
        interventions = sum(r.human_interventions for r in telemetry_records)

        accuracy = 1.0 - (rejections / max(1, total))
        user_acceptance = 1.0 - (interventions / max(1, total))
        avg_tokens = tokens / max(1, total)

        return {
            "eval_status": "EVALUATED",
            "sample_size": total,
            "current_accuracy": round(accuracy, 3),
            "current_user_acceptance": round(user_acceptance, 3),
            "avg_tokens_per_task": int(avg_tokens)
        }
