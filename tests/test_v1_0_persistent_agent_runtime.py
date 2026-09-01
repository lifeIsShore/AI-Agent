import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.state.manager import StateManager
from personal_agent.policy.proposal import ActionProposal, STATUS_PENDING_APPROVAL, STATUS_EXECUTED
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.security.audit import AuditLogger
from personal_agent.tools.registry import ToolRegistry
from personal_agent.scheduler.job import Job
from personal_agent.scheduler.registry import JobRegistry
from personal_agent.scheduler.scheduler import AgentScheduler
from personal_agent.agent.runtime import AgentRuntime

class TestV10PersistentAgentRuntime(unittest.TestCase):

    def setUp(self):
        self.test_state_dir = "data/test_state"
        if os.path.exists(self.test_state_dir):
            shutil.rmtree(self.test_state_dir)
            
        self.state_manager = StateManager(state_dir=self.test_state_dir)
        self.policy = PolicyEngine()
        self.registry = ToolRegistry()
        self.audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_v1_0_audit.jsonl")
        self.audit_logger.clear_logs()

    def tearDown(self):
        if os.path.exists(self.test_state_dir):
            shutil.rmtree(self.test_state_dir)
        self.audit_logger.clear_logs()

    def test_state_manager_disk_persistence(self):
        """Test StateManager saving and loading proposals and runtime state to disk."""
        prop = self.policy.create_proposal("archive_email", "msg_100", {"msg_id": "msg_100"}, reason="Triage archive")
        proposals_map = {prop.proposal_id: prop}

        # Save to disk
        self.state_manager.save_proposals(proposals_map)
        self.assertTrue(os.path.exists(self.state_manager.proposals_path))

        # Load back from disk
        loaded = self.state_manager.load_proposals()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[prop.proposal_id].action, "archive_email")
        self.assertEqual(loaded[prop.proposal_id].target, "msg_100")

    def test_approval_queue_restart_recovery(self):
        """Test ApprovalQueue restoring PENDING_APPROVAL state after process restart."""
        queue1 = ApprovalQueue(tool_registry=self.registry, audit_logger=self.audit_logger, state_manager=self.state_manager)
        prop = self.policy.create_proposal("create_calendar_event", "primary", {"summary": "Meeting"}, reason="Schedule block")
        self.policy.check_proposal(prop, user_approved=False)
        queue1.add_proposal(prop)

        # Simulate agent process restart by instantiating new ApprovalQueue reading from same StateManager
        queue2 = ApprovalQueue(tool_registry=self.registry, audit_logger=self.audit_logger, state_manager=self.state_manager)
        pending = queue2.list_pending()

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].proposal_id, prop.proposal_id)
        self.assertEqual(pending[0].status, STATUS_PENDING_APPROVAL)

    def test_agent_scheduler_and_job_execution(self):
        """Test AgentScheduler registering jobs, running ticks, and saving runtime state."""
        mock_handler = MagicMock(return_value={"result": "briefing generated"})
        job = Job(
            job_id="test_morning_briefing",
            name="Morning Briefing Test",
            interval_minutes=30,
            handler=mock_handler,
            enabled=True
        )

        scheduler = AgentScheduler(state_manager=self.state_manager)
        scheduler.register_job(job)

        self.assertTrue(job.is_due())

        # Run scheduler daemon tick
        results = scheduler.run_daemon_tick()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "SUCCESS")
        mock_handler.assert_called_once()
        self.assertFalse(job.is_due()) # Should not be due immediately after execution

        # Verify runtime state file created
        runtime_state = self.state_manager.load_runtime_state()
        self.assertEqual(len(runtime_state.get("jobs", [])), 1)
        self.assertEqual(runtime_state["jobs"][0]["job_id"], "test_morning_briefing")

    def test_agent_runtime_idempotency_protection(self):
        """Test that AgentRuntime prevents duplicate tool execution for identical proposals."""
        mock_gateway = MagicMock()
        mock_tool_func = MagicMock(return_value="Action Completed Successfully")

        self.registry.register(
            name="mark_read",
            schema={"description": "Mark email read", "parameters": {"type": "object"}},
            func=mock_tool_func
        )

        # Mock LLM requesting mark_read twice
        mock_gateway.chat.side_effect = [
            {"role": "assistant", "tool_calls": [{"function": {"name": "mark_read", "arguments": {"msg_id": "m55"}}}]},
            {"role": "assistant", "content": "Done marking email 1."},
            {"role": "assistant", "tool_calls": [{"function": {"name": "mark_read", "arguments": {"msg_id": "m55"}}}]},
            {"role": "assistant", "content": "Done marking email 2."}
        ]

        runtime = AgentRuntime(
            model_gateway=mock_gateway,
            tool_registry=self.registry,
            policy_engine=self.policy,
            audit_logger=self.audit_logger
        )

        # 1st Call
        resp1 = runtime.process_request("Mark email m55 read", user_approved=True)
        self.assertEqual(mock_tool_func.call_count, 1)

        # 2nd Call with identical tool request
        resp2 = runtime.process_request("Mark email m55 read again", user_approved=True)
        # Mock function count SHOULD STILL BE 1 due to Idempotency Cache Hit!
        self.assertEqual(mock_tool_func.call_count, 1)

if __name__ == "__main__":
    unittest.main()
