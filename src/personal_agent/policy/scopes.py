from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple

SCOPE_ONE_TIME = "ONE_TIME"
SCOPE_BATCH = "BATCH"
SCOPE_SESSION = "SESSION"
SCOPE_RECURRING = "RECURRING"

@dataclass
class DelegatedScope:
    scope_id: str
    scope_type: str                    # ONE_TIME | BATCH | SESSION | RECURRING
    capability: str                    # e.g. gmail.archive
    filter_pattern: str                # e.g. newsletter
    expires_at: Optional[str] = None
    daily_limit: int = 20
    current_daily_count: int = 0

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        try:
            exp_dt = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            return now_dt >= exp_dt
        except ValueError:
            return False

    def can_execute(self) -> bool:
        if self.is_expired():
            return False
        return self.current_daily_count < self.daily_limit

class ScopeManager:
    def __init__(self):
        self.delegations: Dict[str, DelegatedScope] = {}

    def add_delegation(
        self,
        capability: str,
        filter_pattern: str = "*",
        scope_type: str = SCOPE_RECURRING,
        ttl_days: int = 30,
        daily_limit: int = 20
    ) -> DelegatedScope:
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=ttl_days)).isoformat()
        scope_id = f"scope_{capability}_{filter_pattern}"

        delegation = DelegatedScope(
            scope_id=scope_id,
            scope_type=scope_type,
            capability=capability,
            filter_pattern=filter_pattern,
            expires_at=expires_at,
            daily_limit=daily_limit,
            current_daily_count=0
        )
        self.delegations[scope_id] = delegation
        return delegation

    def check_delegated_authorization(self, capability: str, target: str) -> Tuple[bool, str]:
        """Checks if an action is covered under an active bounded recurring delegation."""
        for scope in self.delegations.values():
            if scope.capability == capability:
                if scope.filter_pattern == "*" or scope.filter_pattern in target:
                    if scope.is_expired():
                        return False, f"Delegated scope '{scope.scope_id}' has expired."
                    if scope.current_daily_count >= scope.daily_limit:
                        return False, f"Delegated scope '{scope.scope_id}' reached daily rate limit ({scope.daily_limit}/day)."
                    
                    scope.current_daily_count += 1
                    return True, f"Authorized under delegated recurring scope '{scope.scope_id}' ({scope.current_daily_count}/{scope.daily_limit} today)"

        return False, "No active delegated scope found."
