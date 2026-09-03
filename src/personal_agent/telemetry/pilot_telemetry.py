from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List

@dataclass
class MissionTelemetryRecord:
    mission_id: str
    duration_sec: float = 0.0
    decisions_count: int = 0
    llm_calls: int = 0
    tokens: int = 0
    tools_used: List[str] = field(default_factory=list)
    human_interventions: int = 0
    rejections: int = 0
    replans: int = 0
    success_rate: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RealWorldTelemetry:
    def __init__(self):
        self.records: List[MissionTelemetryRecord] = []

    def record_mission_telemetry(self, record: MissionTelemetryRecord):
        self.records.append(record)

    def get_summary_metrics(self) -> Dict[str, Any]:
        if not self.records:
            return {
                "total_missions": 0,
                "avg_duration_sec": 0.0,
                "total_llm_calls": 0,
                "total_tokens": 0,
                "human_intervention_rate": 0.0
            }

        total = len(self.records)
        avg_dur = sum(r.duration_sec for r in self.records) / total
        total_llm = sum(r.llm_calls for r in self.records)
        total_tokens = sum(r.tokens for r in self.records)
        interventions = sum(r.human_interventions for r in self.records)

        return {
            "total_missions": total,
            "avg_duration_sec": round(avg_dur, 2),
            "total_llm_calls": total_llm,
            "total_tokens": total_tokens,
            "human_intervention_rate": round(interventions / total, 2)
        }
