from typing import List, Dict, Any, Tuple

class ConflictResolver:
    def resolve_agent_conflict(self, proposals: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], str]:
        """Resolves conflicting proposals between specialist agents based on priority and urgency."""
        if not proposals:
            return {}, "No proposals to resolve."

        if len(proposals) == 1:
            return proposals[0], "Single proposal selected without conflict."

        # Sort by urgency and priority
        sorted_props = sorted(
            proposals,
            key=lambda p: (p.get("priority", "LOW") == "HIGH", p.get("urgency", 0.0)),
            reverse=True
        )

        winning_prop = sorted_props[0]
        loser_prop = sorted_props[1]
        reason = f"Resolved conflict in favor of '{winning_prop.get('agent')}' proposal over '{loser_prop.get('agent')}' proposal due to higher deadline urgency."
        return winning_prop, reason
