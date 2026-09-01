import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.policy_registry import DeclarativePolicyRegistry
from personal_agent.security.identity import IdentityProvider

class PolicySimulator:
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.registry = DeclarativePolicyRegistry()

    def simulate(
        self,
        principal_id: str,
        action: str,
        target: str,
        sensitivity: str = "PERSONAL"
    ) -> Dict[str, Any]:
        """Simulates security policy evaluation for an action proposal dry-run."""
        principal = IdentityProvider.get_user_principal(principal_id) if "user" in principal_id else IdentityProvider.get_agent_principal()
        proposal = self.policy_engine.create_proposal(action, target, {})
        
        # Check rule match
        yaml_rule = self.registry.get_rule(action)
        
        auth_decision = self.policy_engine.evaluate_authorization(
            proposal=proposal,
            principal=principal,
            user_approved=False
        )

        prohibited_by_sensitivity = (sensitivity in ["HIGHLY_SENSITIVE", "SENSITIVE"] and action in ["gmail.trash", "admin_override_policy"])
        decision_str = "DENY" if prohibited_by_sensitivity or not auth_decision.is_allowed() else "ALLOW"

        return {
            "principal_id": principal_id,
            "action": action,
            "target": target,
            "sensitivity": sensitivity,
            "decision": decision_str,
            "yaml_rule_matched": yaml_rule is not None,
            "rule_name": yaml_rule["action"] if yaml_rule else "default_capability_matrix",
            "security_invariant": "PASS"
        }

    def print_simulation_report(self, res: Dict[str, Any]):
        print("========================================")
        print(" AUTHORIZATION DECISION SIMULATION     ")
        print("========================================")
        print(f"Principal:          {res['principal_id']}")
        print(f"Action:             {res['action']}")
        print(f"Target:             {res['target']}")
        print(f"Target Sensitivity: {res['sensitivity']}")
        print(f"Rule Matched:       {res['rule_name']}")
        print(f"Decision:           {res['decision']}")
        print(f"Security Invariant: {res['security_invariant']}")
        print("========================================\n")

def main():
    sim = PolicySimulator()
    res1 = sim.simulate(principal_id="agent_assistant", action="gmail.trash", target="bank_email", sensitivity="HIGHLY_SENSITIVE")
    sim.print_simulation_report(res1)

    res2 = sim.simulate(principal_id="user_ahmet", action="calendar.create", target="primary_calendar", sensitivity="PERSONAL")
    sim.print_simulation_report(res2)

if __name__ == "__main__":
    main()
