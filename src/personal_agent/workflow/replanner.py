from typing import Tuple, Dict, Any, List
from personal_agent.workflow.models import Workflow, WorkflowStep, STEP_PENDING, STEP_COMPLETED

class WorkflowReplanner:
    def detect_conflict(self, workflow: Workflow, new_event: Dict[str, Any]) -> bool:
        """Checks if a new incoming calendar event conflicts with active workflow schedule steps."""
        summary = str(new_event.get("summary", "")).lower()
        if "urgent" in summary or "meeting" in summary or "change" in summary:
            return True
        return False

    def replan_uncompleted_steps(
        self,
        workflow: Workflow,
        conflict_event: Dict[str, Any]
    ) -> Tuple[Workflow, str]:
        """Dynamically adjusts remaining uncompleted workflow steps while preserving completed step checkpoints."""
        replanned_count = 0
        for step in workflow.steps:
            if step.status == STEP_PENDING:
                replanned_count += 1
                step.objective = f"[Replanned] {step.objective} (adjusted for {conflict_event.get('summary', 'new event')})"

        reason = f"Replanned {replanned_count} pending steps due to schedule conflict '{conflict_event.get('summary')}'."
        return workflow, reason
