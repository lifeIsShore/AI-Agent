import uuid
from typing import Dict, Any, List, Optional

class MissionStrategy:
    def __init__(
        self,
        strategy_id: str,
        name: str,
        objective: str,
        required_agents: List[str],
        preferred_models: List[str],
        task_sequence: List[str],
        expected_duration_hours: float,
        historical_success_rate: float = 0.85,
        confidence: float = 0.90
    ):
        self.strategy_id = strategy_id
        self.name = name
        self.objective = objective
        self.required_agents = required_agents
        self.preferred_models = preferred_models
        self.task_sequence = task_sequence
        self.expected_duration_hours = expected_duration_hours
        self.historical_success_rate = historical_success_rate
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "objective": self.objective,
            "required_agents": self.required_agents,
            "preferred_models": self.preferred_models,
            "task_sequence": self.task_sequence,
            "expected_duration_hours": self.expected_duration_hours,
            "historical_success_rate": self.historical_success_rate,
            "confidence": self.confidence
        }

class MissionStrategyLibrary:
    def __init__(self):
        self.strategies: Dict[str, MissionStrategy] = {}
        self._initialize_default_strategies()

    def _initialize_default_strategies(self):
        # Thesis Research Strategies
        self.register_strategy(MissionStrategy(
            "strat_thesis_a",
            "Strategy A — Direct Research & Draft",
            "Master Thesis Research & Drafting",
            ["ResearchSpecialist", "DocumentSpecialist"],
            ["Qwen 2.5 1.5B"],
            ["Research Literature", "Draft Proposal", "Review"],
            24.0,
            0.61,
            0.75
        ))
        self.register_strategy(MissionStrategy(
            "strat_thesis_b",
            "Strategy B — Requirements & Calendar Alignment",
            "Master Thesis Research with Calendar Integration",
            ["PlanningSpecialist", "ResearchSpecialist", "CalendarSpecialist", "DocumentSpecialist"],
            ["Qwen 2.5 1.5B", "Deterministic Rule Engine"],
            ["Requirements Analysis", "Deep Research", "Calendar Allocation", "Draft", "Review"],
            18.0,
            0.89,
            0.92
        ))
        self.register_strategy(MissionStrategy(
            "strat_thesis_c",
            "Strategy C — Iterative Critic & Dual Verification",
            "Master Thesis Literature Synthesis with Adversarial Critic",
            ["ResearchSpecialist", "CriticAgent", "VerificationAgent", "DocumentSpecialist"],
            ["Strong Cloud LLM", "Qwen 2.5 1.5B"],
            ["Deep Research", "Critic Challenge", "Contradiction Check", "Write", "Dual Verification"],
            16.0,
            0.86,
            0.95
        ))

    def register_strategy(self, strategy: MissionStrategy):
        self.strategies[strategy.strategy_id] = strategy

    def get_strategies_for_objective(self, objective_keyword: str) -> List[MissionStrategy]:
        return [
            s for s in self.strategies.values()
            if objective_keyword.lower() in s.objective.lower() or objective_keyword.lower() in s.name.lower()
        ]

class StrategySelector:
    def __init__(self, library: MissionStrategyLibrary):
        self.library = library

    def select_best_strategy(self, objective_keyword: str) -> Optional[MissionStrategy]:
        candidates = self.library.get_strategies_for_objective(objective_keyword)
        if not candidates:
            return None
        # Rank by historical_success_rate * confidence
        return max(candidates, key=lambda s: s.historical_success_rate * s.confidence)
