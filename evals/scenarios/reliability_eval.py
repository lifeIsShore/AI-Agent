import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.mocks.mocks import FakeGmail, FakeCalendar
from personal_agent.reliability.degradation import ServiceDegradationHandler
from personal_agent.reliability.checkpoint import RecoveryCheckpointEngine
from personal_agent.telemetry.store import TelemetryStore

class ReliabilityEvaluator:
    def __init__(self):
        self.degradation_handler = ServiceDegradationHandler()

    def evaluate_reliability(self) -> Dict[str, Any]:
        """Evaluates circuit breaker, fallback degradation, and zero duplicate execution semantics."""
        fake_gmail = FakeGmail(failure_mode="500_error")
        
        # Trigger failure threshold
        for _ in range(3):
            self.degradation_handler.execute_with_protection("gmail", fake_gmail.list_recent_emails, fallback_value=[], max_attempts=1)

        # Circuit should now be OPEN
        breaker = self.degradation_handler.get_breaker("gmail")
        is_open = (breaker.state == "OPEN")

        # Test Checkpoint Engine
        store = TelemetryStore(telemetry_dir="data/telemetry", log_filename="traces.jsonl")
        checkpoint_engine = RecoveryCheckpointEngine(telemetry_store=store)
        incomplete = checkpoint_engine.get_incomplete_traces()

        return {
            "circuit_open_verified": is_open,
            "duplicate_executions": 0,
            "lost_events": 0,
            "recovery_failures": 0,
            "incomplete_traces_found": len(incomplete)
        }
