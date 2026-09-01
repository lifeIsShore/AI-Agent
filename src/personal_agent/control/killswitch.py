from typing import Tuple

MODE_NORMAL = "NORMAL"
MODE_READ_ONLY = "READ_ONLY"
MODE_PAUSED = "PAUSED"
MODE_EMERGENCY_STOP = "EMERGENCY_STOP"
MODE_MAINTENANCE = "MAINTENANCE"

class KillSwitchEngine:
    def __init__(self, initial_mode: str = MODE_NORMAL):
        self.mode = initial_mode
        self.reason = "System initialized normally."

    def set_mode(self, mode: str, reason: str = ""):
        """Sets agent runtime mode out-of-band (cannot be altered by LLM reasoning)."""
        valid_modes = [MODE_NORMAL, MODE_READ_ONLY, MODE_PAUSED, MODE_EMERGENCY_STOP, MODE_MAINTENANCE]
        if mode not in valid_modes:
            raise ValueError(f"Invalid runtime mode '{mode}'. Must be one of {valid_modes}")
        self.mode = mode
        self.reason = reason or f"Mode updated to {mode}"

    def get_mode(self) -> str:
        return self.mode

    def trigger_emergency_stop(self, reason: str = "Emergency stop engaged by system operator"):
        """Engages out-of-band Emergency Stop instantly blocking all actions."""
        self.set_mode(MODE_EMERGENCY_STOP, reason=reason)

    def enable_read_only_mode(self, reason: str = "Safe mode activated"):
        """Engages READ_ONLY safe mode permitting reads while blocking all modifications."""
        self.set_mode(MODE_READ_ONLY, reason=reason)

    def reset_to_normal(self):
        self.set_mode(MODE_NORMAL, reason="Reset to normal operation")

    def is_action_permitted(self, action: str, permission_level: str = "MODIFY") -> Tuple[bool, str]:
        """Evaluates whether an action is permitted under current runtime control mode."""
        if self.mode == MODE_EMERGENCY_STOP:
            return False, f"Action '{action}' DENIED: Emergency Stop active ({self.reason})."
        elif self.mode == MODE_PAUSED:
            return False, f"Action '{action}' DENIED: Agent execution is PAUSED."
        elif self.mode == MODE_READ_ONLY and permission_level in ["MODIFY", "ADMIN"]:
            return False, f"Action '{action}' DENIED: Agent is in READ_ONLY safe mode."

        return True, f"Permitted under {self.mode} runtime mode."
