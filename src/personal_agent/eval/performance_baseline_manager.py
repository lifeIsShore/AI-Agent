from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class PerformanceBaseline:
    baseline_id: str
    version: str = "v5.0.0"
    model_tier: str = "STRONG_LOCAL_LLM"
    specialist_id: str = "default"
    accuracy: float = 0.942
    false_urgency_rate: float = 0.011
    user_acceptance_rate: float = 0.870
    tokens_per_task: int = 820
    latency_sec: float = 2.4
    safety_violations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PerformanceBaselineManager:
    def __init__(self):
        self.baselines: Dict[str, PerformanceBaseline] = {
            "default": PerformanceBaseline("b_default"),
            "EmailSpecialist": PerformanceBaseline("b_email", specialist_id="EmailSpecialist"),
            "PlanningSpecialist": PerformanceBaseline("b_plan", specialist_id="PlanningSpecialist"),
            "ResearchSpecialist": PerformanceBaseline("b_res", specialist_id="ResearchSpecialist"),
            "BrowserSpecialist": PerformanceBaseline("b_brow", specialist_id="BrowserSpecialist")
        }

    def get_baseline(self, specialist_id: str = "default") -> PerformanceBaseline:
        return self.baselines.get(specialist_id, self.baselines["default"])

    def set_baseline(self, baseline: PerformanceBaseline):
        self.baselines[baseline.specialist_id] = baseline
