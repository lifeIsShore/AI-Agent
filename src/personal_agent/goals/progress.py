from typing import List, Dict, Any
from personal_agent.goals.goal import Goal, GOAL_STALLED, GOAL_ACHIEVED

class GoalProgressEngine:
    def update_goal_progress(self, goal: Goal, completed_milestone_id: str = None):
        """Updates progress percentage based on completed milestones."""
        if completed_milestone_id:
            for m in goal.milestones:
                if m.milestone_id == completed_milestone_id:
                    m.status = "COMPLETED"

        if goal.milestones:
            completed = sum(1 for m in goal.milestones if m.status == "COMPLETED")
            goal.progress_pct = round((completed / len(goal.milestones)) * 100.0, 1)
            if goal.progress_pct >= 100.0:
                goal.status = GOAL_ACHIEVED

    def detect_stalled_goals(self, goals: List[Goal]) -> List[Dict[str, Any]]:
        """Identifies stalled goals and generates recovery recommendations."""
        stalled_reports = []
        for g in goals:
            if g.status in ["ACTIVE", GOAL_STALLED] and g.progress_pct <= 50.0:
                g.status = GOAL_STALLED
                stalled_reports.append({
                    "goal_id": g.goal_id,
                    "objective": g.objective,
                    "reason": "Incomplete milestones and no progress recorded in last execution cycle",
                    "recommended_recovery_action": f"Schedule focus workflow block for '{g.objective}'"
                })
        return stalled_reports
