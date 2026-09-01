import uuid
from typing import Dict, List, Optional
from personal_agent.goals.goal import Goal, Milestone, GOAL_ACTIVE, GOAL_ACHIEVED

class GoalManager:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}

    def create_goal(self, objective: str, priority: str = "NORMAL", parent_goal_id: Optional[str] = None) -> Goal:
        """Registers a new top-level or child Goal."""
        g_id = f"goal_{uuid.uuid4().hex[:8]}"
        goal = Goal(
            goal_id=g_id,
            objective=objective,
            priority=priority,
            parent_goal_id=parent_goal_id
        )
        self.goals[g_id] = goal
        return goal

    def add_milestone(self, goal_id: str, objective: str) -> Optional[Milestone]:
        """Adds a Milestone to an existing Goal."""
        goal = self.goals.get(goal_id)
        if not goal:
            return None

        m_id = f"m_{uuid.uuid4().hex[:6]}"
        milestone = Milestone(milestone_id=m_id, goal_id=goal_id, objective=objective)
        goal.milestones.append(milestone)
        return milestone

    def get_active_goals(self) -> List[Goal]:
        """Retrieves all currently active goals."""
        return [g for g in self.goals.values() if g.status in [GOAL_ACTIVE, "STALLED", "BLOCKED"]]
