from typing import Dict, Any, List

class EmergencyStop:
    def __init__(self):
        self.emergency_active: bool = False
        self.stop_reason: str = ""
        self.paused_specialists: List[str] = []
        self.revoked_capabilities: List[str] = []

    def trigger_emergency_stop(self, reason: str = "User initiated emergency stop") -> Dict[str, Any]:
        """Instantly halts all autonomous execution across all systems."""
        self.emergency_active = True
        self.stop_reason = reason
        return {
            "status": "EMERGENCY_STOP_ACTIVE",
            "reason": reason,
            "subsequent_actions_blocked": True
        }

    def is_emergency_active(self) -> bool:
        return self.emergency_active

    def pause_specialist(self, specialist_id: str):
        if specialist_id not in self.paused_specialists:
            self.paused_specialists.append(specialist_id)

    def revoke_capability(self, capability: str):
        cap_clean = capability.lower()
        if cap_clean not in self.revoked_capabilities:
            self.revoked_capabilities.append(cap_clean)

    def is_capability_revoked(self, capability: str) -> bool:
        return capability.lower() in self.revoked_capabilities

    def resume_normal_operations(self):
        self.emergency_active = False
        self.stop_reason = ""
