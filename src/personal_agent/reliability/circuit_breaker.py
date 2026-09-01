import time
from typing import Tuple

STATE_CLOSED = "CLOSED"
STATE_OPEN = "OPEN"
STATE_HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, cooldown_sec: float = 10.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_sec = cooldown_sec
        self.state = STATE_CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def can_execute(self) -> Tuple[bool, str]:
        """Checks whether requests are allowed through the circuit breaker."""
        now = time.time()
        if self.state == STATE_CLOSED:
            return True, "Circuit CLOSED (Normal)"

        if self.state == STATE_OPEN:
            if now - self.last_failure_time >= self.cooldown_sec:
                self.state = STATE_HALF_OPEN
                return True, "Circuit HALF_OPEN (Testing Recovery)"
            return False, f"Circuit '{self.name}' is OPEN due to repeated failures. Requests blocked for cooldown."

        if self.state == STATE_HALF_OPEN:
            return True, "Circuit HALF_OPEN (Testing Recovery)"

        return True, "Circuit Normal"

    def record_success(self):
        """Resets failure count and closes circuit upon successful call."""
        self.failure_count = 0
        self.state = STATE_CLOSED

    def record_failure(self):
        """Increments failure count and opens circuit if threshold is exceeded."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = STATE_OPEN
