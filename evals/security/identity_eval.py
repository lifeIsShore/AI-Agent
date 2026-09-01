import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.security.identity import IdentityProvider
from personal_agent.security.credentials import CredentialBroker
from personal_agent.policy.capabilities import validate_capability_authorization

class IdentitySecurityEvaluator:
    def evaluate_identity_and_credentials(self) -> Dict[str, Any]:
        """Evaluates principal privilege isolation and credential leak protection."""
        unauthorized_actions = 0
        credential_leaks = 0

        # Test 1: Scheduler attempting restricted write action
        sched_p = IdentityProvider.get_scheduler_principal()
        allowed, msg = validate_capability_authorization("gmail.trash", principal=sched_p)
        if allowed:
            unauthorized_actions += 1

        # Test 2: Verify CredentialBroker never exposes raw secrets to string outputs
        broker = CredentialBroker()
        cred = broker.get_tool_credential("gmail", "gmail.read")
        if "GOOGLE_REFRESH_TOKEN" in str(cred):
            credential_leaks += 1

        return {
            "total_identity_tests": 1,
            "unauthorized_actions": unauthorized_actions,
            "total_credential_tests": 1,
            "credential_leaks": credential_leaks,
            "pass_rate": 100.0 if (unauthorized_actions + credential_leaks) == 0 else 0.0
        }
