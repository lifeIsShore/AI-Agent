from typing import Dict, Any, List

class LongHorizonMissionControl:
    def get_active_missions(self) -> List[Dict[str, Any]]:
        """Returns multi-week active missions, progress velocity, bottlenecks, and completion predictions."""
        return [
            {
                "mission_id": "m_thesis",
                "name": "🎓 Master Thesis Proposal & Research",
                "progress_percent": 76,
                "status": "EXECUTING",
                "predicted_completion": "2026-11-24",
                "deadline": "2026-11-30",
                "risk_level": "LOW",
                "current_step": "Research -> Literature Verification",
                "selected_strategy": "Strategy B (Requirements -> Research -> Calendar -> Write -> Review)",
                "completion_prob": 0.89,
                "bottleneck": "Literature Diversity"
            },
            {
                "mission_id": "m_msc_courses",
                "name": "📚 M.Sc. Mannheim Course Workload",
                "progress_percent": 45,
                "status": "ACTIVE",
                "predicted_completion": "2026-12-15",
                "deadline": "2026-12-20",
                "risk_level": "LOW",
                "current_step": "Assignment Review",
                "selected_strategy": "Strategy A",
                "completion_prob": 0.92,
                "bottleneck": "None"
            }
        ]
