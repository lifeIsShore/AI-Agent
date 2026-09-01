from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from personal_agent.policy.proposal import ActionProposal
from personal_agent.policy.capabilities import resolve_capability

MODE_AUTOMATIC = "AUTOMATIC"
MODE_QUICK_REVIEW = "QUICK_REVIEW"
MODE_DETAILED_REVIEW = "DETAILED_REVIEW"
MODE_CRITICAL_DENIAL = "CRITICAL_DENIAL"

@dataclass
class ReviewDecision:
    mode: str                          # AUTOMATIC | QUICK_REVIEW | DETAILED_REVIEW | CRITICAL_DENIAL
    required_approval: bool
    risk_level: str                    # LOW | MEDIUM | HIGH | CRITICAL
    reversibility: bool
    explainability_summary: str
    confidence_evidence: float = 1.0

class ReviewDecisionEngine:
    def evaluate_review_mode(
        self,
        proposal: ActionProposal,
        historical_approval_rate: float = 1.0
    ) -> ReviewDecision:
        """Determines adaptive review mode based on risk level, reversibility, side-effects, and preference evidence."""
        capability = resolve_capability(proposal.action) or proposal.action
        risk = proposal.risk_level

        # Reversibility evaluation
        is_reversible = proposal.action not in ["delete_email", "trash_email", "delete_calendar_event", "send_email", "delete_task"]
        is_external_communication = proposal.action in ["send_email"]

        if risk == "CRITICAL":
            return ReviewDecision(
                mode=MODE_CRITICAL_DENIAL,
                required_approval=False,
                risk_level=risk,
                reversibility=False,
                explainability_summary=f"Action '{proposal.action}' is classified as CRITICAL and prohibited by system policy.",
                confidence_evidence=proposal.confidence
            )

        if is_external_communication or risk == "HIGH":
            return ReviewDecision(
                mode=MODE_DETAILED_REVIEW,
                required_approval=True,
                risk_level=risk,
                reversibility=is_reversible,
                explainability_summary=f"High-impact capability '{capability}' requires detailed human review prior to execution.",
                confidence_evidence=proposal.confidence
            )

        if risk == "MEDIUM":
            return ReviewDecision(
                mode=MODE_QUICK_REVIEW,
                required_approval=True,
                risk_level=risk,
                reversibility=is_reversible,
                explainability_summary=f"Capability '{capability}' requires quick human approval or parameter editing.",
                confidence_evidence=proposal.confidence
            )

        # Low Risk
        return ReviewDecision(
            mode=MODE_AUTOMATIC,
            required_approval=False,
            risk_level=risk,
            reversibility=is_reversible,
            explainability_summary=f"Low risk capability '{capability}' automatically approved by policy.",
            confidence_evidence=proposal.confidence
        )
