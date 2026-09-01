from typing import Dict, Any, List, Optional, Tuple
from personal_agent.workflow.models import (
    Workflow, WorkflowStep, WF_CREATED, WF_RUNNING, WF_WAITING_APPROVAL,
    WF_VERIFYING, WF_COMPLETED, WF_FAILED, WF_PAUSED, WF_CANCELLED, STEP_PENDING, STEP_COMPLETED
)
from personal_agent.workflow.dag import WorkflowDAG

WF_WAITING_RESOURCE = "WAITING_RESOURCE"
WF_RECOVERING = "RECOVERING"
WF_REPLANNING = "REPLANNING"

class WorkflowCoordinator:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.dag = WorkflowDAG()

    def register_workflow(self, workflow: Workflow):
        self.workflows[workflow.workflow_id] = workflow

    def determine_next_action(self, workflow_id: str) -> Tuple[str, List[WorkflowStep]]:
        """Determines next execution action deterministically."""
        wf = self.workflows.get(workflow_id)
        if not wf:
            return "WORKFLOW_NOT_FOUND", []

        if wf.status in [WF_COMPLETED, WF_FAILED, WF_CANCELLED, WF_PAUSED]:
            return f"TERMINAL_{wf.status}", []

        ready_steps = self.dag.get_ready_steps(wf)
        if ready_steps:
            return "EXECUTE_PARALLEL_STEPS", ready_steps

        all_completed = all(s.status == STEP_COMPLETED for s in wf.steps)
        if all_completed:
            wf.update_status(WF_COMPLETED)
            return "WORKFLOW_COMPLETED", []

        return "WAITING_DEPENDENCIES", []

    def cancel_workflow(self, workflow_id: str, reason: str = "User cancellation request") -> Tuple[bool, str]:
        """Cancels target workflow without disrupting other active running workflows."""
        wf = self.workflows.get(workflow_id)
        if not wf:
            return False, f"Workflow '{workflow_id}' not found."

        if wf.status in [WF_COMPLETED, WF_CANCELLED]:
            return False, f"Workflow '{workflow_id}' is already in terminal state '{wf.status}'."

        wf.update_status(WF_CANCELLED)
        return True, f"Workflow '{workflow_id}' cancelled cleanly: {reason}."
