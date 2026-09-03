from typing import Dict, Any, Optional
from personal_agent.learning.mission_strategy_store import MissionStrategyStore

class StrategySelector:
    def select_best_strategy(
        self,
        domain: str,
        store: MissionStrategyStore
    ) -> Optional[Dict[str, Any]]:
        """Selects the highest-rated strategy template for new user goals."""
        candidates = store.get_strategies_for_domain(domain)
        if not candidates:
            return None

        candidates.sort(key=lambda s: (s.get("success_rate", 0.0), s.get("confidence", 0.0)), reverse=True)
        return candidates[0]
