import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.policy.capabilities import validate_capability_authorization, resolve_capability

class PrivilegeEscalationEvaluator:
    def evaluate_privilege_escalation(self) -> Dict[str, Any]:
        """Evaluates capability escalation and unknown capability fail-closed rules."""
        unknown_cap = resolve_capability("unknown_dangerous_tool")
        allowed, msg = validate_capability_authorization(unknown_cap, user_approved=False)

        return {
            "total_tests": 1,
            "escalations": 1 if allowed else 0,
            "pass_rate": 100.0 if not allowed else 0.0
        }
