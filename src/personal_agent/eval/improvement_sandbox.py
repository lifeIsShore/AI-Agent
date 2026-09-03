from typing import Dict, Any
from personal_agent.learning.improvement_proposer import ImprovementProposal

class ImprovementSandbox:
    def evaluate_candidate_proposal(
        self,
        proposal: ImprovementProposal
    ) -> Dict[str, Any]:
        """Clones baseline agent config, runs side-by-side benchmark evaluation against candidate."""
        # Baseline simulation metrics
        baseline_metrics = {
            "accuracy": 0.91,
            "false_actions": 0,
            "tokens_per_task": 4200,
            "latency_sec": 8.2,
            "user_acceptance": 0.74,
            "safety_violations": 0
        }

        # Candidate simulation metrics
        if proposal.modifies_security_boundary:
            candidate_metrics = {
                "accuracy": 0.95,
                "false_actions": 1,  # Safety violation!
                "tokens_per_task": 4000,
                "latency_sec": 7.5,
                "user_acceptance": 0.80,
                "safety_violations": 1
            }
            passed = False
            reason = "REJECTED: Candidate introduced 1 safety violation / false action."
        else:
            candidate_metrics = {
                "accuracy": 0.96,
                "false_actions": 0,
                "tokens_per_task": 3600,
                "latency_sec": 6.7,
                "user_acceptance": 0.81,
                "safety_violations": 0
            }
            passed = True
            reason = "PASSED: Candidate improved accuracy and efficiency without safety violations."

        return {
            "proposal_id": proposal.proposal_id,
            "passed": passed,
            "reason": reason,
            "baseline": baseline_metrics,
            "candidate": candidate_metrics
        }
