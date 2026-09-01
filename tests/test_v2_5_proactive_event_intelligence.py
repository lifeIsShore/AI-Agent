import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.events.event import AgentEvent
from personal_agent.events.classifier import EventClassifier, ACTION_WORKFLOW, ACTION_IGNORE
from personal_agent.events.deduplicator import EventDeduplicator
from personal_agent.events.correlator import EventCorrelator, SITUATION_SCHEDULE_CONFLICT
from personal_agent.events.priority import EventPriorityEngine, P5_CRITICAL, P0_IGNORE
from personal_agent.events.notification import NotificationIntelligenceEngine, ROUTE_URGENT_INTERRUPT, ROUTE_QUEUE_BRIEFING
from personal_agent.events.trigger import ProactiveTriggerEngine
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import STATUS_PENDING_APPROVAL

class TestV25ProactiveEventIntelligence(unittest.TestCase):

    def setUp(self):
        self.classifier = EventClassifier()
        self.dedup = EventDeduplicator()
        self.correlator = EventCorrelator()
        self.priority = EventPriorityEngine()
        self.notification = NotificationIntelligenceEngine()
        self.trigger = ProactiveTriggerEngine()
        self.policy = PolicyEngine()

    def test_event_classifier_and_metrics(self):
        """Test EventClassifier computes importance, urgency, and recommended actions accurately."""
        cl = self.classifier.classify_event("EMAIL_RECEIVED", {"subject": "Urgent thesis submission deadline"})
        self.assertGreater(cl.importance, 0.85)
        self.assertGreater(cl.urgency, 0.80)
        self.assertEqual(cl.recommended_action, ACTION_WORKFLOW)

        cl_spam = self.classifier.classify_event("EMAIL_RECEIVED", {"subject": "Weekly job alerts digest"})
        self.assertEqual(cl_spam.recommended_action, ACTION_IGNORE)

    def test_event_deduplication_via_payload_hash(self):
        """Test EventDeduplicator suppresses duplicate events using payload identity hash."""
        e1 = AgentEvent(event_type="EMAIL_RECEIVED", source="gmail", entity_id="msg_999", payload={"subject": "Lecture room change"})
        
        is_dup1, msg1 = self.dedup.is_duplicate(e1)
        self.assertFalse(is_dup1)

        is_dup2, msg2 = self.dedup.is_duplicate(e1)
        self.assertTrue(is_dup2)
        self.assertIn("Duplicate", msg2)

    def test_event_correlator_composite_situations(self):
        """Test EventCorrelator detects composite situations across email and calendar events."""
        events = [AgentEvent(event_type="EMAIL_RECEIVED", source="gmail", entity_id="m1", payload={"subject": "Lecture room change"})]
        cal_events = [{"summary": "University lecture", "start": "10:00"}]

        situations = self.correlator.detect_composite_situations(events, cal_events, [])
        self.assertEqual(len(situations), 1)
        self.assertEqual(situations[0]["situation_id"], SITUATION_SCHEDULE_CONFLICT)

    def test_event_priority_engine_p0_to_p5(self):
        """Test EventPriorityEngine assigns P0-P5 priorities based on composite metrics."""
        prio_high = self.priority.calculate_priority(importance=0.95, urgency=0.90, actionability=0.85)
        self.assertEqual(prio_high, P5_CRITICAL)

        prio_low = self.priority.calculate_priority(importance=0.10, urgency=0.10, actionability=0.10)
        self.assertEqual(prio_low, P0_IGNORE)

    def test_notification_intelligence_routing(self):
        """Test NotificationIntelligenceEngine routes alerts based on priority and user state."""
        route_p5, reason5 = self.notification.determine_notification_routing("P5", is_user_busy=False)
        self.assertEqual(route_p5, ROUTE_URGENT_INTERRUPT)

        route_p4_busy, reason4 = self.notification.determine_notification_routing("P4", is_user_busy=True)
        self.assertEqual(route_p4_busy, ROUTE_QUEUE_BRIEFING)

    def test_proactive_trigger_engine_policy_boundary(self):
        """Test ProactiveTriggerEngine generates workflow candidates subject to policy checks."""
        wf = self.trigger.evaluate_proactive_trigger({"subject": "Thesis submission deadline"}, priority="P5")
        self.assertIsNotNone(wf)
        self.assertEqual(wf.priority, "HIGH")

        # Invariant check: Proactive proposal must still require policy authorization
        prop = self.policy.create_proposal("create_calendar_event", "primary_calendar", {"summary": "Proactive block"})
        allowed, reason = self.policy.check_proposal(prop, user_approved=False)
        self.assertFalse(allowed)
        self.assertEqual(prop.status, STATUS_PENDING_APPROVAL)

if __name__ == "__main__":
    unittest.main()
