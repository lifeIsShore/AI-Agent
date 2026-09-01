from typing import Tuple
from personal_agent.autonomy.autonomy_policy import AutonomyPolicyEngine
from personal_agent.policy.engine import PolicyEngine
from personal_agent.control.killswitch import KillSwitchEngine

class AutonomyGovernor:
    def __init__(
        self,
        autonomy_policy: AutonomyPolicyEngine = None,
        policy_engine: PolicyEngine = None,
        killswitch: KillSwitchEngine = None
    ):
        self.autonomy_policy = autonomy_policy or AutonomyPolicyEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.killswitch = killswitch or KillSwitchEngine()

    def authorize_action(
        self,
        action: str,
        target: str,
        risk: str,
        autonomy_level: str
    ) -> Tuple[bool, str]:
        """Final deterministic security gate authorizing or blocking autonomous actions."""
        # 1. KillSwitch check
        ks_ok, ks_msg = self.killswitch.is_action_permitted(action, "system.read")
        if not ks_ok:
            return False, f"Autonomy Governor Denied: {ks_msg}"

        # 2. Autonomy Policy level check
        level_ok, level_msg = self.autonomy_policy.evaluate_autonomy_permission(risk, autonomy_level)
        if not level_ok:
            return False, f"Autonomy Governor Denied: {level_msg}"

        # 3. Policy Engine proposal check
        prop = self.policy_engine.create_proposal(action, target, {})
        auth_dec = self.policy_engine.evaluate_authorization(prop, user_approved=False)
        if not auth_dec.is_allowed():
            return False, f"Autonomy Governor Denied: Policy authorization failed ({auth_dec.reason})."

        return True, f"Autonomy Governor Authorized: Action '{action}' on '{target}' permitted under {autonomy_level}."
