from typing import List, Dict, Any, Tuple
from personal_agent.multi_agent.task import AgentTask, TASK_COMPLETED, TASK_FAILED

class BaseSpecialistAgent:
    def __init__(self, agent_name: str, allowed_capabilities: List[str]):
        self.agent_name = agent_name
        self.allowed_capabilities = set(allowed_capabilities)

    def is_capability_allowed(self, capability: str) -> bool:
        return capability in self.allowed_capabilities

    def execute_task_capability(
        self,
        capability: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Executes a capability while enforcing strict capability isolation boundaries."""
        if not self.is_capability_allowed(capability):
            return False, f"Capability Violation: '{self.agent_name}' is NOT authorized for capability '{capability}'.", {}
        
        return True, f"Capability '{capability}' executed successfully by '{self.agent_name}'.", {"status": "ok"}

class InboxAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__("InboxAgent", ["gmail.read", "gmail.archive"])

class CalendarAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__("CalendarAgent", ["calendar.read", "calendar.create"])

class TaskAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__("TaskAgent", ["tasks.read", "tasks.create"])
