import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.policy.policy_registry import DeclarativePolicyRegistry
from personal_agent.security.classification import DataClassifier, SENSITIVITY_HIGHLY_SENSITIVE, SENSITIVITY_PUBLIC, SENSITIVITY_PERSONAL
from personal_agent.security.dlp import DataLossPreventionEngine
from personal_agent.security.provenance import ProvenanceTracker
from personal_agent.policy.simulator import PolicySimulator

class TestV19PolicyAsCodeAndGovernance(unittest.TestCase):

    def setUp(self):
        self.registry = DeclarativePolicyRegistry(policy_dir="policies")
        self.classifier = DataClassifier()
        self.dlp = DataLossPreventionEngine(self.classifier)
        self.provenance = ProvenanceTracker()
        self.simulator = PolicySimulator()

    def test_declarative_policy_registry_loading(self):
        """Test DeclarativePolicyRegistry loads and parses YAML policies from disk."""
        rule_gmail_trash = self.registry.get_rule("gmail.trash")
        self.assertIsNotNone(rule_gmail_trash)
        self.assertEqual(rule_gmail_trash["risk_level"], "HIGH")
        self.assertTrue(rule_gmail_trash["approval_required"])

    def test_data_classification_tiers(self):
        """Test DataClassifier categorizes content into sensitivity tiers accurately."""
        sens_pass = self.classifier.classify_sensitivity("Your account password: secret_key_123")
        self.assertEqual(sens_pass, SENSITIVITY_HIGHLY_SENSITIVE)

        sens_news = self.classifier.classify_sensitivity("Weekly engineering newsletter", category="newsletter")
        self.assertEqual(sens_news, SENSITIVITY_PUBLIC)

    def test_data_loss_prevention_dlp_boundary(self):
        """Test DataLossPreventionEngine redacts HIGHLY_SENSITIVE data from prompt payload context."""
        items = [
            {"id": "1", "body": "Weekly newsletter digest", "category": "newsletter"},
            {"id": "2", "body": "Your bank PIN is 9988", "category": "finance"}
        ]

        sanitized, blocked = self.dlp.sanitize_context_payload(items)
        self.assertEqual(blocked, 1)
        self.assertEqual(sanitized[0]["body"], "Weekly newsletter digest")
        self.assertIn("[REDACTED_HIGHLY_SENSITIVE_DATA_DLP_BLOCKED]", sanitized[1]["body"])

    def test_data_provenance_tracking_lineage(self):
        """Test ProvenanceTracker records and formats verifiable data lineage explanations."""
        rec = self.provenance.tag_provenance(
            content_id="item_001",
            source="gmail",
            source_id="msg_987",
            trust_level="EXTERNAL",
            sensitivity="PERSONAL"
        )
        self.assertEqual(rec.source, "gmail")

        explanation = self.provenance.explain_lineage("item_001")
        self.assertIn("GMAIL", explanation)
        self.assertIn("msg_987", explanation)

    def test_policy_simulator_dry_run(self):
        """Test PolicySimulator runs dry-run simulation reports cleanly."""
        res = self.simulator.simulate(
            principal_id="agent_assistant",
            action="gmail.trash",
            target="bank_email",
            sensitivity="HIGHLY_SENSITIVE"
        )
        self.assertEqual(res["decision"], "DENY")
        self.assertEqual(res["security_invariant"], "PASS")

if __name__ == "__main__":
    unittest.main()
