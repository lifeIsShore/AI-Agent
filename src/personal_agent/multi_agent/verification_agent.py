from typing import Dict, Any, List

class VerificationAgent:
    def __init__(self):
        self.agent_id = "VerificationAgent"

    def verify_evidence_threshold(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verifies evidence thresholds before governor submission."""
        valid_items = sum(1 for e in evidence_list if e.get("confidence", 0.0) >= 0.70)
        threshold_met = valid_items >= 1

        return {
            "verifier_agent_id": self.agent_id,
            "total_evidence_count": len(evidence_list),
            "valid_evidence_count": valid_items,
            "threshold_met": threshold_met,
            "status": "EVIDENCE_VERIFIED" if threshold_met else "INSUFFICIENT_EVIDENCE"
        }
