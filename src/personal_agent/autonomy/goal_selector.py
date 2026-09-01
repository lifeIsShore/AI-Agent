from typing import List, Optional, Tuple
from personal_agent.goals.goal import Goal, GOAL_ACTIVE, GOAL_STALLED

class GoalSelector:
    def select_next_goal(self, goals: List[Goal]) -> Tuple[Optional[Goal], str]:
        """Scores active goals balancing priority, progress momentum, and deadline urgency."""
        active = [g for g in goals if g.status in [GOAL_ACTIVE, GOAL_STALLED]]
        if not active:
            return None, "No active goals available for autonomous pursuit."

        def score_goal(g: Goal) -> float:
            prio_score = 100.0 if g.priority == "HIGH" else (50.0 if g.priority == "NORMAL" else 20.0)
            # Give boost to stalled goals to prevent starvation
            starvation_boost = 30.0 if g.status == GOAL_STALLED else 0.0
            progress_factor = (100.0 - g.progress_pct) * 0.2
            return prio_score + starvation_boost + progress_factor

        sorted_goals = sorted(active, key=score_goal, reverse=True)
        winner = sorted_goals[0]
        return winner, f"Selected Goal '{winner.objective}' (ID: {winner.goal_id}, Priority: {winner.priority}, Status: {winner.status})."
