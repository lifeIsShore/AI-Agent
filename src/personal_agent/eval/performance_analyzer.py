from typing import Dict, Any, List
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class AgentPerformanceAnalyzer:
    def analyze_performance(
        self,
        telemetry_records: List[MissionTelemetryRecord]
    ) -> Dict[str, Any]:
        """Analyzes quality metrics across Accuracy, Efficiency, and Usefulness dimensions."""
        if not telemetry_records:
            return {
                "accuracy_score": 1.0,
                "efficiency_tokens_per_mission": 0,
                "usefulness_intervention_rate": 0.0,
                "overall_performance_grade": "A+"
            }

        total = len(telemetry_records)
        avg_tokens = sum(r.tokens for r in telemetry_records) / total
        interventions = sum(r.human_interventions for r in telemetry_records)
        rejections = sum(r.rejections for r in telemetry_records)

        accuracy = 1.0 - (rejections / max(1, total))
        usefulness = 1.0 - (interventions / max(1, total))

        return {
            "accuracy_score": round(accuracy, 2),
            "efficiency_tokens_per_mission": int(avg_tokens),
            "usefulness_intervention_rate": round(interventions / total, 2),
            "overall_performance_grade": "A" if accuracy >= 0.9 else "B"
        }
