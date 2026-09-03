from typing import Dict, Any, List

class MissionStrategyStore:
    def __init__(self):
        self.strategies: Dict[str, Dict[str, Any]] = {
            "strat_thesis_b": {
                "strategy_id": "strat_thesis_b",
                "domain": "university_deadline",
                "name": "Strategy B: Requirements -> Research -> Calendar -> Write -> Review",
                "step_sequence": ["Requirements", "Research", "Calendar", "Write", "Review"],
                "success_rate": 0.89,
                "confidence": 0.95
            },
            "strat_thesis_a": {
                "strategy_id": "strat_thesis_a",
                "domain": "university_deadline",
                "name": "Strategy A: Research -> Write -> Review",
                "step_sequence": ["Research", "Write", "Review"],
                "success_rate": 0.61,
                "confidence": 0.70
            }
        }

    def save_strategy(self, strategy: Dict[str, Any]):
        sid = strategy.get("strategy_id", "strat_custom")
        self.strategies[sid] = strategy

    def get_strategies_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        return [s for s in self.strategies.values() if s.get("domain", "").lower() == domain.lower()]
