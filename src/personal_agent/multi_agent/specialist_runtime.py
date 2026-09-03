from typing import Tuple, Dict, Any, Optional
from personal_agent.multi_agent.agent_registry import AgentSpecialistProfile

class SpecialistRuntime:
    def can_execute_tool(
        self,
        profile: AgentSpecialistProfile,
        tool_name: str
    ) -> Tuple[bool, str]:
        """Validates tool execution against specialist's strict tool white-list."""
        if tool_name not in profile.allowed_tools:
            return False, (
                f"Specialist Execution BLOCKED: Tool '{tool_name}' is not in the allowed tool "
                f"white-list for agent '{profile.agent_id}' ({profile.allowed_tools})."
            )

        return True, f"Tool '{tool_name}' permitted for specialist '{profile.agent_id}'."

    def execute_specialist_task(
        self,
        profile: AgentSpecialistProfile,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executes tool action within constrained specialist environment."""
        permitted, reason = self.can_execute_tool(profile, tool_name)
        if not permitted:
            return {
                "status": "BLOCKED",
                "agent_id": profile.agent_id,
                "tool": tool_name,
                "reason": reason
            }

        return {
            "status": "SUCCESS",
            "agent_id": profile.agent_id,
            "tool": tool_name,
            "args": tool_args,
            "output": f"Specialist '{profile.agent_id}' executed tool '{tool_name}' successfully."
        }
