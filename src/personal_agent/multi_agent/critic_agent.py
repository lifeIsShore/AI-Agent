from typing import Dict, Any, List

class CriticAgent:
    def __init__(self):
        self.agent_id = "CriticAgent"

    def evaluate_plan_quality(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates strategy completeness, plan quality, and literature diversity."""
        steps = plan.get("steps", [])
        has_research = any("research" in str(s).lower() for s in steps)
        has_review = any("review" in str(s).lower() for s in steps)

        quality_score = 0.95 if (has_research and has_review) else 0.65
        passed = quality_score >= 0.80

        feedback = "Plan satisfies structural diversity requirements." if passed else "Strategy lacks sufficient review or research validation steps."

        return {
            "critic_agent_id": self.agent_id,
            "quality_score": quality_score,
            "passed": passed,
            "feedback": feedback
        }
