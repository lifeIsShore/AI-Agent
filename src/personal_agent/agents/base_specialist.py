from typing import Dict, Any, List, Optional

class SpecialistAgent:
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        capabilities: List[str],
        tools: List[str],
        preferred_models: List[str],
        autonomy_cap: str = "BOUNDED_AUTO"
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.tools = tools
        self.preferred_models = preferred_models
        self.autonomy_cap = autonomy_cap

    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Base execution interface to be overridden by specialized agents."""
        return {
            "agent_id": self.agent_id,
            "status": "COMPLETED",
            "output": f"Executed by {self.name}",
            "provenance_id": f"fact_{self.agent_id}_exec"
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "preferred_models": self.preferred_models,
            "autonomy_cap": self.autonomy_cap
        }

class AgentCapabilityRegistry:
    def __init__(self):
        self.registry: Dict[str, List[str]] = {}

    def register_agent_capabilities(self, agent_id: str, capabilities: List[str]):
        self.registry[agent_id] = capabilities

    def find_agents_by_capability(self, capability: str) -> List[str]:
        return [agent_id for agent_id, caps in self.registry.items() if capability in caps]
