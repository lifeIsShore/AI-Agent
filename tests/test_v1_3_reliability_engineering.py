import sys
import os
import time
import unittest
import shutil
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.reliability.retry import retry_with_backoff
from personal_agent.reliability.circuit_breaker import CircuitBreaker, STATE_CLOSED, STATE_OPEN, STATE_HALF_OPEN
from personal_agent.reliability.degradation import ServiceDegradationHandler
from personal_agent.state.manager import StateManager
from personal_agent.policy.proposal import ActionProposal
from personal_agent.telemetry.trace import TraceContext
from personal_agent.telemetry.store import TelemetryStore
from personal_agent.telemetry.tracer import (
    AgentTracer, STEP_REQUEST_RECEIVED, STEP_LLM_CALL, STEP_TOOL_EXECUTION_SUCCESS, STEP_TRACE_COMPLETED
)

class TestV13ReliabilityEngineering(unittest.TestCase):

    def setUp(self):
        self.test_dir = "data/test_reliability"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

        self.state_manager = StateManager(state_dir=self.test_dir)
        self.telemetry_store = TelemetryStore(telemetry_dir=self.test_dir, log_filename="test_flight.jsonl")
        self.tracer = AgentTracer(store=self.telemetry_store)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_exponential_retry_with_backoff(self):
        """Test retry_with_backoff retrying intermittent failures with metadata."""
        attempts = 0
        def intermittent_func():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Transient network error")
            return "Success Result"

        success, res, meta = retry_with_backoff(intermittent_func, max_attempts=3, base_delay=0.01)
        self.assertTrue(success)
        self.assertEqual(res, "Success Result")
        self.assertEqual(meta["attempt_count"], 3)
        self.assertEqual(meta["retry_count"], 2)

    def test_circuit_breaker_transitions(self):
        """Test CircuitBreaker state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)."""
        cb = CircuitBreaker("test_service", failure_threshold=2, cooldown_sec=0.1)
        self.assertEqual(cb.state, STATE_CLOSED)

        # Fail twice to open circuit
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, STATE_OPEN)

        # Immediate check should block execution
        can_exec, _ = cb.can_execute()
        self.assertFalse(can_exec)

        # Wait cooldown
        time.sleep(0.15)
        can_exec_after, msg = cb.can_execute()
        self.assertTrue(can_exec_after)
        self.assertEqual(cb.state, STATE_HALF_OPEN)

        # Success resets to CLOSED
        cb.record_success()
        self.assertEqual(cb.state, STATE_CLOSED)

    def test_service_degradation_handler_fallback(self):
        """Test ServiceDegradationHandler returning graceful fallback when circuit is OPEN."""
        handler = ServiceDegradationHandler()
        failing_func = MagicMock(side_effect=RuntimeError("API Outage"))

        # Trigger failure threshold
        for _ in range(3):
            handler.execute_with_protection("gmail", failing_func, fallback_value=[], max_attempts=1)

        # Circuit should now be OPEN, returning graceful fallback
        success, fallback_res, msg = handler.execute_with_protection("gmail", failing_func, fallback_value=["fallback_email"])
        self.assertFalse(success)
        self.assertEqual(fallback_res, ["fallback_email"])
        self.assertIn("temporarily degraded", msg)

    def test_atomic_state_writes_and_corrupted_json_recovery(self):
        """Test StateManager atomic file writes and automatic recovery from corrupted JSON files."""
        prop = ActionProposal(proposal_id="p1", action="archive_email", target="m1", parameters={})
        self.state_manager.save_proposals({"p1": prop})
        self.assertTrue(os.path.exists(self.state_manager.proposals_path))

        # Deliberately corrupt file
        with open(self.state_manager.proposals_path, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON TEXT ...")

        # Load back: should recover safely without raising JSONDecodeError
        loaded = self.state_manager.load_proposals()
        self.assertEqual(loaded, {})
        self.assertTrue(os.path.exists(self.state_manager.proposals_path + ".corrupted"))

    def test_flight_recorder_sequence_tracing(self):
        """Test Flight Recorder logging full 14-step decision sequence."""
        ctx = TraceContext(request_id="req_999")
        self.tracer.record_flight_step(ctx, 1, STEP_REQUEST_RECEIVED, {"prompt": "Plan day"})
        self.tracer.record_flight_step(ctx, 2, STEP_LLM_CALL, {"model": "ollama"})
        self.tracer.record_flight_step(ctx, 3, STEP_TOOL_EXECUTION_SUCCESS, {"tool": "create_calendar_event"})
        self.tracer.record_flight_step(ctx, 4, STEP_TRACE_COMPLETED, {"status": "SUCCESS"})

        recent = self.telemetry_store.get_recent_traces(limit=10)
        self.assertEqual(len(recent), 4)
        self.assertEqual(recent[0]["step"], STEP_REQUEST_RECEIVED)
        self.assertEqual(recent[3]["step"], STEP_TRACE_COMPLETED)

if __name__ == "__main__":
    unittest.main()
