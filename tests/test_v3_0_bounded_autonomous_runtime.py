import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.autonomy.controller import AutonomyController
from personal_agent.autonomy.autonomy_policy import (
    AutonomyPolicyEngine, LEVEL_0_OBSERVE, LEVEL_1_RECOMMEND,
    LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO, LEVEL_4_SUPERVISED_AUTO
)
from personal_agent.autonomy.goal_selector import GoalSelector
from personal_agent.autonomy.governor import AutonomyGovernor
from personal_agent.goals.goal import Goal, GOAL_ACTIVE, GOAL_STALLED

class TestV30BoundedAutonomousRuntime(unittest.TestCase):

    def setUp(self):
        self.controller = AutonomyController()
        self.policy = AutonomyPolicyEngine()
        self.selector = GoalSelector()
        self.governor = AutonomyGovernor()

    def test_autonomy_controller_closed_loop(self):
        """Test AutonomyController runs closed control loop cycle."""
        rec = self.controller.run_autonomous_cycle("goal_100", proposed_action="create_calendar_event")
        self.assertEqual(rec.goal_id, "goal_100")
        self.assertEqual(rec.status, "SUCCESS")

    def test_autonomy_policy_levels_0_to_4(self):
        """Test AutonomyPolicyEngine enforces levels 0 to 4 based on risk level."""
        # Level 0: Observe only
        ok0, _ = self.policy.evaluate_autonomy_permission("LOW", LEVEL_0_OBSERVE)
        self.assertFalse(ok0)

        # Level 1: Recommend only
        ok1, _ = self.policy.evaluate_autonomy_permission("LOW", LEVEL_1_RECOMMEND)
        self.assertFalse(ok1)

        # Level 2: Approval required
        ok2, _ = self.policy.evaluate_autonomy_permission("LOW", LEVEL_2_APPROVAL)
        self.assertFalse(ok2)

        # Level 3: LOW risk auto, HIGH risk approval required
        ok3_low, _ = self.policy.evaluate_autonomy_permission("LOW", LEVEL_3_BOUNDED_AUTO)
        self.assertTrue(ok3_low)
        ok3_high, _ = self.policy.evaluate_autonomy_permission("HIGH", LEVEL_3_BOUNDED_AUTO)
        self.assertFalse(ok3_high)

        # Level 4: LOW/MEDIUM risk auto
        ok4_med, _ = self.policy.evaluate_autonomy_permission("MEDIUM", LEVEL_4_SUPERVISED_AUTO)
        self.assertTrue(ok4_med)

    def test_goal_selector_arbitration_and_starvation(self):
        """Test GoalSelector selects highest scoring goal and boosts stalled goals."""
        g_normal = Goal("g1", "Routine maintenance", priority="NORMAL", progress_pct=50.0)
        g_stalled = Goal("g2", "Stalled critical task", priority="NORMAL", status=GOAL_STALLED, progress_pct=10.0)

        winner, msg = self.selector.select_next_goal([g_normal, g_stalled])
        self.assertEqual(winner.goal_id, "g2")
        self.assertIn("Selected Goal", msg)

    def test_autonomy_governor_security_gate(self):
        """Test AutonomyGovernor acts as final deterministic security gate."""
        ok_low, msg_low = self.governor.authorize_action("get_current_time", "system", "LOW", LEVEL_3_BOUNDED_AUTO)
        self.assertTrue(ok_low)

        # Invariant check: High risk action under LEVEL_3 requires human approval
        ok_high, msg_high = self.governor.authorize_action("calendar.delete", "primary", "HIGH", LEVEL_3_BOUNDED_AUTO)
        self.assertFalse(ok_high)
        self.assertIn("Denied", msg_high)

    def test_security_invariant_agent_proposes_governor_authorizes(self):
        """Hard Security Invariant: Agent proposes actions, but AutonomyGovernor deterministically authorizes."""
        # Level 0 Observe mode MUST block execution regardless of model desire
        ok_blocked, msg_blocked = self.governor.authorize_action("create_calendar_event", "primary", "LOW", LEVEL_0_OBSERVE)
        self.assertFalse(ok_blocked)

if __name__ == "__main__":
    unittest.main()
