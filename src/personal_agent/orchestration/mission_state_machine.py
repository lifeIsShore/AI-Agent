from typing import Dict, Any, List, Optional

class MissionStateMachine:
    VALID_STATES = [
        "CREATED", "PLANNING", "PLANNED", "AWAITING_AUTHORIZATION",
        "AUTHORIZED", "EXECUTING", "VERIFYING", "COMPLETED",
        "BLOCKED", "FAILED", "REPLAN", "STOPPED", "CANCELLED", "EMERGENCY_STOP"
    ]

    def __init__(self, mission_id: str, initial_state: str = "CREATED"):
        if initial_state not in self.VALID_STATES:
            raise ValueError(f"Invalid state '{initial_state}'")
        self.mission_id = mission_id
        self.current_state = initial_state
        self.state_history = [{"state": initial_state, "timestamp": "2026-09-03 19:07:00"}]

    def transition_to(self, new_state: str, reason: str = "") -> bool:
        """Transitions mission state safely with historical audit logging."""
        if new_state not in self.VALID_STATES:
            return False
        self.current_state = new_state
        self.state_history.append({"state": new_state, "reason": reason})
        return True
