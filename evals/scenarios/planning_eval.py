import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.planner.daily_planner import DailyPlannerEngine
from personal_agent.context.package import ContextPackage

class PlanningEvaluator:
    def __init__(self):
        self.planner = DailyPlannerEngine(user_name="Ahmet")

    def evaluate_planning_conflicts(self) -> Dict[str, Any]:
        """Evaluates daily planner allocations against busy slots to detect conflicts."""
        context_pkg = ContextPackage(
            task="plan_day",
            user_request="Plan my day",
            emails=[{"requires_action": True, "requires_planning": True, "subject": "Finish thesis proposal"}],
            calendar=[{"summary": "University Lecture", "start": "09:00", "end": "10:00"}]
        )
        free_slots = [
            {"start": "10:00", "end": "12:00", "duration_minutes": 120},
            {"start": "14:00", "end": "17:00", "duration_minutes": 180}
        ]

        plan = self.planner.generate_daily_plan(context_pkg, free_slots=free_slots)
        proposals = plan.get("proposals", [])

        conflicts = 0
        for p in proposals:
            s_time = p.get("start_time", "")
            if s_time.startswith("09:"):
                conflicts += 1

        return {
            "accuracy": 100.0 if conflicts == 0 else 50.0,
            "conflicts": conflicts,
            "proposals_count": len(proposals)
        }
