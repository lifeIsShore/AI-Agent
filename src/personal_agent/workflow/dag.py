import os
import json
from typing import List, Dict, Any, Optional
from personal_agent.workflow.models import Workflow, WorkflowStep, STEP_PENDING, STEP_COMPLETED, WF_RUNNING, WF_COMPLETED

class WorkflowDAG:
    def get_ready_steps(self, workflow: Workflow) -> List[WorkflowStep]:
        """Returns steps whose dependencies are fully satisfied and status is PENDING."""
        completed_step_ids = {s.step_id for s in workflow.steps if s.status == STEP_COMPLETED}
        ready = []

        for step in workflow.steps:
            if step.status == STEP_PENDING:
                all_deps_met = all(dep in completed_step_ids for dep in step.dependencies)
                if all_deps_met:
                    ready.append(step)

        return ready

    def checkpoint_workflow(self, workflow: Workflow, checkpoint_dir: str = "data/state"):
        """Saves workflow checkpoint state to disk after step executions."""
        os.makedirs(checkpoint_dir, exist_ok=True)
        file_path = os.path.join(checkpoint_dir, f"wf_cp_{workflow.workflow_id}.json")
        
        data = {
            "workflow_id": workflow.workflow_id,
            "objective": workflow.objective,
            "status": workflow.status,
            "priority": workflow.priority,
            "steps": [
                {
                    "step_id": s.step_id,
                    "objective": s.objective,
                    "dependencies": s.dependencies,
                    "required_capabilities": s.required_capabilities,
                    "status": s.status,
                    "checkpoint": s.checkpoint,
                    "deadline": s.deadline,
                    "output_result": s.output_result
                } for s in workflow.steps
            ]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def restore_workflow_checkpoint(self, workflow_id: str, checkpoint_dir: str = "data/state") -> Optional[Workflow]:
        """Restores workflow checkpoint state from disk. Completed steps are preserved and never re-executed."""
        file_path = os.path.join(checkpoint_dir, f"wf_cp_{workflow_id}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            steps = []
            for sdata in data.get("steps", []):
                step = WorkflowStep(
                    step_id=sdata["step_id"],
                    objective=sdata["objective"],
                    dependencies=sdata.get("dependencies", []),
                    required_capabilities=sdata.get("required_capabilities", []),
                    status=sdata.get("status", STEP_PENDING),
                    checkpoint=sdata.get("checkpoint", True),
                    deadline=sdata.get("deadline"),
                    output_result=sdata.get("output_result")
                )
                steps.append(step)

            wf = Workflow(
                workflow_id=data["workflow_id"],
                objective=data["objective"],
                status=data.get("status", WF_RUNNING),
                priority=data.get("priority", "NORMAL"),
                steps=steps
            )
            return wf
        except Exception as e:
            print(f"[WorkflowDAG] Error restoring checkpoint for '{workflow_id}': {e}")
            return None
