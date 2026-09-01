import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.policy.proposal import (
    ActionProposal, STATUS_PROPOSED, STATUS_AUTO_APPROVED, STATUS_PENDING_APPROVAL, STATUS_APPROVED, STATUS_REJECTED, STATUS_EXECUTED
)
from personal_agent.policy.engine import PolicyEngine, PermissionLevel
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.security.audit import AuditLogger
from personal_agent.tools.registry import ToolRegistry
from personal_agent.state.manager import StateManager
from personal_agent.memory.learning import MemoryLearningLoop
from personal_agent.memory.manager import MemoryManager

class TestV08ApprovalAndMemoryLoop(unittest.TestCase):

    def setUp(self):
        self.test_dir = "data/test_v0_8_state"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

        self.policy = PolicyEngine()
        self.registry = ToolRegistry()
        self.audit_logger = AuditLogger(log_dir=self.test_dir, log_filename="test_v0_8_audit.jsonl")
        self.state_manager = StateManager(state_dir=self.test_dir)

        # Mock memory store & manager
        self.mock_gateway = MagicMock()
        self.memory_manager = MemoryManager(gateway=self.mock_gateway)
        self.memory_loop = MemoryLearningLoop(memory_manager=self.memory_manager)

        self.queue = ApprovalQueue(
            tool_registry=self.registry,
            audit_logger=self.audit_logger,
            memory_loop=self.memory_loop,
            state_manager=self.state_manager
        )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_status_lifecycle_refinement(self):
        """Test distinction between AUTO_APPROVED, PENDING_APPROVAL, and DENIED in PolicyEngine."""
        # 1. READ_ONLY -> STATUS_AUTO_APPROVED
        prop_read = self.policy.create_proposal("get_today_events", "calendar", {})
        allowed, reason = self.policy.check_proposal(prop_read)
        self.assertTrue(allowed)
        self.assertEqual(prop_read.status, STATUS_AUTO_APPROVED)

        # 2. MODIFY -> STATUS_PENDING_APPROVAL (Not generic DENIED)
        prop_mod = self.policy.create_proposal("archive_email", "msg_123", {"msg_id": "msg_123"})
        allowed, reason = self.policy.check_proposal(prop_mod, user_approved=False)
        self.assertFalse(allowed)
        self.assertEqual(prop_mod.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

        # 3. User Approved -> STATUS_APPROVED
        allowed, reason = self.policy.check_proposal(prop_mod, user_approved=True)
        self.assertTrue(allowed)
        self.assertEqual(prop_mod.status, STATUS_APPROVED)

    def test_approval_queue_approve_and_edit(self):
        """Test approving and editing parameters of a proposal in ApprovalQueue."""
        mock_tool_func = MagicMock(return_value={"status": "success", "event_id": "ev_100"})
        self.registry.register(
            name="create_calendar_event",
            schema={"description": "Create event", "parameters": {"type": "object"}},
            func=mock_tool_func
        )

        prop = self.policy.create_proposal(
            action="create_calendar_event",
            target="primary",
            parameters={"summary": "Thesis draft", "start_time": "10:00", "end_time": "11:00"},
            reason="Allocated into free slot"
        )
        self.policy.check_proposal(prop, user_approved=False)
        self.queue.add_proposal(prop)

        # Verify pending list
        pending = self.queue.list_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].proposal_id, prop.proposal_id)

        # User edits start_time to 14:00 and approves
        success, msg, res = self.queue.approve_proposal(
            proposal_id=prop.proposal_id,
            edited_params={"start_time": "14:00", "end_time": "15:00"}
        )

        self.assertTrue(success)
        self.assertEqual(prop.status, STATUS_EXECUTED)
        self.assertEqual(prop.parameters["start_time"], "14:00")
        mock_tool_func.assert_called_once_with(summary="Thesis draft", start_time="14:00", end_time="15:00")

        # Verify audit record
        logs = self.audit_logger.get_recent_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["execution_status"], "SUCCESS")

    def test_approval_queue_rejection(self):
        """Test rejecting a proposal in ApprovalQueue."""
        prop = self.policy.create_proposal(
            action="trash_email",
            target="msg_555",
            parameters={"msg_id": "msg_555"},
            reason="Move email to trash"
        )
        self.policy.check_proposal(prop, user_approved=False)
        self.queue.add_proposal(prop)

        success, msg = self.queue.reject_proposal(proposal_id=prop.proposal_id, reason="Don't delete this email")
        self.assertTrue(success)
        self.assertEqual(prop.status, STATUS_REJECTED)

        # Verify audit record
        logs = self.audit_logger.get_recent_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["execution_status"], "REJECTED")

    def test_memory_learning_loop(self):
        """Test recording approval and rejection feedback into MemoryStore."""
        prop = self.policy.create_proposal(
            action="archive_email",
            target="newsletter_123",
            parameters={"msg_id": "newsletter_123"},
            reason="Weekly tech digest"
        )

        # Record approval feedback
        mem_item = self.memory_loop.record_feedback(proposal=prop, user_decision="APPROVED")
        self.assertIsNotNone(mem_item)
        self.assertIn("User approved action 'archive_email'", mem_item["content"])

        # Record rejection feedback
        prop_rej = self.policy.create_proposal("trash_email", "receipt_456", {})
        mem_rej = self.memory_loop.record_feedback(proposal=prop_rej, user_decision="REJECTED", user_reason="Keep receipts")
        self.assertIsNotNone(mem_rej)
        self.assertIn("User rejected action 'trash_email'", mem_rej["content"])

    def test_learned_memories_do_not_bypass_policy_engine(self):
        """Verify that learned memory preferences NEVER bypass PolicyEngine approval gates for MODIFY actions."""
        # Add a learned memory preference
        self.memory_manager.add_explicit_memory(
            memory_type="preference",
            content="User usually approves archiving newsletters from LinkedIn."
        )

        # Check a new MODIFY proposal for archiving a LinkedIn email
        prop = self.policy.create_proposal("archive_email", "linkedin_msg", {"msg_id": "linkedin_msg"})
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        # Policy Engine MUST STILL REQUIRE HUMAN AUTHORIZATION!
        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
