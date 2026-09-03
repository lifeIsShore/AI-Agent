from typing import Tuple, Optional
from personal_agent.learning.outcome_engine import OutcomeEngine
from personal_agent.autonomy.autonomy_policy import (
    LEVEL_0_OBSERVE, LEVEL_1_RECOMMEND, LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO, LEVEL_4_SUPERVISED_AUTO
)

LEVEL_RANKS = {
    LEVEL_0_OBSERVE: 0,
    LEVEL_1_RECOMMEND: 1,
    LEVEL_2_APPROVAL: 2,
    LEVEL_3_BOUNDED_AUTO: 3,
    LEVEL_4_SUPERVISED_AUTO: 4
}

RANK_TO_LEVEL = {v: k for k, v in LEVEL_RANKS.items()}

class AdaptivePolicy:
    def __init__(self, outcome_engine: Optional[OutcomeEngine] = None):
        self.outcome_engine = outcome_engine or OutcomeEngine()

    def evaluate_adaptive_autonomy_level(
        self,
        action_type: str,
        requested_level: str,
        governor_max_level: str = LEVEL_3_BOUNDED_AUTO
    ) -> Tuple[str, str]:
        """Evaluates historical performance to recommend autonomy level, capped strictly by Governor max level."""
        req_rank = LEVEL_RANKS.get(requested_level, 2)
        gov_max_rank = LEVEL_RANKS.get(governor_max_level, 3)

        success_rate = self.outcome_engine.get_success_rate(action_type)
        outcomes = self.outcome_engine.get_outcomes_by_action_type(action_type)
        user_overrides = [r for r in outcomes if r.user_override or r.outcome_type in ("USER_REJECTED", "USER_MODIFIED")]

        # Determine adaptive recommendation
        if user_overrides and len(user_overrides) >= 2:
            adapted_rank = min(req_rank, LEVEL_RANKS[LEVEL_2_APPROVAL])
            reason = f"Historical user overrides/rejections ({len(user_overrides)}) degraded autonomy level to APPROVAL required."
        elif success_rate >= 95.0 and len(outcomes) >= 5:
            adapted_rank = req_rank
            reason = f"High historical success rate ({success_rate}%) permits requested level {requested_level}."
        else:
            adapted_rank = min(req_rank, LEVEL_RANKS[LEVEL_2_APPROVAL])
            reason = f"Insufficient or mixed historical record ({success_rate}% success); defaulting to APPROVAL required."

        # Hard Security Invariant: Learning can NEVER increase permissions beyond governor_max_level
        final_rank = min(adapted_rank, gov_max_rank)
        final_level = RANK_TO_LEVEL[final_rank]

        if final_rank < adapted_rank:
            reason += f" (Capped by Governor ceiling '{governor_max_level}')."

        return final_level, reason
