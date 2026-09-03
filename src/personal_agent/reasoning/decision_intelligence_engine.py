from typing import Dict, Any, List

class DecisionIntelligenceEngine:
    def formulate_decision_options(
        self,
        problem_statement: str,
        current_workload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Formulates scenario trade-off options (Option A, Option B, Option C) with recommendations."""
        options: List[Dict[str, Any]] = [
            {
                "option_id": "opt_a",
                "name": "Option A — Continue Current Plan",
                "completion_prob": 0.72,
                "risk_level": "HIGH",
                "impact": "High risk of missing thesis proposal review window."
            },
            {
                "option_id": "opt_b",
                "name": "Option B — Reduce Secondary Workload",
                "completion_prob": 0.84,
                "risk_level": "LOW",
                "impact": "Frees 6 hours for thesis focus. Highly recommended."
            },
            {
                "option_id": "opt_c",
                "name": "Option C — Move Research Deadline",
                "completion_prob": 0.91,
                "risk_level": "LOW",
                "impact": "Requires advisor notification email."
            }
        ]

        return {
            "problem_statement": problem_statement,
            "options": options,
            "recommended_option": "opt_b",
            "recommendation_reason": "Option B maximizes thesis completion probability (84%) while maintaining low risk without calendar delays.",
            "requires_user_decision": True
        }
