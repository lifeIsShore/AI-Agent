from typing import Dict, Any, Tuple

PILOT_MODE_OBSERVATION = "OBSERVATION"
PILOT_MODE_RECOMMENDATION = "RECOMMENDATION"
PILOT_MODE_APPROVAL = "APPROVAL"
PILOT_MODE_BOUNDED_AUTO = "BOUNDED_AUTO"
PILOT_MODE_EMERGENCY_STOP = "EMERGENCY_STOP"

class PilotController:
    def __init__(self, mode: str = PILOT_MODE_RECOMMENDATION, phase: int = 1):
        self.current_mode = mode
        self.current_phase = phase
        self.rollback_history = []

    def set_pilot_mode(self, mode: str):
        self.current_mode = mode

    def advance_phase(self) -> int:
        if self.current_phase < 5:
            self.current_phase += 1
            if self.current_phase == 1:
                self.current_mode = PILOT_MODE_OBSERVATION
            elif self.current_phase == 2:
                self.current_mode = PILOT_MODE_RECOMMENDATION
            elif self.current_phase == 3:
                self.current_mode = PILOT_MODE_APPROVAL
            elif self.current_phase >= 4:
                self.current_mode = PILOT_MODE_BOUNDED_AUTO
        return self.current_phase

    def trigger_rollback(self, reason: str = "Error threshold exceeded"):
        self.rollback_history.append({"phase": self.current_phase, "mode": self.current_mode, "reason": reason})
        if self.current_phase > 1:
            self.current_phase -= 1
        self.current_mode = PILOT_MODE_RECOMMENDATION

    def is_capability_allowed(
        self,
        capability: str,
        user_approved: bool = False
    ) -> Tuple[bool, str]:
        """Evaluates capability against current pilot mode matrix."""
        if self.current_mode == PILOT_MODE_EMERGENCY_STOP:
            return False, "PilotController HARD BLOCK: Emergency stop active."

        cap_clean = capability.lower()

        # Prohibited actions
        if "financial" in cap_clean or "destructive" in cap_clean or "trash" in cap_clean or "delete" in cap_clean:
            return False, f"PilotController HARD BLOCK: '{capability}' is strictly prohibited during real-world pilot."

        # Mode gating
        if self.current_mode == PILOT_MODE_OBSERVATION:
            if "read" not in cap_clean and "view" not in cap_clean:
                return False, "PilotController BLOCKED: Phase 1 Observation Mode is read-only."

        elif self.current_mode == PILOT_MODE_RECOMMENDATION:
            if "read" not in cap_clean and "view" not in cap_clean and "recommend" not in cap_clean:
                return False, "PilotController BLOCKED: Phase 2 Recommendation Mode cannot modify external systems."

        elif self.current_mode == PILOT_MODE_APPROVAL:
            if "send" in cap_clean or "create" in cap_clean or "modify" in cap_clean or "external" in cap_clean:
                if not user_approved:
                    return False, f"PilotController BLOCKED: '{capability}' requires human approval in Phase 3 Approval Mode."

        return True, f"PilotController PERMITTED: '{capability}' allowed under mode {self.current_mode}."
