from typing import Dict, Any, Tuple

class AgentBudgetManager:
    def __init__(self):
        self.budgets: Dict[str, Dict[str, Any]] = {
            "InboxAgent": {"max_tokens": 2000, "used_tokens": 0, "max_cost": 0.01},
            "CalendarAgent": {"max_tokens": 1500, "used_tokens": 0, "max_cost": 0.005},
            "TaskAgent": {"max_tokens": 1000, "used_tokens": 0, "max_cost": 0.005}
        }

    def consume_agent_tokens(self, agent_name: str, tokens: int) -> Tuple[bool, str]:
        """Consumes tokens for an agent and checks against per-agent sub-budget limit."""
        b = self.budgets.get(agent_name)
        if not b:
            return True, f"No specific sub-budget defined for '{agent_name}'."

        if b["used_tokens"] + tokens > b["max_tokens"]:
            return False, f"Agent Budget Exceeded: '{agent_name}' requested {tokens} tokens (Limit: {b['max_tokens']})."

        b["used_tokens"] += tokens
        return True, f"Agent '{agent_name}' consumed {tokens} tokens (Used: {b['used_tokens']}/{b['max_tokens']})."
