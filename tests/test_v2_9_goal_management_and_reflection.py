import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.goals.manager import GoalManager
from personal_agent.goals.goal import GOAL_ACTIVE, GOAL_STALLED, GOAL_ACHIEVED
from personal_agent.goals.progress import GoalProgressEngine
from personal_agent.reflection.engine import SelfReflectionEngine
from personal_agent.reflection.evolution import StrategyEvolutionEngine
from personal_agent.learning.strategy_store import ExecutionStrategyStore
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import STATUS_PENDING_APPROVAL

class TestV29GoalManagementAndReflection(unittest.TestCase):

    def setUp(self):
        self.mgr = GoalManager()
        self.progress_engine = GoalProgressEngine()
        self.reflection_engine = SelfReflectionEngine()
        self.evolution_engine = StrategyEvolutionEngine()
        self.strategy_store = ExecutionStrategyStore()
        self.policy = PolicyEngine()

    def test_goal_manager_hierarchy_creation(self):
        """Test GoalManager registers Goal objects and Milestones."""
        g = self.mgr.create_goal("Prepare Master's Semester", priority="HIGH")
        m1 = self.mgr.add_milestone(g.goal_id, "Register courses")
        
        self.assertIsNotNone(g)
        self.assertEqual(len(g.milestones), 1)
        self.assertEqual(m1.objective, "Register courses")

    def test_goal_progress_and_milestones(self):
        """Test GoalProgressEngine updates goal progress percentage when milestones complete."""
        g = self.mgr.create_goal("Complete thesis draft", priority="HIGH")
        m1 = self.mgr.add_milestone(g.goal_id, "Write introduction")
        m2 = self.mgr.add_milestone(g.goal_id, "Write literature review")

        self.progress_engine.update_goal_progress(g, m1.milestone_id)
        self.assertEqual(g.progress_pct, 50.0)

        self.progress_engine.update_goal_progress(g, m2.milestone_id)
        self.assertEqual(g.progress_pct, 100.0)
        self.assertEqual(g.status, GOAL_ACHIEVED)

    def test_stalled_goal_detection_and_recovery(self):
        """Test GoalProgressEngine detects stalled goals and formulates recovery recommendations."""
        g = self.mgr.create_goal("Blocked course registration", priority="MEDIUM")
        g.milestones.append(self.mgr.add_milestone(g.goal_id, "Submit advisor signoff"))
        
        stalled_list = self.progress_engine.detect_stalled_goals([g])
        self.assertEqual(len(stalled_list), 1)
        self.assertEqual(g.status, GOAL_STALLED)
        self.assertIn("recommended_recovery_action", stalled_list[0])

    def test_self_reflection_engine_deviation_analysis(self):
        """Test SelfReflectionEngine compares expected vs actual workflow outcomes."""
        refl = self.reflection_engine.evaluate_workflow_reflection(
            workflow_id="wf_daily_1",
            expected_outcome="4 focus blocks scheduled",
            actual_outcome="3 focus blocks scheduled"
        )
        self.assertIn("diverged", refl.deviation_reason)
        self.assertIn("Adjust conflict resolution", refl.recommendation)

    def test_strategy_evolution_updates(self):
        """Test StrategyEvolutionEngine updates strategy confidence from reflection records."""
        refl = self.reflection_engine.evaluate_workflow_reflection("wf_1", "4 sessions", "4 sessions")
        evol_res = self.evolution_engine.evolve_strategy("daily_planner_strategy", refl, self.strategy_store)
        
        self.assertTrue(evol_res["evolution_applied"])
        strat = self.strategy_store.get_preferred_strategy("daily_planner_strategy")
        self.assertIsNotNone(strat)

    def test_security_reflection_cannot_bypass_policy(self):
        """Hard Security Invariant: Reflection recommendations MUST NEVER alter security policies or bypass authorization."""
        refl = self.reflection_engine.evaluate_workflow_reflection("wf_sec", "delete files", "delete files")
        self.evolution_engine.evolve_strategy("delete_strategy", refl, self.strategy_store)

        # Invariant check: Proposal still requires policy authorization
        prop = self.policy.create_proposal("gmail.archive", "email_1", {"msg_id": "1"})
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)
        
        self.assertFalse(allowed)
        self.assertIn(prop.status, [STATUS_PENDING_APPROVAL, "DENIED"])

if __name__ == "__main__":
    unittest.main()
