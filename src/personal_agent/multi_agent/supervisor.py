import uuid
from typing import List, Dict, Any
from personal_agent.multi_agent.task import AgentTask, TASK_PENDING

class AgentSupervisor:
    def decompose_goal(self, goal: str, workflow_id: str) -> List[AgentTask]:
        """Decomposes top-level user goal into scoped specialist AgentTask contracts."""
        tasks = [
            AgentTask(
                task_id=f"task_inbox_{uuid.uuid4().hex[:6]}",
                workflow_id=workflow_id,
                parent_agent="AgentSupervisor",
                assigned_agent="InboxAgent",
                objective="Fetch, sanitize, and analyze unread inbox emails",
                required_capabilities=["gmail.read", "gmail.archive"],
                budget_tokens=2000
            ),
            AgentTask(
                task_id=f"task_cal_{uuid.uuid4().hex[:6]}",
                workflow_id=workflow_id,
                parent_agent="AgentSupervisor",
                assigned_agent="CalendarAgent",
                objective="Fetch calendar schedule and compute free slots",
                required_capabilities=["calendar.read", "calendar.create"],
                budget_tokens=1500
            ),
            AgentTask(
                task_id=f"task_tasks_{uuid.uuid4().hex[:6]}",
                workflow_id=workflow_id,
                parent_agent="AgentSupervisor",
                assigned_agent="TaskAgent",
                objective="Fetch outstanding todo tasks and prioritize focus items",
                required_capabilities=["tasks.read", "tasks.create"],
                budget_tokens=1000
            )
        ]
        return tasks
