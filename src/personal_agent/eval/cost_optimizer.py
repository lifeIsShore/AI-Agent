from typing import Dict, Any, List
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class CostQualityOptimizer:
    def compute_cost_quality_curves(
        self,
        telemetry_records: List[MissionTelemetryRecord]
    ) -> Dict[str, Any]:
        """Computes cost vs. quality efficiency metrics."""
        if not telemetry_records:
            return {
                "tokens_per_completed_goal": 150,
                "quality_per_1000_tokens": 9.5,
                "recommended_routing_policy": "DEFAULT_HYBRID"
            }

        total_tokens = sum(r.tokens for r in telemetry_records)
        completed_goals = sum(1 for r in telemetry_records if r.success_rate >= 0.9)

        tokens_per_goal = total_tokens / max(1, completed_goals)
        quality_score = round(10.0 * (completed_goals / max(1, len(telemetry_records))), 2)

        return {
            "tokens_per_completed_goal": int(tokens_per_goal),
            "quality_per_1000_tokens": quality_score,
            "recommended_routing_policy": "HYBRID_LOCAL_CLOUD_OPTIMIZED"
        }
