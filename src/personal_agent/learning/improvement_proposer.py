import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List

@dataclass
class ImprovementProposal:
    proposal_id: str
    problem: str
    evidence: str
    hypothesis: str
    proposed_change: str
    expected_gain: str
    risk: str = "LOW"
    affected_components: List[str] = field(default_factory=list)
    modifies_security_boundary: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ImprovementProposer:
    def generate_proposals(
        self,
        weaknesses: List[Dict[str, Any]]
    ) -> List[ImprovementProposal]:
        """Turns observed weaknesses into structured ImprovementProposal objects."""
        proposals = []

        for w in weaknesses:
            p_id = f"prop_{uuid.uuid4().hex[:8]}"
            w_type = w.get("weakness_type")

            if w_type == "HIGH_USER_REJECTION":
                proposals.append(ImprovementProposal(
                    proposal_id=p_id,
                    problem="High user rejection rate on calendar recommendations.",
                    evidence=w.get("evidence", ""),
                    hypothesis="Switching to conservative morning scheduling reduces user rejections.",
                    proposed_change="Update PlanningSpecialist preference rule to favor 09:00-12:00 slots.",
                    expected_gain="Reduce user rejections by 50%.",
                    risk="LOW",
                    affected_components=["PlanningSpecialist"],
                    modifies_security_boundary=False
                ))

            elif w_type == "TOKEN_INEFFICIENCY":
                proposals.append(ImprovementProposal(
                    proposal_id=p_id,
                    problem="Token consumption per research mission is high.",
                    evidence=w.get("evidence", ""),
                    hypothesis="Using local small model for simple summary extraction reduces token cost.",
                    proposed_change="Route summary extraction tasks to TIER_SMALL_LOCAL_LLM.",
                    expected_gain="Reduce token consumption by 35%.",
                    risk="LOW",
                    affected_components=["ModelRouter", "ResearchSpecialist"],
                    modifies_security_boundary=False
                ))

        return proposals
