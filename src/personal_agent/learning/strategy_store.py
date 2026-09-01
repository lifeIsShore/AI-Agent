import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ExecutionStrategy:
    strategy_id: str
    objective: str
    context_type: str
    success_rate_pct: float = 100.0
    evidence_count: int = 1
    preferred_parameters: Dict[str, Any] = field(default_factory=dict)

class ExecutionStrategyStore:
    def __init__(self):
        self.strategies: Dict[str, ExecutionStrategy] = {}

    def get_or_create_strategy(self, objective: str, context_type: str = "general") -> ExecutionStrategy:
        strat = self.strategies.get(objective)
        if not strat:
            strat = ExecutionStrategy(
                strategy_id=f"strat_{uuid.uuid4().hex[:8]}",
                objective=objective,
                context_type=context_type
            )
            self.strategies[objective] = strat
        return strat

    def update_strategy_outcome(self, objective: str, success: bool, used_parameters: Dict[str, Any] = None):
        """Updates learned strategy evidence counters and success percentage."""
        strat = self.get_or_create_strategy(objective)
        strat.evidence_count += 1

        if used_parameters:
            strat.preferred_parameters.update(used_parameters)

        if success:
            strat.success_rate_pct = min(100.0, strat.success_rate_pct + 1.5)
        else:
            strat.success_rate_pct = max(0.0, strat.success_rate_pct - 5.0)

    def get_preferred_strategy(self, objective: str) -> Optional[ExecutionStrategy]:
        """Returns preferred strategy recommendation for future execution planning."""
        return self.strategies.get(objective)
