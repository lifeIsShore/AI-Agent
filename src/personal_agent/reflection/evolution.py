from typing import Dict, Any
from personal_agent.reflection.engine import ReflectionRecord
from personal_agent.learning.strategy_store import ExecutionStrategyStore

class StrategyEvolutionEngine:
    def evolve_strategy(
        self,
        strategy_name: str,
        reflection: ReflectionRecord,
        strategy_store: ExecutionStrategyStore
    ) -> Dict[str, Any]:
        """Evolves strategy confidence parameters based on reflection records."""
        is_success = (reflection.expected_outcome == reflection.actual_outcome)
        strategy_store.update_strategy_outcome(strategy_name, success=is_success)
        strat = strategy_store.get_preferred_strategy(strategy_name)

        return {
            "strategy_name": strategy_name,
            "success_rate_pct": strat.success_rate_pct if strat else 100.0,
            "evidence_count": strat.evidence_count if strat else 1,
            "evolution_applied": True
        }
