import sys
import os
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.runtime.lifecycle import LifecycleManager, AgentLifecycleState, RuntimeCheckpoint
from personal_agent.runtime.heartbeat import HeartbeatMonitor, HeartbeatSnapshot
from personal_agent.runtime.watchdog import RuntimeWatchdog, WatchdogStatus
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.runtime.shutdown import ShutdownHandler
from personal_agent.autonomy.governor import AutonomyGovernor

class TestV31PersistentAutonomousOperations(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_1_")
        self.supervisor = RuntimeSupervisor(storage_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_normal_heartbeat_running_state(self):
        """Test 1: Normal heartbeat emission under RUNNING state."""
        self.supervisor.start()
        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.RUNNING)

        hb = self.supervisor.emit_heartbeat(active_goal_id="goal_100", current_op="checking_inbox", latency_ms=45.2)
        self.assertIsNotNone(hb)
        self.assertEqual(hb.state, AgentLifecycleState.RUNNING.value)
        self.assertEqual(hb.active_goal_id, "goal_100")
        self.assertEqual(hb.current_operation, "checking_inbox")
        self.assertTrue(self.supervisor.heartbeat_monitor.is_healthy())

    def test_watchdog_detects_stalled_loop(self):
        """Test 2: Watchdog detects artificially stalled execution loop."""
        self.supervisor.start()
        watchdog = RuntimeWatchdog(max_execution_duration_sec=0.1) # 100ms threshold for test
        
        # Simulate long-running operation starting in past
        past_start_time = time.time() - 0.5
        hb = self.supervisor.heartbeat_monitor.record_heartbeat(state=AgentLifecycleState.RUNNING.value)
        
        status = watchdog.evaluate_health(heartbeat=hb, operation_start_time=past_start_time)
        self.assertFalse(status.is_healthy)
        self.assertEqual(status.issue_type, "STALLED_EXECUTION")
        self.assertEqual(status.recommended_state, AgentLifecycleState.DEGRADED.value)

    def test_runtime_exception_triggers_safe_recovery(self):
        """Test 3: Runtime exception triggers safe recovery procedure."""
        self.supervisor.start()
        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.RUNNING)

        # Trigger recovery
        success = self.supervisor.attempt_recovery(simulate_failure=False)
        self.assertTrue(success)
        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.RUNNING)

    def test_repeated_failures_trigger_degraded(self):
        """Test 4: Repeated cycle failures transition state to DEGRADED."""
        self.supervisor.start()
        watchdog = RuntimeWatchdog(max_consecutive_errors=2)
        
        hb = self.supervisor.heartbeat_monitor.record_heartbeat(
            state=AgentLifecycleState.RUNNING.value,
            consecutive_errors=3
        )
        status = watchdog.evaluate_health(heartbeat=hb)
        self.assertFalse(status.is_healthy)
        self.assertEqual(status.issue_type, "REPEATED_FAILURES")
        self.assertEqual(status.recommended_state, AgentLifecycleState.DEGRADED.value)

    def test_process_restart_restores_state(self):
        """Test 5: Process restart restores runtime state and active goal from atomic checkpoint."""
        self.supervisor.start()
        self.supervisor.active_goal_id = "goal_semester_prep"
        self.supervisor.active_workflows = ["wf_calendar_sync", "wf_email_triage"]
        self.supervisor.pause(reason="maintenance")

        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.PAUSED)

        # Re-instantiate supervisor (simulating process restart)
        restarted_supervisor = RuntimeSupervisor(storage_dir=self.test_dir)
        self.assertEqual(restarted_supervisor.current_state, AgentLifecycleState.PAUSED)
        self.assertEqual(restarted_supervisor.active_goal_id, "goal_semester_prep")
        self.assertEqual(restarted_supervisor.active_workflows, ["wf_calendar_sync", "wf_email_triage"])

    def test_clean_shutdown_on_signal(self):
        """Test 6: Clean shutdown on signal flushes logs and saves final SHUTTING_DOWN checkpoint."""
        self.supervisor.start()
        shutdown_handler = ShutdownHandler(self.supervisor)
        
        final_chk = shutdown_handler.initiate_shutdown(reason="SIGINT_received")
        self.assertTrue(shutdown_handler.is_shutdown_complete)
        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.SHUTTING_DOWN)
        self.assertEqual(final_chk.state, AgentLifecycleState.SHUTTING_DOWN.value)

    def test_corrupted_checkpoint_safe_fallback(self):
        """Test 7: Corrupted checkpoint file triggers safe default fallback without crashing."""
        lifecycle = LifecycleManager(storage_dir=self.test_dir)
        
        # Corrupt file with malformed JSON
        with open(lifecycle.filepath, 'w', encoding='utf-8') as f:
            f.write("{corrupt_json_structure: [unclosed")

        # Load checkpoint should not raise Exception, should return safe fallback
        chk = lifecycle.load_checkpoint()
        self.assertIsNotNone(chk)
        self.assertEqual(chk.state, AgentLifecycleState.STARTING.value)
        self.assertEqual(chk.metadata.get("reason"), "corrupted_checkpoint_fallback")

    def test_failed_recovery_remains_paused(self):
        """Test 8: Failed recovery procedure forces supervisor to remain in PAUSED state."""
        self.supervisor.start()
        
        # Attempt recovery with simulated failure
        success = self.supervisor.attempt_recovery(simulate_failure=True)
        self.assertFalse(success)
        self.assertEqual(self.supervisor.current_state, AgentLifecycleState.PAUSED)

    def test_autonomous_action_blocked_during_recovery(self):
        """Test 9: Hard security invariant: autonomous action requests during RECOVERING/PAUSED are strictly blocked."""
        self.supervisor.start()
        
        # 1. Action allowed while RUNNING
        res_running = self.supervisor.execute_autonomous_action(goal_id="goal_100", proposed_action="get_current_time")
        self.assertEqual(res_running["status"], "SUCCESS")

        # 2. Transition supervisor to RECOVERING
        self.supervisor.current_state = AgentLifecycleState.RECOVERING
        res_recovering = self.supervisor.execute_autonomous_action(goal_id="goal_100", proposed_action="get_current_time")
        self.assertEqual(res_recovering["status"], "BLOCKED")
        self.assertIn("must be RUNNING", res_recovering["reason"])

        # 3. Direct AutonomyGovernor check with non-RUNNING state
        governor = AutonomyGovernor()
        auth_ok, auth_msg = governor.authorize_action("get_current_time", "system", "LOW", "LEVEL_3_BOUNDED_AUTO", supervisor_state="PAUSED")
        self.assertFalse(auth_ok)
        self.assertIn("Supervisor state is 'PAUSED'", auth_msg)

if __name__ == "__main__":
    unittest.main()
