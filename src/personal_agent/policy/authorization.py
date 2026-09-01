from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from personal_agent.security.principal import Principal

DECISION_ALLOW = "ALLOW"
DECISION_DENY = "DENY"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

@dataclass
class AuthorizationDecision:
    decision: str                      # ALLOW | DENY | REQUIRE_APPROVAL
    principal_id: str
    principal_type: str
    capability: str
    target: str
    risk_level: str                    # LOW | MEDIUM | HIGH | CRITICAL
    policy_rule: str
    approval_required: bool
    reason: str
    expires_at: Optional[str] = None
    parameters_hash: Optional[str] = None

    def is_allowed(self) -> bool:
        return self.decision == DECISION_ALLOW
