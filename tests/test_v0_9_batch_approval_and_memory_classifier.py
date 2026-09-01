import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.policy.proposal import ActionProposal, STATUS_PENDING_APPROVAL, STATUS_EXECUTED, STATUS_REJECTED
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.security.audit import AuditLogger
from personal_agent.tools.registry import ToolRegistry
from personal_agent.memory.learning import MemoryLearningLoop, SCOPE_DURABLE_PREFERENCE, SCOPE_EVENT_MEMORY
from personal_agent.memory.manager import MemoryManager

class TestV09BatchApprovalAndMemoryClassifier(unittest.TestCase):

    def setUp(self):
        self.policy = PolicyEngine()
        self.registry = ToolRegistry()
        self.audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_v0_9_audit.jsonl")
        self.audit_logger.clear_logs()

        self.mock_gateway = MagicMock()
        self.memory_manager = MemoryManager(gateway=self.mock_gateway)
        self.memory_loop = MemoryLearningLoop(memory_manager=self.memory_manager)

        self.queue = ApprovalQueue(
            tool_registry=self.registry,
            audit_logger=self.audit_logger,
            memory_loop=self.memory_loop
        )

    def tearDown(self):
        self.audit_logger.clear_logs()

    def test_approve_batch_evaluates_proposals_individually(self):
        """Test that approve_batch evaluates each proposal individually through Policy Engine and ToolRegistry."""
        mock_archive = MagicMock(return_value={"status": "archived"})
        self.registry.register(
            name="archive_email",
            schema={"description": "Archive email", "parameters": {"type": "object"}},
            func=mock_archive
        )

        p1 = self.policy.create_proposal("archive_email", "email_1", {"msg_id": "email_1"}, reason="Newsletter")
        p2 = self.policy.create_proposal("archive_email", "email_2", {"msg_id": "email_2"}, reason="Digest")
        self.policy.check_proposal(p1, user_approved=False)
        self.policy.check_proposal(p2, user_approved=False)

        self.queue.add_proposal(p1)
        self.queue.add_proposal(p2)

        # Batch approval call
        results = self.queue.approve_batch([p1.proposal_id, p2.proposal_id])
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0][0])
        self.assertTrue(results[1][0])

        self.assertEqual(p1.status, STATUS_EXECUTED)
        self.assertEqual(p2.status, STATUS_EXECUTED)

        # Verify audit logs created individually for both proposals
        logs = self.audit_logger.get_recent_logs(limit=10)
        self.assertEqual(len(logs), 2)

    def test_reject_batch(self):
        """Test reject_batch safely rejects a group of pending proposals."""
        p1 = self.policy.create_proposal("trash_email", "msg_10", {"msg_id": "msg_10"})
        p2 = self.policy.create_proposal("trash_email", "msg_11", {"msg_id": "msg_11"})
        self.policy.check_proposal(p1, user_approved=False)
        self.policy.check_proposal(p2, user_approved=False)

        self.queue.add_proposal(p1)
        self.queue.add_proposal(p2)

        results = self.queue.reject_batch([p1.proposal_id, p2.proposal_id], reason="Batch reject by user")
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0][0])
        self.assertEqual(p1.status, STATUS_REJECTED)
        self.assertEqual(p2.status, STATUS_REJECTED)

    def test_memory_feedback_classifier_durable_vs_event(self):
        """Test classifying feedback into durable preference vs point-in-time event memory."""
        # 1. Point-in-time calendar event rejection -> SCOPE_EVENT_MEMORY
        prop_event = self.policy.create_proposal("create_calendar_event", "primary", {"summary": "Lecture"}, reason="Scheduled slot at 10:00 today")
        scope, mem_type, imp = self.memory_loop.classify_feedback(prop_event, "REJECTED", user_reason="User rejected this calendar slot")
        self.assertEqual(scope, SCOPE_EVENT_MEMORY)
        self.assertEqual(mem_type, "event_history")
        self.assertEqual(imp, "low")

        # 2. General rule / preference phrase -> SCOPE_DURABLE_PREFERENCE
        prop_pref = self.policy.create_proposal("archive_email", "newsletter_456", {"msg_id": "newsletter_456"}, reason="Automated tech newsletter")
        scope2, mem_type2, imp2 = self.memory_loop.classify_feedback(prop_pref, "APPROVED", user_reason="I always prefer archiving tech newsletters")
        self.assertEqual(scope2, SCOPE_DURABLE_PREFERENCE)
        self.assertEqual(mem_type2, "preference")
        self.assertEqual(imp2, "high")

    def test_event_rejection_does_not_pollute_durable_preferences(self):
        """Verify point-in-time event rejections create event_history rather than durable preferences."""
        prop = self.policy.create_proposal("create_calendar_event", "primary", {"summary": "Study session"}, reason="Slot 14:00 today")
        mem_item = self.memory_loop.record_feedback(prop, user_decision="REJECTED", user_reason="Not today")

        self.assertIsNotNone(mem_item)
        self.assertEqual(mem_item["type"], "event_history")
        self.assertEqual(mem_item["memory_scope"], SCOPE_EVENT_MEMORY)

if __name__ == "__main__":
    unittest.main()
