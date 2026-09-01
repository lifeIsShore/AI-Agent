import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.policy.review import ReviewDecisionEngine, MODE_AUTOMATIC, MODE_QUICK_REVIEW, MODE_DETAILED_REVIEW, MODE_CRITICAL_DENIAL
from personal_agent.policy.scopes import ScopeManager, SCOPE_RECURRING
from personal_agent.policy.rejection import RepeatedRejectionTracker
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import ActionProposal, STATUS_PENDING_APPROVAL

class TestV18AdaptiveHITL(unittest.TestCase):

    def setUp(self):
        self.policy = PolicyEngine()
        self.review_engine = ReviewDecisionEngine()
        self.scope_manager = ScopeManager()
        self.rejection_tracker = RepeatedRejectionTracker(threshold=3)

    def test_review_decision_engine_modes(self):
        """Test ReviewDecisionEngine categorizes review modes accurately."""
        # Low risk -> AUTOMATIC
        prop_low = self.policy.create_proposal("get_today_events", "primary", {})
        dec_low = self.review_engine.evaluate_review_mode(prop_low)
        self.assertEqual(dec_low.mode, MODE_AUTOMATIC)

        # Medium risk -> QUICK_REVIEW
        prop_med = self.policy.create_proposal("create_calendar_event", "primary", {})
        dec_med = self.review_engine.evaluate_review_mode(prop_med)
        self.assertEqual(dec_med.mode, MODE_QUICK_REVIEW)

        # High risk / external -> DETAILED_REVIEW
        prop_high = self.policy.create_proposal("send_email", "user@test.com", {})
        dec_high = self.review_engine.evaluate_review_mode(prop_high)
        self.assertEqual(dec_high.mode, MODE_DETAILED_REVIEW)

    def test_delegated_scope_manager_recurring(self):
        """Test bounded recurring delegated scopes with daily rate limits."""
        scope = self.scope_manager.add_delegation(
            capability="gmail.archive",
            filter_pattern="newsletter",
            daily_limit=2
        )

        auth1, msg1 = self.scope_manager.check_delegated_authorization("gmail.archive", "newsletter_100")
        self.assertTrue(auth1)

        auth2, msg2 = self.scope_manager.check_delegated_authorization("gmail.archive", "newsletter_101")
        self.assertTrue(auth2)

        # 3rd attempt exceeds daily rate limit of 2
        auth3, msg3 = self.scope_manager.check_delegated_authorization("gmail.archive", "newsletter_102")
        self.assertFalse(auth3)
        self.assertIn("rate limit", msg3)

    def test_format_explainable_card(self):
        """Test rich pre-execution proposal presentation card formatting."""
        prop = self.policy.create_proposal(
            action="create_calendar_event",
            target="primary_calendar",
            parameters={"summary": "Study German"},
            reason="Free calendar slot detected"
        )

        card_str = prop.format_explainable_card()
        self.assertIn("ACTION PROPOSAL", card_str)
        self.assertIn("create_calendar_event", card_str)
        self.assertIn("primary_calendar", card_str)

    def test_repeated_rejection_tracker(self):
        """Test repeated rejections >= 3 trigger proposal throttling."""
        action = "trash_email"
        category = "promotional"

        self.rejection_tracker.record_rejection(action, category)
        self.rejection_tracker.record_rejection(action, category)
        t1, _ = self.rejection_tracker.should_throttle_proposal(action, category)
        self.assertFalse(t1)

        # 3rd rejection triggers throttle
        self.rejection_tracker.record_rejection(action, category)
        t2, msg = self.rejection_tracker.should_throttle_proposal(action, category)
        self.assertTrue(t2)
        self.assertIn("Throttled", msg)

    def test_security_invariant_memory_recommends_not_security_authority(self):
        """Hard Security Invariant: Memory evidence recommendations MUST NEVER bypass PolicyEngine authorization."""
        prop = self.policy.create_proposal("archive_email", "msg_999", {"msg_id": "msg_999"}, confidence=0.99)
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)

        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)
        self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
