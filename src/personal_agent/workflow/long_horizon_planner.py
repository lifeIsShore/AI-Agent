import uuid
from typing import List, Dict, Any, Tuple, Optional
from personal_agent.workflow.milestone_manager import MilestoneManager, MilestoneRecord
from personal_agent.workflow.models import Workflow, WorkflowStep, STEP_PENDING

class LongHorizonPlanner:
    def __init__(self, milestone_manager: Optional[MilestoneManager] = None):
        self.milestone_manager = milestone_manager or MilestoneManager()

    def decompose_goal_to_dag(
        self,
        goal_id: str,
        objective: str
    ) -> Tuple[List[MilestoneRecord], Workflow]:
        """Decomposes a multi-day/multi-week goal into milestones and a Workflow with steps."""
        # 1. Milestone 1: Requirements & Guidelines
        ms1 = self.milestone_manager.create_milestone(
            goal_id=goal_id,
            objective=f"Understand requirements for '{objective}'"
        )

        # 2. Milestone 2: Research & Literature Collection
        ms2 = self.milestone_manager.create_milestone(
            goal_id=goal_id,
            objective=f"Gather literature and materials for '{objective}'",
            dependencies=[ms1.milestone_id]
        )

        # 3. Milestone 3: Execution & Drafting
        ms3 = self.milestone_manager.create_milestone(
            goal_id=goal_id,
            objective=f"Draft primary deliverable for '{objective}'",
            dependencies=[ms2.milestone_id]
        )

        # 4. Milestone 4: Review & Final Submission
        ms4 = self.milestone_manager.create_milestone(
            goal_id=goal_id,
            objective=f"Review and finalize '{objective}'",
            dependencies=[ms3.milestone_id]
        )

        milestones = [ms1, ms2, ms3, ms4]

        # Construct Workflow
        s1 = WorkflowStep(step_id=ms1.milestone_id, objective=ms1.objective, status=STEP_PENDING)
        s2 = WorkflowStep(step_id=ms2.milestone_id, objective=ms2.objective, dependencies=[ms1.milestone_id], status=STEP_PENDING)
        s3 = WorkflowStep(step_id=ms3.milestone_id, objective=ms3.objective, dependencies=[ms2.milestone_id], status=STEP_PENDING)
        s4 = WorkflowStep(step_id=ms4.milestone_id, objective=ms4.objective, dependencies=[ms3.milestone_id], status=STEP_PENDING)

        wf = Workflow(
            workflow_id=f"wf_{goal_id}",
            objective=objective,
            steps=[s1, s2, s3, s4]
        )

        return milestones, wf
