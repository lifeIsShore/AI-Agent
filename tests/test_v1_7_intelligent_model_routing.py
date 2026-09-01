import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.security.sanitizer import redact_credentials
from personal_agent.models.registry import ModelRegistry
from personal_agent.models.scoring import ComplexityScorer, INTENT_GET_TIME, INTENT_PLAN_DAY
from personal_agent.models.router import ModelRouter, ModelDecision
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import STATUS_PENDING_APPROVAL

class TestV17IntelligentModelRouting(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistry()
        self.scorer = ComplexityScorer()
        self.router = ModelRouter(registry=self.registry, scorer=self.scorer)
        self.policy = PolicyEngine()

    def test_credential_redaction_sanitizer(self):
        """Test V1.6.1 credential redaction across strings, dicts, and exceptions."""
        secret_dict = {
            "access_token": "bearer_gmail_12345678",
            "google_refresh_token": "mock_google_refresh_token_secret",
            "user_prompt": "Hello world"
        }

        sanitized = redact_credentials(secret_dict)
        self.assertEqual(sanitized["access_token"], "[REDACTED_SECRET]")
        self.assertEqual(sanitized["google_refresh_token"], "[REDACTED_SECRET]")
        self.assertEqual(sanitized["user_prompt"], "Hello world")

        # Test string exception redaction
        err_msg = "OAuth failure with bearer_gmail_88888888 key"
        sanitized_err = redact_credentials(err_msg)
        self.assertIn("[REDACTED_BEARER_TOKEN]", sanitized_err)

    def test_deterministic_rules_routing(self):
        """Test deterministic routing bypassing LLM for trivial queries (0 tokens)."""
        decision = self.router.route_request(intent=INTENT_GET_TIME)
        self.assertIsInstance(decision, ModelDecision)
        self.assertEqual(decision.selected_tier, "rules")
        self.assertEqual(decision.estimated_tokens, 0)
        self.assertEqual(decision.estimated_cost, 0.0)

    def test_complexity_scorer_calculation(self):
        """Test multi-factor complexity scoring."""
        c_simple = self.scorer.calculate_complexity(intent="SIMPLE_QUERY", context_bytes=100)
        c_complex = self.scorer.calculate_complexity(intent="PLAN_DAY", context_bytes=4000, risk_level="HIGH")

        self.assertLess(c_simple, 0.40)
        self.assertGreaterEqual(c_complex, 0.70)

    def test_confidence_triggered_escalation(self):
        """Test low model confidence triggers escalation to remote-large tier."""
        decision = self.router.route_request(intent="REVIEW_INBOX", confidence=0.55)
        self.assertEqual(decision.selected_tier, "remote-large")
        self.assertTrue(decision.escalated)
        self.assertIn("Confidence escalation", decision.reason)

    def test_security_invariant_model_confidence_never_bypasses_policy(self):
        """Hard Invariant Test: 99.9% model confidence MUST NEVER bypass PolicyEngine authorization."""
        prop = self.policy.create_proposal("trash_email", "m99", {"msg_id": "m99"}, confidence=0.999)
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
