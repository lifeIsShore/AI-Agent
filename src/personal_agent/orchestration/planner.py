import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from personal_agent.orchestration.roles import (
    ROLE_INBOX_ANALYST, ROLE_CALENDAR_PLANNER, ROLE_TASK_PLANNER, ROLE_EXECUTION_COORDINATOR
)

@dataclass
class ExecutionPlan:
    plan_id: str
    objective: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    parallel_groups: List[List[str]] = field(default_factory=list)
    expected_cost: float = 0.002
    expected_latency_ms: int = 450
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ExecutionPlanner:
    def create_execution_plan(self, user_request: str) -> ExecutionPlan:
        """Decomposes user objective into structured execution steps with role assignments and parallel groups."""
        plan_id = f"eplan_{uuid.uuid4().hex[:8]}"

        steps = [
            {
                "step_id": "step_fetch_gmail",
                "objective": "Read Gmail inbox unread items",
                "role": ROLE_INBOX_ANALYST,
                "required_capability": "gmail.read",
                "dependencies": []
            },
            {
                "step_id": "step_fetch_calendar",
                "objective": "Read Calendar schedule and free slots",
                "role": ROLE_CALENDAR_PLANNER,
                "required_capability": "calendar.read",
                "dependencies": []
            },
            {
                "step_id": "step_fetch_tasks",
                "objective": "Read pending task list",
                "role": ROLE_TASK_PLANNER,
                "required_capability": "tasks.read",
                "dependencies": []
            },
            {
                "step_id": "step_coordinate_plan",
                "objective": "Synthesize schedule and generate action proposals",
                "role": ROLE_EXECUTION_COORDINATOR,
                "required_capability": "calendar.create",
                "dependencies": ["step_fetch_gmail", "step_fetch_calendar", "step_fetch_tasks"]
            }
        ]

        parallel_groups = [
            ["step_fetch_gmail", "step_fetch_calendar", "step_fetch_tasks"],
            ["step_coordinate_plan"]
        ]

        return ExecutionPlan(
            plan_id=plan_id,
            objective=user_request,
            steps=steps,
            parallel_groups=parallel_groups,
            expected_cost=0.0025,
            expected_latency_ms=450
        )
