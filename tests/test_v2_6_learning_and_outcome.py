import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.learning.outcome_engine import OutcomeLearningEngine, OUTCOME_SUCCESS, OUTCOME_USER_CORRECTED, OUTCOME_FAILED
from personal_agent.learning.strategy_store import ExecutionStrategyStore
from personal_agent.learning.feedback_loop import FeedbackLoop, FEEDBACK_CORRECT, FEEDBACK_APPROVE
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import STATUS_PENDING_APPROVAL

class TestV26LearningAndOutcome(unittest.TestCase):

    def setUp(self):
        self.outcome_engine = OutcomeLearningEngine()
        self.strategy_store = ExecutionStrategyStore()
        self.feedback_loop = FeedbackLoop(self.outcome_engine, self.strategy_store)
        self.policy = PolicyEngine()

    def test_outcome_learning_engine_tracking(self):
        """Test OutcomeLearningEngine tracks outcome records and computes success rate."""
        self.outcome_engine.record_outcome("target_1", "create_calendar_event", OUTCOME_SUCCESS)
        self.outcome_engine.record_outcome("target_2", "create_calendar_event", OUTCOME_SUCCESS)
        self.outcome_engine.record_outcome("target_3", "create_calendar_event", OUTCOME_FAILED)

        rate = self.outcome_engine.get_success_rate("create_calendar_event")
        self.assertEqual(rate, 66.7)

    def test_execution_strategy_store_updates(self):
        """Test ExecutionStrategyStore updates evidence count and preferred parameters."""
        self.strategy_store.update_strategy_outcome("plan_day", success=True, used_parameters={"start_time": "16:00"})
        strat = self.strategy_store.get_preferred_strategy("plan_day")

        self.assertIsNotNone(strat)
        self.assertEqual(strat.evidence_count, 2)
        self.assertEqual(strat.preferred_parameters["start_time"], "16:00")

    def test_feedback_loop_correction_adaptation(self):
        """Test FeedbackLoop processes user corrections and adapts future candidate parameters."""
        ok, msg = self.feedback_loop.process_feedback(
            proposal_id="prop_100",
            action="create_calendar_event",
            feedback_type=FEEDBACK_CORRECT,
            corrected_params={"start_time": "16:00"}
        )

        self.assertTrue(ok)
        self.assertIn("16:00", msg)
        strat = self.strategy_store.get_preferred_strategy("create_calendar_event")
        self.assertEqual(strat.preferred_parameters["start_time"], "16:00")

    def test_security_invariant_learning_recommends_not_security_authority(self):
        """Hard Security Invariant: Learned strategy recommendations MUST NEVER bypass PolicyEngine authorization."""
        self.strategy_store.update_strategy_outcome("archive_email", success=True)
        strat = self.strategy_store.get_preferred_strategy("archive_email")
        self.assertGreater(strat.success_rate_pct, 90.0)

        # Invariant check: Even with 90%+ success strategy, proposal requires explicit policy check
        prop = self.policy.create_proposal("archive_email", "email_999", {"msg_id": "999"})
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)

if __name__ == "__main__":
    unittest.main()
