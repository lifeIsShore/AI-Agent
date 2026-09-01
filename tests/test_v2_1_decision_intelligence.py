import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.reasoning.reasoner import DecisionReasoner
from personal_agent.reasoning.plan import DecisionPlan
from personal_agent.context.optimizer import ContextOptimizer
from personal_agent.memory.lifecycle import MemoryLifecycleManager, ManagedMemory
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import STATUS_PENDING_APPROVAL

class TestV21DecisionIntelligence(unittest.TestCase):

    def setUp(self):
        self.reasoner = DecisionReasoner()
        self.optimizer = ContextOptimizer()
        self.memory_mgr = MemoryLifecycleManager()
        self.policy = PolicyEngine()

    def test_decision_reasoner_structured_plan(self):
        """Test DecisionReasoner constructs structured DecisionPlan objects."""
        items = [{"id": "1", "subject": "Thesis proposal deadline", "category": "university"}]
        plan = self.reasoner.build_decision_plan("Plan my day", items)

        self.assertIsInstance(plan, DecisionPlan)
        self.assertEqual(plan.objective, "Plan my day")
        self.assertGreaterEqual(len(plan.subtasks), 4)
        self.assertEqual(plan.candidate_actions[0]["action"], "create_calendar_event")

    def test_context_optimizer_scoring_and_budgeting(self):
        """Test ContextOptimizer ranks items by relevance score and trims within token budget."""
        items = [
            {"id": "1", "subject": "Weekly job alerts"},
            {"id": "2", "subject": "Thesis submission deadline"},
            {"id": "3", "subject": "Random spam"}
        ]
        # Restrict budget so only top relevance items fit
        res = self.optimizer.optimize_context_selection(items, max_token_budget=40)

        self.assertIsNotNone(res)
        self.assertEqual(res["selected_items"][0]["subject"], "Thesis submission deadline")
        self.assertGreaterEqual(res["avg_relevance_score"], 0.70)

    def test_memory_contradiction_detection(self):
        """Test ContradictionDetector detects opposing user behavior and demotes confidence."""
        mem = self.memory_mgr.add_memory("m1", "User prefers afternoon processing", "preference", confidence=0.85)
        success, msg = self.memory_mgr.update_with_feedback("m1", "User approved morning processing")

        self.assertTrue(success)
        self.assertIn("Contradiction", msg)
        self.assertLess(self.memory_mgr.memories["m1"].confidence, 0.85)

    def test_memory_lifecycle_manager_promotion(self):
        """Test positive user feedback promotes memory confidence and evidence count."""
        mem = self.memory_mgr.add_memory("m2", "User prefers afternoon processing", "preference", confidence=0.80)
        success, msg = self.memory_mgr.update_with_feedback("m2", "User approved afternoon processing")

        self.assertTrue(success)
        self.assertEqual(self.memory_mgr.memories["m2"].evidence_count, 2)
        self.assertGreater(self.memory_mgr.memories["m2"].confidence, 0.80)

    def test_security_invariant_memory_recommends_not_security_authority(self):
        """Hard Security Invariant: Memory recommendations MUST NEVER bypass PolicyEngine authorization."""
        prop = self.policy.create_proposal("archive_email", "msg_777", {"msg_id": "msg_777"}, confidence=0.99)
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
