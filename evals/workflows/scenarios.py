from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class WorkflowScenario:
    scenario_id: str
    description: str
    objective: str
    step_count: int
    expected_completion: bool

WORKFLOW_SCENARIOS: List[WorkflowScenario] = [
    WorkflowScenario(
        scenario_id="wf_sc_01_study_plan",
        description="Multi-step university study preparation DAG workflow",
        objective="Prepare weekly university study plan",
        step_count=4,
        expected_completion=True
    ),
    WorkflowScenario(
        scenario_id="wf_sc_02_replanning",
        description="Dynamic replanning under calendar schedule conflict",
        objective="Replan daily schedule post urgent lecture conflict",
        step_count=3,
        expected_completion=True
    )
]
