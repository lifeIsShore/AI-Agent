import sys
import os
import unittest
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.security.principal import Principal, PRINCIPAL_USER, PRINCIPAL_SCHEDULER
from personal_agent.security.identity import IdentityProvider
from personal_agent.security.secrets import SecretStore
from personal_agent.security.credentials import CredentialBroker
from personal_agent.policy.capabilities import resolve_capability, get_target_aware_capability_risk, validate_capability_authorization, RISK_HIGH, RISK_CRITICAL
from personal_agent.policy.authorization import AuthorizationDecision, DECISION_ALLOW, DECISION_DENY, DECISION_REQUIRE_APPROVAL
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.tools.registry import ToolRegistry
from personal_agent.security.audit import AuditLogger
from personal_agent.state.manager import StateManager

class TestV16CapabilitySecretsAndIdentity(unittest.TestCase):

    def setUp(self):
        self.test_dir = "data/test_v1_6_sec"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

        self.secret_store = SecretStore()
        self.credential_broker = CredentialBroker(secret_store=self.secret_store)
        self.policy = PolicyEngine()
        self.audit_logger = AuditLogger(log_dir=self.test_dir, log_filename="test_v1_6_audit.jsonl")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_principal_identity_resolution(self):
        """Test Principal identity construction and type checks."""
        user_p = IdentityProvider.get_user_principal("user_ahmet")
        sched_p = IdentityProvider.get_scheduler_principal("inbox_triage_job")

        self.assertTrue(user_p.is_user())
        self.assertTrue(sched_p.is_scheduler())
        self.assertEqual(user_p.principal_id, "user_ahmet")

    def test_scheduler_principal_restricted_capabilities(self):
        """Test that scheduler principal cannot execute high-risk write capabilities."""
        sched_p = IdentityProvider.get_scheduler_principal()
        allowed, msg = validate_capability_authorization("gmail.trash", principal=sched_p)
        self.assertFalse(allowed)
        self.assertIn("restricted", msg.lower())

    def test_credential_broker_secrets_isolation(self):
        """Test CredentialBroker isolates OAuth tokens and secrets boundary."""
        cred = self.credential_broker.get_tool_credential("gmail", "gmail.read")
        self.assertIsNotNone(cred)
        self.assertEqual(cred["service"], "gmail")
        self.assertIn("access_token", cred)
        # Verify secret tokens are not bare text in credentials
        self.assertNotIn("GOOGLE_REFRESH_TOKEN", str(cred))

    def test_target_aware_capability_risk_escalation(self):
        """Test multi-factor risk escalation for broad target scopes."""
        risk_single = get_target_aware_capability_risk("gmail.archive", "msg_123")
        risk_broad = get_target_aware_capability_risk("gmail.archive", "inbox_all")

        self.assertEqual(risk_single, "MEDIUM")
        self.assertEqual(risk_broad, "HIGH")

    def test_structured_authorization_decision_object(self):
        """Test PolicyEngine returns structured AuthorizationDecision objects."""
        prop = self.policy.create_proposal("archive_email", "msg_123", {"msg_id": "msg_123"})
        user_p = IdentityProvider.get_user_principal()
        
        decision = self.policy.evaluate_authorization(prop, principal=user_p, user_approved=False)
        self.assertIsInstance(decision, AuthorizationDecision)
        self.assertEqual(decision.decision, DECISION_REQUIRE_APPROVAL)
        self.assertEqual(decision.principal_id, "user_ahmet")
        self.assertEqual(decision.capability, "gmail.archive")

    def test_expanded_audit_logging_fields(self):
        """Test AuditLogger records 15-field flight audit logs."""
        prop = self.policy.create_proposal("archive_email", "msg_123", {"msg_id": "msg_123"})
        log_entry = self.audit_logger.log_proposal(
            proposal=prop,
            policy_decision="Allowed by explicit approval",
            user_approved=True,
            execution_status="SUCCESS",
            principal_id="user_ahmet",
            credential_scope="OAuth2"
        )

        self.assertEqual(log_entry["principal_id"], "user_ahmet")
        self.assertEqual(log_entry["capability"], "gmail.archive")
        self.assertIn("parameters_hash", log_entry)

if __name__ == "__main__":
    unittest.main()
