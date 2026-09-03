import uuid
from typing import Dict, Any, List, Optional
from personal_agent.multi_agent.agent_registry import AgentRegistry

class MissionTeam:
    def __init__(self, team_name: str, registry: Optional[AgentRegistry] = None):
        self.team_id = f"team_{uuid.uuid4().hex[:8]}"
        self.team_name = team_name
        self.registry = registry or AgentRegistry()
        self.members: List[Dict[str, Any]] = [
            {"agent_id": "ResearchSpecialist", "role": "RESEARCHER"},
            {"agent_id": "PlanningSpecialist", "role": "PLANNER"},
            {"agent_id": "EmailSpecialist", "role": "COMMUNICATOR"},
            {"agent_id": "CriticAgent", "role": "CRITIC"},
            {"agent_id": "VerificationAgent", "role": "VERIFIER"}
        ]

    def get_team_members(self) -> List[Dict[str, Any]]:
        return self.members

    def get_agent_by_role(self, role: str) -> Optional[Dict[str, Any]]:
        for m in self.members:
            if m.get("role", "").upper() == role.upper():
                return m
        return None
