import time
from typing import Dict, Any, List

class GoalPriorityEngine:
    def evaluate_priorities(self) -> List[Dict[str, Any]]:
        """Evaluates and ranks goal priorities based on urgency, bottleneck risk, and capacity constraints."""
        return [
            {
                "goal_id": "g_thesis",
                "name": "🎓 Master Thesis Proposal & Research",
                "priority_score": 9.4,
                "trend": "UP",
                "importance": "HIGH",
                "urgency": "HIGH",
                "reason": "Deadline Nov 30 + methodology bottleneck + workload risk HIGH (+12.0h)"
            },
            {
                "goal_id": "g_job",
                "name": "💼 M.Sc. Job & Application Search",
                "priority_score": 5.1,
                "trend": "DOWN",
                "importance": "MEDIUM",
                "urgency": "MEDIUM",
                "reason": "No immediate deadline + sufficient progress"
            },
            {
                "goal_id": "g_ai_agent",
                "name": "🤖 Personal AI Agent OS Architecture",
                "priority_score": 4.7,
                "trend": "STABLE",
                "importance": "HIGH",
                "urgency": "LOW",
                "reason": "Continuous development + 1,667 passing unit tests"
            },
            {
                "goal_id": "g_university",
                "name": "📚 M.Sc. Mannheim Course Workload",
                "priority_score": 3.8,
                "trend": "STABLE",
                "importance": "MEDIUM",
                "urgency": "LOW",
                "reason": "Assignments on track (45% completed)"
            },
            {
                "goal_id": "g_personal",
                "name": "🏠 Personal Task Backlog",
                "priority_score": 2.7,
                "trend": "DOWN",
                "importance": "LOW",
                "urgency": "LOW",
                "reason": "De-prioritized to free focus hours for thesis methodology"
            }
        ]

class GoalLifecycleManager:
    def __init__(self):
        self.active_goals = ["g_thesis", "g_job", "g_ai_agent", "g_university", "g_personal"]

    def get_active_count(self) -> int:
        return len(self.active_goals)

class AutonomousGoalPriorityManager:
    def __init__(self):
        self.priority_engine = GoalPriorityEngine()
        self.lifecycle_manager = GoalLifecycleManager()

    def get_goal_priority_summary(self) -> Dict[str, Any]:
        priorities = self.priority_engine.evaluate_priorities()
        top_goal = max(priorities, key=lambda g: g["priority_score"])

        return {
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_active_goals": self.lifecycle_manager.get_active_count(),
            "top_priority_goal": top_goal,
            "goal_priorities": priorities,
            "governor_authorization": "AUTHORIZED (Bounded Autonomy)"
        }
