import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Add src and workspace to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evals.framework.scenario import EvalScenario
from evals.framework.runner import EvalRunner
from evals.framework.report import EvalReportGenerator
from evals.mocks.mocks import FakeGmail, FakeCalendar, FakeLLM
from evals.scenarios.triage_eval import TriageEvaluator
from evals.scenarios.planning_eval import PlanningEvaluator
from evals.scenarios.reliability_eval import ReliabilityEvaluator
from personal_agent.reliability.checkpoint import RecoveryCheckpointEngine
from personal_agent.telemetry.store import TelemetryStore
from personal_agent.telemetry.tracer import AgentTracer, STEP_TOOL_EXECUTION_SUCCESS
from personal_agent.telemetry.trace import TraceContext
from personal_agent.telemetry.metrics import TelemetryMetricsCalculator

class TestV14EvaluationAndReliabilityValidation(unittest.TestCase):

    def setUp(self):
        self.test_dir = "data/test_v1_4_eval"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

        self.telemetry_store = TelemetryStore(telemetry_dir=self.test_dir, log_filename="test_v1_4_traces.jsonl")
        self.tracer = AgentTracer(store=self.telemetry_store)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_eval_runner_and_report_generation(self):
        """Test EvalRunner execution and formal report formatting."""
        runner = EvalRunner()
        report = runner.generate_report()
        
        self.assertIn("V1.4 AGENT RELIABILITY REPORT", report)
        self.assertIn("Accuracy:", report)
        self.assertIn("P50 Workflow Latency:", report)
        self.assertIn("Unauthorized Executions:  0", report)

    def test_recovery_checkpoint_engine_zero_duplicate_execution(self):
        """Test RecoveryCheckpointEngine detecting incomplete trace and preventing duplicate tool execution."""
        ctx = TraceContext(trace_id="trace_crash_test_100")
        self.tracer.record_flight_step(ctx, 1, STEP_TOOL_EXECUTION_SUCCESS, {"tool": "archive_email"})

        checkpoint_engine = RecoveryCheckpointEngine(telemetry_store=self.telemetry_store)
        incomplete = checkpoint_engine.get_incomplete_traces()
        self.assertEqual(len(incomplete), 1)

        action = checkpoint_engine.evaluate_recovery_action("trace_crash_test_100")
        self.assertTrue(action["skip_tool_execution"])
        self.assertEqual(action["resume_step"], "MEMORY_UPDATED")

    def test_telemetry_metrics_calculator_percentiles(self):
        """Test TelemetryMetricsCalculator calculating P50/P95/P99 latencies and average token counts."""
        ctx = TraceContext()
        latencies = [0.01, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50]
        for lat in latencies:
            self.tracer.record_llm_call(ctx, "ollama", "PLAN_DAY", 100, 50, lat)

        metrics_calc = TelemetryMetricsCalculator(store=self.telemetry_store)
        metrics = metrics_calc.calculate_metrics()

        self.assertEqual(metrics["total_llm_calls"], 10)
        self.assertGreater(metrics["p50_latency_sec"], 0.0)
        self.assertGreater(metrics["p95_latency_sec"], metrics["p50_latency_sec"])
        self.assertEqual(metrics["avg_tokens_per_call"], 150)

    def test_triage_evaluator_metrics(self):
        """Test TriageEvaluator calculating classification accuracy and false urgent rates."""
        mock_gateway = MagicMock()
        mock_gateway.chat.return_value = {"role": "assistant", "content": "Analysis"}
        evaluator = TriageEvaluator(gateway=mock_gateway)

        res = evaluator.evaluate_dataset()
        self.assertGreaterEqual(res["accuracy"], 80.0)
        self.assertLessEqual(res["false_urgent_rate"], 10.0)

    def test_planning_evaluator_zero_conflicts(self):
        """Test PlanningEvaluator verifying zero calendar conflicts."""
        evaluator = PlanningEvaluator()
        res = evaluator.evaluate_planning_conflicts()
        self.assertEqual(res["conflicts"], 0)
        self.assertEqual(res["accuracy"], 100.0)

if __name__ == "__main__":
    unittest.main()
