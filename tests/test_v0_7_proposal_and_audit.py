import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.policy.proposal import ActionProposal
from personal_agent.policy.engine import PolicyEngine, PermissionLevel
from personal_agent.security.audit import AuditLogger
from personal_agent.agent.runtime import AgentRuntime
from personal_agent.tools.registry import ToolRegistry

class TestV07ProposalAndAudit(unittest.TestCase):

    def setUp(self):
        self.policy = PolicyEngine()
        self.audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_audit.jsonl")
        self.audit_logger.clear_logs()

    def tearDown(self):
        self.audit_logger.clear_logs()

    def test_action_proposal_model(self):
        """Test ActionProposal model creation and dictionary serialization."""
        prop = ActionProposal(
            action="archive_email",
            target="msg_123",
            parameters={"msg_id": "msg_123"},
            reason="Promotional newsletter email",
            confidence=0.97,
            risk_level="MEDIUM",
            required_permission="MODIFY"
        )

        self.assertTrue(prop.proposal_id.startswith("prop_"))
        self.assertEqual(prop.action, "archive_email")

        # Test dictionary serialization
        prop_dict = prop.to_dict()
        self.assertEqual(prop_dict["target"], "msg_123")
        self.assertEqual(prop_dict["risk_level"], "MEDIUM")

        # Test reconstruction
        reconstructed = ActionProposal.from_dict(prop_dict)
        self.assertEqual(reconstructed.proposal_id, prop.proposal_id)
        self.assertEqual(reconstructed.action, prop.action)

    def test_policy_engine_proposal_evaluation(self):
        """Test PolicyEngine proposal checking and risk classification."""
        # 1. READ_ONLY -> LOW risk, auto-approved
        prop_read = self.policy.create_proposal(action="get_today_events", target="calendar", parameters={})
        self.assertEqual(prop_read.risk_level, "LOW")
        allowed, reason = self.policy.check_proposal(prop_read)
        self.assertTrue(allowed)
        self.assertEqual(prop_read.status, "AUTO_APPROVED")

        # 2. MODIFY (archive_email) -> MEDIUM risk, blocked without approval -> PENDING_APPROVAL
        prop_mod = self.policy.create_proposal(action="archive_email", target="msg_1", parameters={"msg_id": "msg_1"})
        self.assertEqual(prop_mod.risk_level, "MEDIUM")
        allowed, reason = self.policy.check_proposal(prop_mod, user_approved=False)
        self.assertFalse(allowed)
        self.assertEqual(prop_mod.status, "PENDING_APPROVAL")

        # 3. MODIFY with user approval -> APPROVED
        allowed, reason = self.policy.check_proposal(prop_mod, user_approved=True)
        self.assertTrue(allowed)
        self.assertEqual(prop_mod.status, "APPROVED")

        # 4. HIGH risk action (trash_email) -> HIGH risk level
        prop_high = self.policy.create_proposal(action="trash_email", target="msg_2", parameters={"msg_id": "msg_2"})
        self.assertEqual(prop_high.risk_level, "HIGH")

    def test_audit_logger_persistence(self):
        """Test writing and reading structured audit logs."""
        prop = self.policy.create_proposal(
            action="create_calendar_event",
            target="primary",
            parameters={"summary": "Thesis work", "start_time": "14:00", "end_time": "15:00"},
            reason="Allocated into free afternoon slot"
        )

        entry = self.audit_logger.log_proposal(
            proposal=prop,
            policy_decision="Allowed by explicit human approval",
            user_approved=True,
            execution_status="SUCCESS",
            execution_result={"event_id": "ev_999"},
            latency_sec=0.15
        )

        self.assertEqual(entry["action"], "create_calendar_event")
        self.assertEqual(entry["execution_status"], "SUCCESS")

        # Read back from audit file
        logs = self.audit_logger.get_recent_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["proposal_id"], prop.proposal_id)
        self.assertEqual(logs[0]["action"], "create_calendar_event")

        # Test action filter
        filtered = self.audit_logger.get_recent_logs(limit=10, action_filter="create_calendar_event")
        self.assertEqual(len(filtered), 1)

        empty_filter = self.audit_logger.get_recent_logs(limit=10, action_filter="non_existent")
        self.assertEqual(len(empty_filter), 0)

    def test_agent_runtime_audit_integration(self):
        """Test end-to-end AgentRuntime tool call execution with audit logging."""
        mock_gateway = MagicMock()
        registry = ToolRegistry()

        # Register a test tool
        mock_func = MagicMock(return_value="Success Result")
        registry.register(
            name="get_current_time",
            schema={"description": "Get current time", "parameters": {"type": "object"}},
            func=mock_func
        )

        # Mock LLM response asking to call get_current_time
        mock_gateway.chat.side_effect = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "get_current_time",
                            "arguments": {}
                        }
                    }
                ]
            },
            {"role": "assistant", "content": "The time has been checked."}
        ]

        runtime = AgentRuntime(
            model_gateway=mock_gateway,
            tool_registry=registry,
            policy_engine=self.policy,
            audit_logger=self.audit_logger
        )

        resp = runtime.process_request("What time is it?")
        self.assertEqual(resp, "The time has been checked.")

        # Verify audit log was recorded
        logs = self.audit_logger.get_recent_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["action"], "get_current_time")
        self.assertEqual(logs[0]["execution_status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
