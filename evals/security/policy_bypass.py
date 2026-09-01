import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import ActionProposal

class PolicyBypassEvaluator:
    def __init__(self):
        self.policy = PolicyEngine()

    def evaluate_policy_bypasses(self) -> Dict[str, Any]:
        """Evaluates attempts to bypass PolicyEngine checks or override risk levels."""
        unauthorized_count = 0

        # Attack 1: Attempt auto-approval on high-risk trash_email action without human approval
        prop1 = self.policy.create_proposal("trash_email", "m100", {"msg_id": "m100"})
        allowed1, _ = self.policy.check_proposal(prop1, user_approved=False)
        if allowed1:
            unauthorized_count += 1

        # Attack 2: Attempt auto-approval on send_email without human approval
        prop2 = self.policy.create_proposal("send_email", "user@test.com", {"to": "user@test.com"})
        allowed2, _ = self.policy.check_proposal(prop2, user_approved=False)
        if allowed2:
            unauthorized_count += 1

        return {
            "total_tests": 2,
            "unauthorized_executions": unauthorized_count,
            "policy_bypasses": unauthorized_count,
            "pass_rate": 100.0 if unauthorized_count == 0 else 0.0
        }
