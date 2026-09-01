from typing import Dict, Any, Callable, Tuple, Optional
from personal_agent.reliability.circuit_breaker import CircuitBreaker
from personal_agent.reliability.retry import retry_with_backoff

class ServiceDegradationHandler:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {
            "gmail": CircuitBreaker("gmail", failure_threshold=3, cooldown_sec=5.0),
            "calendar": CircuitBreaker("calendar", failure_threshold=3, cooldown_sec=5.0),
            "tasks": CircuitBreaker("tasks", failure_threshold=3, cooldown_sec=5.0),
            "ollama": CircuitBreaker("ollama", failure_threshold=3, cooldown_sec=5.0)
        }

    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Retrieves or creates a CircuitBreaker for a target service."""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(service_name, failure_threshold=3, cooldown_sec=5.0)
        return self.breakers[service_name]

    def execute_with_protection(
        self,
        service_name: str,
        func: Callable[[], Any],
        fallback_value: Optional[Any] = None,
        max_attempts: int = 3
    ) -> Tuple[bool, Any, str]:
        """Executes a service call protected by CircuitBreaker and retry backoff."""
        breaker = self.get_breaker(service_name)
        can_exec, msg = breaker.can_execute()

        if not can_exec:
            print(f"[Degradation] Service '{service_name}' circuit OPEN. Returning graceful fallback.")
            return False, fallback_value, f"Service '{service_name}' temporarily degraded ({msg})"

        success, res, meta = retry_with_backoff(func, max_attempts=max_attempts)
        if success:
            breaker.record_success()
            return True, res, "Success"
        else:
            breaker.record_failure()
            print(f"[Degradation] Service '{service_name}' failed after {meta['attempt_count']} attempts: {meta['last_error']}")
            return False, fallback_value, f"Service '{service_name}' execution failed: {meta['last_error']}"
