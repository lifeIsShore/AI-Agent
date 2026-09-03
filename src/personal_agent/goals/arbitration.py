from typing import List, Dict, Tuple, Optional
from personal_agent.goals.goal import Goal, GOAL_ACTIVE, GOAL_STALLED

PRIORITY_WEIGHTS = {
    "URGENT": 10.0,
    "HIGH": 7.0,
    "NORMAL": 4.0,
    "LOW": 2.0
}

class GoalArbitrator:
    def __init__(self, starvation_increment: float = 1.0):
        self.starvation_increment = starvation_increment
        self.unprocessed_cycles: Dict[str, int] = {}

    def score_goal(self, goal: Goal) -> float:
        """Computes priority score for a goal including starvation boost."""
        base_score = PRIORITY_WEIGHTS.get(goal.priority.upper(), 4.0)
        cycles = self.unprocessed_cycles.get(goal.goal_id, 0)
        starvation_boost = cycles * self.starvation_increment
        deadline_boost = 3.0 if goal.deadline else 0.0
        stalled_boost = 2.0 if goal.status == GOAL_STALLED else 0.0

        return base_score + starvation_boost + deadline_boost + stalled_boost

    def select_prioritized_goals(self, goals: List[Goal]) -> List[Tuple[Goal, float]]:
        """Arbitrates and orders goals by score, incrementing starvation counters for unselected goals."""
        active_goals = [g for g in goals if g.status in (GOAL_ACTIVE, GOAL_STALLED)]
        if not active_goals:
            return []

        scored = [(g, self.score_goal(g)) for g in active_goals]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Selected top goal gets cycle count reset; unselected goals get incremented
        top_goal = scored[0][0]
        self.unprocessed_cycles[top_goal.goal_id] = 0

        for g, _ in scored[1:]:
            self.unprocessed_cycles[g.goal_id] = self.unprocessed_cycles.get(g.goal_id, 0) + 1

        return scored
