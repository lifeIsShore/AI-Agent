import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from personal_agent.runtime.heartbeat import HeartbeatSnapshot
from personal_agent.runtime.lifecycle import AgentLifecycleState

@dataclass
class WatchdogStatus:
    is_healthy: bool
    issue_type: Optional[str] = None
    recommended_state: str = AgentLifecycleState.RUNNING.value
    details: str = "Operating normally."

class RuntimeWatchdog:
    def __init__(
        self,
        max_heartbeat_staleness_sec: float = 30.0,
        max_execution_duration_sec: float = 60.0,
        max_consecutive_errors: int = 3
    ):
        self.max_heartbeat_staleness_sec = max_heartbeat_staleness_sec
        self.max_execution_duration_sec = max_execution_duration_sec
        self.max_consecutive_errors = max_consecutive_errors

    def evaluate_health(
        self,
        heartbeat: Optional[HeartbeatSnapshot],
        operation_start_time: Optional[float] = None,
        dependency_health: Optional[Dict[str, bool]] = None
    ) -> WatchdogStatus:
        now = time.time()

        # 1. Heartbeat check
        if not heartbeat:
            return WatchdogStatus(
                is_healthy=False,
                issue_type="NO_HEARTBEAT",
                recommended_state=AgentLifecycleState.DEGRADED.value,
                details="No heartbeat recorded yet."
            )

        staleness = now - heartbeat.timestamp
        if staleness > self.max_heartbeat_staleness_sec:
            return WatchdogStatus(
                is_healthy=False,
                issue_type="MISSED_HEARTBEAT",
                recommended_state=AgentLifecycleState.RECOVERING.value,
                details=f"Heartbeat is stale ({staleness:.1f}s > threshold {self.max_heartbeat_staleness_sec}s)."
            )

        # 2. Consecutive error check
        if heartbeat.consecutive_errors >= self.max_consecutive_errors:
            return WatchdogStatus(
                is_healthy=False,
                issue_type="REPEATED_FAILURES",
                recommended_state=AgentLifecycleState.DEGRADED.value,
                details=f"Consecutive errors ({heartbeat.consecutive_errors}) exceeded threshold ({self.max_consecutive_errors})."
            )

        # 3. Stalled operation check
        if operation_start_time and (now - operation_start_time) > self.max_execution_duration_sec:
            duration = now - operation_start_time
            return WatchdogStatus(
                is_healthy=False,
                issue_type="STALLED_EXECUTION",
                recommended_state=AgentLifecycleState.DEGRADED.value,
                details=f"Operation duration ({duration:.1f}s) exceeded execution timeout ({self.max_execution_duration_sec}s)."
            )

        # 4. Dependency health check
        if dependency_health:
            unhealthy_deps = [dep for dep, status in dependency_health.items() if not status]
            if unhealthy_deps:
                return WatchdogStatus(
                    is_healthy=False,
                    issue_type="UNHEALTHY_DEPENDENCIES",
                    recommended_state=AgentLifecycleState.DEGRADED.value,
                    details=f"Unhealthy dependencies detected: {', '.join(unhealthy_deps)}."
                )

        return WatchdogStatus(
            is_healthy=True,
            issue_type=None,
            recommended_state=AgentLifecycleState.RUNNING.value,
            details="All watchdog parameters are healthy."
        )
