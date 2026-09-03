from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Tuple
from personal_agent.autonomy.autonomy_policy import LEVEL_3_BOUNDED_AUTO

@dataclass
class AutonomyProfile:
    profile_id: str
    mission_id: str
    max_autonomy_level: str = LEVEL_3_BOUNDED_AUTO
    allowed_capabilities: List[str] = field(default_factory=lambda: ["email.read", "calendar.read", "calendar.modify", "tasks.read", "tasks.write"])
    requires_explicit_approval: List[str] = field(default_factory=lambda: ["external_email", "application_submission", "financial_transaction", "delete_file"])

    def is_action_allowed(
        self,
        capability: str,
        user_approved: bool = False
    ) -> Tuple[bool, str]:
        """Evaluates action against mission-specific autonomy profile rules."""
        cap_clean = capability.lower()

        # Check explicit approval requirements
        for req in self.requires_explicit_approval:
            if req in cap_clean:
                if not user_approved:
                    return False, f"AutonomyProfile HARD BLOCK: Action '{capability}' requires explicit human approval."

        return True, f"AutonomyProfile PERMITTED: Action '{capability}' allowed under profile '{self.profile_id}'."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
