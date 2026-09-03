from typing import Tuple, Dict, Any
from personal_agent.learning.improvement_proposer import ImprovementProposal

class ImprovementGovernor:
    def authorize_proposal(
        self,
        proposal: ImprovementProposal,
        sandbox_result: Dict[str, Any],
        user_approved: bool = False
    ) -> Tuple[bool, str]:
        """Validates that proposed changes NEVER modify security boundaries or permissions."""

        # Invariant 1: Security Boundary Security Rule
        if proposal.modifies_security_boundary or "financial" in proposal.proposed_change.lower() or "delete" in proposal.proposed_change.lower():
            return False, f"ImprovementGovernor HARD REJECT: Proposal '{proposal.proposal_id}' attempts to modify security boundaries or permissions."

        # Invariant 2: Sandbox Evaluation Gate
        if not sandbox_result.get("passed", False):
            return False, f"ImprovementGovernor REJECT: Proposal '{proposal.proposal_id}' failed sandbox simulation evaluation ({sandbox_result.get('reason')})."

        # Invariant 3: Human Approval Gate
        if not user_approved:
            return False, f"ImprovementGovernor GATE: Proposal '{proposal.proposal_id}' passed sandbox evaluation and requires human approval for deployment."

        return True, f"ImprovementGovernor APPROVED: Proposal '{proposal.proposal_id}' authorized for production deployment."
