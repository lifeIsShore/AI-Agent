from typing import List, Optional
from personal_agent.multi_agent.agent_registry import AgentRegistry, AgentSpecialistProfile

class AgentRouter:
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()

    def route_task(
        self,
        task_description: str,
        required_capabilities: Optional[List[str]] = None
    ) -> List[AgentSpecialistProfile]:
        """Routes task/goal to single or collaborating team of specialist agents."""
        matched: List[AgentSpecialistProfile] = []
        task_clean = task_description.lower()

        # 1. Match by explicit required capabilities
        if required_capabilities:
            for cap in required_capabilities:
                agents = self.registry.get_agents_by_capability(cap)
                for a in agents:
                    if a not in matched:
                        matched.append(a)

        # 2. Match by keyword semantics
        if "email" in task_clean or "gmail" in task_clean or "inbox" in task_clean:
            a = self.registry.get_agent("EmailSpecialist")
            if a and a not in matched:
                matched.append(a)

        if "browse" in task_clean or "web" in task_clean or "url" in task_clean or "portal" in task_clean:
            a = self.registry.get_agent("BrowserSpecialist")
            if a and a not in matched:
                matched.append(a)

        if "research" in task_clean or "paper" in task_clean or "literature" in task_clean or "rag" in task_clean:
            a = self.registry.get_agent("ResearchSpecialist")
            if a and a not in matched:
                matched.append(a)

        if "calendar" in task_clean or "schedule" in task_clean or "meeting" in task_clean:
            a = self.registry.get_agent("CalendarSpecialist")
            if a and a not in matched:
                matched.append(a)

        if "plan" in task_clean or "thesis" in task_clean or "milestone" in task_clean:
            a = self.registry.get_agent("PlanningSpecialist")
            if a and a not in matched:
                matched.append(a)

        # Fallback to PlanningSpecialist if no matches found
        if not matched:
            fallback = self.registry.get_agent("PlanningSpecialist")
            if fallback:
                matched.append(fallback)

        return matched
