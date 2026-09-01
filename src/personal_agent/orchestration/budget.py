from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class WorkflowBudget:
    max_tokens: int = 20000
    max_cost_eur: float = 0.10
    max_runtime_sec: float = 120.0
    max_tool_calls: int = 30
    max_retries: int = 5
    
    current_tokens: int = 0
    current_cost_eur: float = 0.0
    current_runtime_sec: float = 0.0
    current_tool_calls: int = 0

    def record_usage(self, tokens: int = 0, cost: float = 0.0, runtime: float = 0.0, tool_calls: int = 1) -> Tuple[bool, str]:
        """Tracks usage and enforces workflow resource budget limits."""
        self.current_tokens += tokens
        self.current_cost_eur += cost
        self.current_runtime_sec += runtime
        self.current_tool_calls += tool_calls

        if self.current_tokens > self.max_tokens:
            return False, f"SAFE_STOP: Token budget exceeded ({self.current_tokens} > {self.max_tokens})."
        if self.current_cost_eur > self.max_cost_eur:
            return False, f"SAFE_STOP: Cost budget exceeded (€{self.current_cost_eur:.4f} > €{self.max_cost_eur:.2f})."
        if self.current_runtime_sec > self.max_runtime_sec:
            return False, f"SAFE_STOP: Runtime budget exceeded ({self.current_runtime_sec:.1f}s > {self.max_runtime_sec:.1f}s)."
        if self.current_tool_calls > self.max_tool_calls:
            return False, f"SAFE_STOP: Tool call limit exceeded ({self.current_tool_calls} > {self.max_tool_calls})."

        return True, "Within budget limits."
