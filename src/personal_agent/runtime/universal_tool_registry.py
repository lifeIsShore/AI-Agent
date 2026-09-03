from typing import Dict, Any, List, Optional

class UniversalToolRegistry:
    def __init__(self):
        self.agent_tool_mappings = {
            "CodingAgent": ["repository.read", "repository.search", "file.patch", "git.diff", "test.run", "git.commit", "git.push"],
            "ResearchAgent": ["web.search", "paper.fetch", "source.verify", "artifact.create"],
            "DataAnalysisAgent": ["dataset.inspect", "python.execute", "dataframe.transform", "chart.create"],
            "WritingAgent": ["document.read", "document.write", "artifact.create"],
            "FinanceAgent": ["financial_data.read", "calculation.execute", "memo.create"]
        }
        self.restricted_tools = {"git.push", "production.deploy", "database.drop"}

    def is_tool_registered_for_agent(self, agent_id: str, tool_name: str) -> bool:
        allowed_tools = self.agent_tool_mappings.get(agent_id, [])
        return tool_name in allowed_tools

    def evaluate_tool_authority(self, agent_id: str, tool_name: str) -> Dict[str, Any]:
        """Enforces Capability != Authority by verifying tool registration and governor restrictions."""
        is_registered = self.is_tool_registered_for_agent(agent_id, tool_name)
        is_restricted = tool_name in self.restricted_tools

        if not is_registered:
            return {"authorized": False, "reason": f"Tool '{tool_name}' not registered for agent '{agent_id}'", "status": "DENIED"}

        if is_restricted:
            return {"authorized": False, "reason": f"Tool '{tool_name}' requires human approval", "status": "PENDING_HUMAN_APPROVAL"}

        return {"authorized": True, "reason": f"Authorized for {agent_id}", "status": "APPROVED"}
