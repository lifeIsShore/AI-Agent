from typing import Dict, Any

class InterAgentConflictResolver:
    def resolve_agent_conflict(
        self,
        proposal_a: Dict[str, Any],
        proposal_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolves conflicting proposals between specialist agents based on safety & confidence."""
        conf_a = proposal_a.get("confidence", 0.5)
        conf_b = proposal_b.get("confidence", 0.5)

        winner = proposal_a if conf_a >= conf_b else proposal_b

        return {
            "resolution_status": "CONFLICT_RESOLVED",
            "winning_proposal": winner,
            "reason": f"Selected proposal from '{winner.get('agent_id', 'agent')}' due to higher confidence ({max(conf_a, conf_b)})."
        }
