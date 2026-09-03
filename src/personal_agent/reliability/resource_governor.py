import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional, List

@dataclass
class ResourceBudget:
    max_llm_calls_hour: int = 100
    max_tokens_hour: int = 100_000
    max_concurrent_workflows: int = 3
    max_browser_sessions: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ResourceGovernor:
    def __init__(self, budget: Optional[ResourceBudget] = None):
        self.budget = budget or ResourceBudget()
        self.llm_calls_window: List[float] = []
        self.tokens_window: List[Tuple[float, int]] = []
        self.active_workflows_count: int = 0
        self.active_browser_sessions_count: int = 0

    def _cleanup_stale_window(self):
        now = time.time()
        one_hour_ago = now - 3600.0
        self.llm_calls_window = [t for t in self.llm_calls_window if t > one_hour_ago]
        self.tokens_window = [(t, count) for (t, count) in self.tokens_window if t > one_hour_ago]

    def can_consume_resource(
        self,
        resource_type: str,
        quantity: int = 1
    ) -> Tuple[bool, str]:
        """Validates resource availability against hard resource budgets."""
        self._cleanup_stale_window()

        res_clean = resource_type.lower()

        if res_clean == "llm_call":
            if len(self.llm_calls_window) + quantity > self.budget.max_llm_calls_hour:
                return False, f"Resource Governor EXHAUSTED: Hourly LLM call budget limit reached ({len(self.llm_calls_window)}/{self.budget.max_llm_calls_hour})."

        elif res_clean == "tokens":
            total_tokens = sum(c for _, c in self.tokens_window)
            if total_tokens + quantity > self.budget.max_tokens_hour:
                return False, f"Resource Governor EXHAUSTED: Hourly token budget limit reached ({total_tokens}/{self.budget.max_tokens_hour})."

        elif res_clean == "workflow":
            if self.active_workflows_count + quantity > self.budget.max_concurrent_workflows:
                return False, f"Resource Governor EXHAUSTED: Max concurrent workflows limit reached ({self.active_workflows_count}/{self.budget.max_concurrent_workflows})."

        elif res_clean == "browser_session":
            if self.active_browser_sessions_count + quantity > self.budget.max_browser_sessions:
                return False, f"Resource Governor EXHAUSTED: Max concurrent browser sessions limit reached ({self.active_browser_sessions_count}/{self.budget.max_browser_sessions})."

        return True, f"Resource Governor PERMITTED: Resource '{resource_type}' within budget."

    def record_usage(self, resource_type: str, quantity: int = 1):
        now = time.time()
        res_clean = resource_type.lower()
        if res_clean == "llm_call":
            for _ in range(quantity):
                self.llm_calls_window.append(now)
        elif res_clean == "tokens":
            self.tokens_window.append((now, quantity))
        elif res_clean == "workflow":
            self.active_workflows_count += quantity
        elif res_clean == "browser_session":
            self.active_browser_sessions_count += quantity

    def release_resource(self, resource_type: str, quantity: int = 1):
        res_clean = resource_type.lower()
        if res_clean == "workflow":
            self.active_workflows_count = max(0, self.active_workflows_count - quantity)
        elif res_clean == "browser_session":
            self.active_browser_sessions_count = max(0, self.active_browser_sessions_count - quantity)
