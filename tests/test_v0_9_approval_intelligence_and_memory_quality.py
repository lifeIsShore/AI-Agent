import sys
import os
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.policy.proposal import (
    ActionProposal, STATUS_PROPOSED, STATUS_PENDING_APPROVAL, STATUS_EXECUTED, STATUS_EXPIRED
)
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.security.audit import AuditLogger
from personal_agent.tools.registry import ToolRegistry
from personal_agent.memory.learning import (
    MemoryLearningLoop, PREFERENCE_SCOPE_SENDER, PREFERENCE_SCOPE_CATEGORY, PREFERENCE_SCOPE_ACTION
)
from personal_agent.memory.manager import MemoryManager

class TestV09ApprovalIntelligenceAndMemoryQuality(unittest.TestCase):

    def setUp(self):
        self.policy = PolicyEngine()
        self.registry = ToolRegistry()
        self.audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_v0_9_intel_audit.jsonl")
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

    def test_proposal_expiration_ttl(self):
        """Test that expired proposals transition to STATUS_EXPIRED and block execution."""
        # Create proposal expired 10 minutes ago
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        prop = ActionProposal(
            action="archive_email",
            target="msg_expired",
            parameters={"msg_id": "msg_expired"},
            expires_at=past_time
        )
        
        self.assertTrue(prop.is_expired())

        allowed, reason = self.policy.check_proposal(prop)
        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_EXPIRED)
        self.assertIn("has expired", reason)

        # Attempt to approve via queue
        self.queue.add_proposal(prop)
        success, msg, res = self.queue.approve_proposal(prop.proposal_id)
        self.assertFalse(success)
        self.assertIn("has expired", msg)

    def test_explainability_chain_why_proposed(self):
        """Test proposal details explainability chain retrieval."""
        why_chain = [
            "1. Sender is an automated newsletter service.",
            "2. Message contains promotional unsubscribe headers.",
            "3. User previously approved archiving tech digests."
        ]
        prop = self.policy.create_proposal(
            action="archive_email",
            target="msg_newsletter",
            parameters={"msg_id": "msg_newsletter"},
            reason="Automated digest recommendation",
            why_proposed=why_chain
        )
        self.queue.add_proposal(prop)

        details = self.queue.get_proposal_details(prop.proposal_id)
        self.assertIsNotNone(details)
        self.assertEqual(len(details["why_proposed"]), 3)
        self.assertEqual(details["why_proposed"][0], "1. Sender is an automated newsletter service.")

    def test_stale_target_validation(self):
        """Test that stale target validation prevents executing proposals whose targets changed."""
        mock_func = MagicMock(return_value={"status": "archived"})
        self.registry.register("archive_email", {"description": "Archive"}, mock_func)

        prop = self.policy.create_proposal(
            action="archive_email",
            target="msg_999",
            parameters={"msg_id": "msg_999"},
            target_checksum="hash_original_v1"
        )
        self.policy.check_proposal(prop, user_approved=False)
        self.queue.add_proposal(prop)

        # Mock target validator failing due to state change
        def mock_validator(target, checksum):
            return False, "Email #msg_999 was deleted by user in Gmail web UI"

        success, msg, res = self.queue.approve_proposal(prop.proposal_id, target_validator=mock_validator)
        self.assertFalse(success)
        self.assertIn("Target state changed", msg)

    def test_scoped_preference_confidence_and_decay(self):
        """Test inference of granular preference scopes, confidence updates, and time decay."""
        prop = self.policy.create_proposal(
            action="archive_email",
            target="email_123",
            parameters={"sender": "alerts@jobboard.com", "category": "job_digest"},
            reason="Weekly tech digest"
        )

        scope, condition = self.memory_loop.infer_preference_scope(prop)
        self.assertEqual(scope, PREFERENCE_SCOPE_SENDER)
        self.assertEqual(condition["sender"], "alerts@jobboard.com")

        # Confidence updates
        conf_start = 0.50
        conf_after_pos = self.memory_loop.update_confidence(conf_start, positive_signal=True)
        self.assertGreater(conf_after_pos, conf_start)

        conf_after_neg = self.memory_loop.update_confidence(conf_after_pos, positive_signal=False)
        self.assertLess(conf_after_neg, conf_after_pos)

        # Decay over 30 days
        decayed = self.memory_loop.apply_decay(1.0, days_elapsed=30.0)
        self.assertLess(decayed, 1.0)

    def test_hard_security_invariant_confidence_never_bypasses_policy(self):
        """Security Invariant Verification: High preference confidence MUST NEVER bypass Policy Engine human authorization for MODIFY actions."""
        # Store high confidence preference
        self.memory_manager.store.add_memory(
            memory_type="preference",
            content="User archiving newsletter (100% confidence)",
            confidence=1.0,
            metadata={"confidence": 1.0, "observations": 50}
        )

        # Check proposal for archive_email (MODIFY action)
        prop = self.policy.create_proposal("archive_email", "msg_777", {"msg_id": "msg_777"}, confidence=1.0)
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        # MUST STRICTLY STILL BE PENDING_APPROVAL / DENIED
        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
