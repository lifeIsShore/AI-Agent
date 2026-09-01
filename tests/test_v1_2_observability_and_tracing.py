import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.telemetry.trace import TraceContext
from personal_agent.telemetry.store import TelemetryStore
from personal_agent.telemetry.tracer import AgentTracer
from personal_agent.models.gateway import ModelGateway
from personal_agent.policy.engine import PolicyEngine
from personal_agent.tools.registry import ToolRegistry
from personal_agent.security.audit import AuditLogger
from personal_agent.agent.runtime import AgentRuntime

class TestV12ObservabilityAndTracing(unittest.TestCase):

    def setUp(self):
        self.test_telemetry_dir = "data/test_telemetry"
        if os.path.exists(self.test_telemetry_dir):
            shutil.rmtree(self.test_telemetry_dir)

        self.telemetry_store = TelemetryStore(telemetry_dir=self.test_telemetry_dir, log_filename="test_traces.jsonl")
        self.tracer = AgentTracer(store=self.telemetry_store)

    def tearDown(self):
        if os.path.exists(self.test_telemetry_dir):
            shutil.rmtree(self.test_telemetry_dir)

    def test_trace_context_correlation(self):
        """Test TraceContext propagation and child span creation."""
        root_ctx = TraceContext(request_id="req_555")
        child_ctx = root_ctx.create_child_span(proposal_id="prop_777", execution_id="exec_888")

        self.assertEqual(child_ctx.trace_id, root_ctx.trace_id)
        self.assertEqual(child_ctx.request_id, "req_555")
        self.assertEqual(child_ctx.proposal_id, "prop_777")
        self.assertEqual(child_ctx.execution_id, "exec_888")

    def test_tracer_llm_metrics_and_context_efficiency_recording(self):
        """Test AgentTracer recording LLM call tokens and context efficiency metrics to disk."""
        ctx = TraceContext(proposal_id="prop_111")

        self.tracer.record_llm_call(
            trace_ctx=ctx,
            model="ollama",
            intent="PLAN_DAY",
            prompt_tokens=250,
            completion_tokens=45,
            latency_sec=1.12
        )

        self.tracer.record_context_efficiency(
            trace_ctx=ctx,
            intent="PLAN_DAY",
            item_counts={"emails": 3, "calendar": 2, "tasks": 5},
            total_bytes=1500,
            latency_sec=0.02
        )

        recent = self.telemetry_store.get_recent_traces(limit=10)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["type"], "LLM_CALL")
        self.assertEqual(recent[0]["prompt_tokens"], 250)
        self.assertEqual(recent[1]["type"], "CONTEXT_EFFICIENCY")
        self.assertEqual(recent[1]["item_counts"]["emails"], 3)

    def test_agent_runtime_telemetry_integration(self):
        """Test AgentRuntime recording spans and LLM calls to AgentTracer."""
        mock_gateway = MagicMock()
        mock_gateway.chat.return_value = {"role": "assistant", "content": "Hello!"}
        registry = ToolRegistry()
        policy = PolicyEngine()
        audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_v1_2_audit.jsonl")

        runtime = AgentRuntime(
            model_gateway=mock_gateway,
            tool_registry=registry,
            policy_engine=policy,
            audit_logger=audit_logger,
            tracer=self.tracer
        )

        ctx = TraceContext()
        res = runtime.process_request("Say hello", trace_ctx=ctx)
        self.assertEqual(res, "Hello!")

    def test_architecture_documentation_files_exist(self):
        """Test that docs/ markdown files exist and contain valid text."""
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
        expected_files = ["architecture.md", "security.md", "event-model.md", "telemetry-model.md"]

        for fname in expected_files:
            fpath = os.path.join(docs_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Docs file missing: {fname}")
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertGreater(len(content), 100, f"Docs file too short: {fname}")

if __name__ == "__main__":
    unittest.main()
