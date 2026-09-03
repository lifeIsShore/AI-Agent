import time
from typing import Dict, Any, Optional, List
from personal_agent.runtime.lifecycle import LifecycleManager, AgentLifecycleState, RuntimeCheckpoint
from personal_agent.runtime.heartbeat import HeartbeatMonitor, HeartbeatSnapshot
from personal_agent.runtime.watchdog import RuntimeWatchdog, WatchdogStatus
from personal_agent.autonomy.controller import AutonomyController
from personal_agent.autonomy.governor import AutonomyGovernor

class RuntimeSupervisor:
    def __init__(
        self,
        storage_dir: str = "data/runtime",
        heartbeat_interval: float = 10.0,
        autonomy_controller: Optional[AutonomyController] = None,
        governor: Optional[AutonomyGovernor] = None
    ):
        self.lifecycle_manager = LifecycleManager(storage_dir=storage_dir)
        self.heartbeat_monitor = HeartbeatMonitor(interval_sec=heartbeat_interval)
        self.watchdog = RuntimeWatchdog()
        self.autonomy_controller = autonomy_controller or AutonomyController()
        self.governor = governor or AutonomyGovernor()
        
        # Load previous checkpoint or initialize STARTING
        self.last_checkpoint = self.lifecycle_manager.load_checkpoint()
        self.current_state = AgentLifecycleState(self.last_checkpoint.state)
        self.active_goal_id: Optional[str] = self.last_checkpoint.active_goal_id
        self.active_workflows: List[str] = self.last_checkpoint.active_workflows
        self.consecutive_errors: int = 0
        self.current_operation_start_time: Optional[float] = None

    def start(self) -> RuntimeCheckpoint:
        """Transitions state machine from STARTING -> INITIALIZING -> RUNNING."""
        self.current_state = AgentLifecycleState.INITIALIZING
        self._save_state()
        
        # System startup initialization
        self.current_state = AgentLifecycleState.RUNNING
        return self._save_state()

    def _save_state(self, metadata: Optional[Dict[str, Any]] = None) -> RuntimeCheckpoint:
        chk = self.lifecycle_manager.save_checkpoint(
            state=self.current_state.value,
            active_goal_id=self.active_goal_id,
            active_workflows=self.active_workflows,
            metadata=metadata
        )
        self.last_checkpoint = chk
        return chk

    def emit_heartbeat(
        self,
        active_goal_id: Optional[str] = None,
        current_op: str = "idle",
        latency_ms: float = 0.0,
        consecutive_errors: Optional[int] = None
    ) -> HeartbeatSnapshot:
        if active_goal_id is not None:
            self.active_goal_id = active_goal_id
        if consecutive_errors is not None:
            self.consecutive_errors = consecutive_errors

        hb = self.heartbeat_monitor.record_heartbeat(
            state=self.current_state.value,
            active_goal_id=self.active_goal_id,
            current_operation=current_op,
            latency_ms=latency_ms,
            consecutive_errors=self.consecutive_errors
        )

        # Run watchdog health evaluation
        watchdog_status = self.watchdog.evaluate_health(
            heartbeat=hb,
            operation_start_time=self.current_operation_start_time
        )

        if not watchdog_status.is_healthy:
            print(f"[RuntimeSupervisor WATCHDOG ALERT] {watchdog_status.details}")
            # Transition to recommended degraded/recovering state
            if self.current_state == AgentLifecycleState.RUNNING:
                self.current_state = AgentLifecycleState(watchdog_status.recommended_state)
                self._save_state(metadata={"watchdog_issue": watchdog_status.issue_type, "details": watchdog_status.details})

        return hb

    def attempt_recovery(self, simulate_failure: bool = False) -> bool:
        """Attempts safe recovery procedure. If recovery fails, forces PAUSED state."""
        self.current_state = AgentLifecycleState.RECOVERING
        self._save_state(metadata={"action": "recovery_started"})

        if simulate_failure:
            print("[RuntimeSupervisor Recovery] Recovery procedure failed. Transitioning to PAUSED.")
            self.current_state = AgentLifecycleState.PAUSED
            self._save_state(metadata={"action": "recovery_failed_paused"})
            return False

        print("[RuntimeSupervisor Recovery] Self-healing completed successfully. Transitioning to RUNNING.")
        self.consecutive_errors = 0
        self.current_operation_start_time = None
        self.current_state = AgentLifecycleState.RUNNING
        self._save_state(metadata={"action": "recovery_succeeded_running"})
        return True

    def execute_autonomous_action(self, goal_id: str, proposed_action: str = "create_calendar_event", risk_level: str = "LOW") -> Dict[str, Any]:
        """Runs an autonomous action cycle, strictly blocked if not in RUNNING state."""
        if self.current_state != AgentLifecycleState.RUNNING:
            err_msg = f"Autonomous execution BLOCKED. Supervisor state is '{self.current_state.value}' (must be RUNNING)."
            print(f"[RuntimeSupervisor SAFETY GATE] {err_msg}")
            return {
                "goal_id": goal_id,
                "status": "BLOCKED",
                "reason": err_msg,
                "supervisor_state": self.current_state.value
            }

        # Check with governor
        authorized, gov_msg = self.governor.authorize_action(
            action=proposed_action,
            target="system",
            risk=risk_level,
            autonomy_level=self.autonomy_controller.autonomy_level,
            supervisor_state=self.current_state.value
        )

        if not authorized:
            return {
                "goal_id": goal_id,
                "status": "DENIED",
                "reason": gov_msg,
                "supervisor_state": self.current_state.value
            }

        self.current_operation_start_time = time.time()
        try:
            rec = self.autonomy_controller.run_autonomous_cycle(goal_id=goal_id, proposed_action=proposed_action)
            self.consecutive_errors = 0
            return {
                "goal_id": goal_id,
                "status": rec.status,
                "action_taken": rec.action_taken,
                "governor_decision": rec.governor_decision,
                "supervisor_state": self.current_state.value
            }
        except Exception as e:
            self.consecutive_errors += 1
            print(f"[RuntimeSupervisor ERROR] Autonomous cycle execution failed: {e}")
            if self.consecutive_errors >= self.watchdog.max_consecutive_errors:
                self.current_state = AgentLifecycleState.DEGRADED
                self._save_state(metadata={"error": str(e)})
            raise e
        finally:
            self.current_operation_start_time = None

    def pause(self, reason: str = "user_requested") -> RuntimeCheckpoint:
        self.current_state = AgentLifecycleState.PAUSED
        return self._save_state(metadata={"reason": reason})

    def resume(self) -> RuntimeCheckpoint:
        self.current_state = AgentLifecycleState.RUNNING
        self.consecutive_errors = 0
        return self._save_state(metadata={"reason": "resumed"})
