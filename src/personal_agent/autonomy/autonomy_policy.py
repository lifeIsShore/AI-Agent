from typing import Tuple

LEVEL_0_OBSERVE = "LEVEL_0_OBSERVE"
LEVEL_1_RECOMMEND = "LEVEL_1_RECOMMEND"
LEVEL_2_APPROVAL = "LEVEL_2_APPROVAL"
LEVEL_3_BOUNDED_AUTO = "LEVEL_3_BOUNDED_AUTO"
LEVEL_4_SUPERVISED_AUTO = "LEVEL_4_SUPERVISED_AUTO"

class AutonomyPolicyEngine:
    def evaluate_autonomy_permission(self, action_risk: str, autonomy_level: str) -> Tuple[bool, str]:
        """Evaluates whether an action is allowed for autonomous execution under current autonomy level."""
        if autonomy_level == LEVEL_0_OBSERVE:
            return False, "Level 0 Observe Mode: Execution forbidden."

        if autonomy_level == LEVEL_1_RECOMMEND:
            return False, "Level 1 Recommend Mode: Action recommendation generated, execution forbidden."

        if autonomy_level == LEVEL_2_APPROVAL:
            return False, "Level 2 Approval Mode: Explicit human approval required before execution."

        if autonomy_level == LEVEL_3_BOUNDED_AUTO:
            if action_risk == "LOW":
                return True, "Level 3 Bounded Auto: LOW risk action pre-authorized for auto-execution."
            return False, f"Level 3 Bounded Auto: {action_risk} risk action requires explicit human approval."

        if autonomy_level == LEVEL_4_SUPERVISED_AUTO:
            if action_risk in ["LOW", "MEDIUM"]:
                return True, f"Level 4 Supervised Auto: {action_risk} risk action authorized for auto-execution."
            return False, "Level 4 Supervised Auto: HIGH risk action requires explicit human approval."

        return False, f"Unknown autonomy level '{autonomy_level}'."
