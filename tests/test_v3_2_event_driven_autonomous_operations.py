import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.events.event import (
    AgentEvent, EVENT_EMAIL_RECEIVED, EVENT_DEADLINE_APPROACHING,
    EVENT_CALENDAR_UPDATED, EVENT_GOAL_CHANGED
)
from personal_agent.events.bus import EventBus
from personal_agent.events.store import EventStore
from personal_agent.events.deduplicator import EventDeduplicator
from personal_agent.events.goal_correlator import EventGoalCorrelator
from personal_agent.events.trigger import TriggerEngine, TRIGGER_DEADLINE_WARNING
from personal_agent.events.processor import EventProcessor
from personal_agent.autonomy.proactive_engine import ProactiveActionEngine
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.runtime.lifecycle import AgentLifecycleState
from personal_agent.goals.goal import Goal, GOAL_ACTIVE

class TestV32EventDrivenAutonomousOperations(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_2_")
        self.event_store = EventStore(storage_dir=self.test_dir)
        self.event_bus = EventBus(event_store=self.event_store)
        self.deduplicator = EventDeduplicator()
        self.goal_correlator = EventGoalCorrelator()
        self.trigger_engine = TriggerEngine()
        self.processor = EventProcessor(
            deduplicator=self.deduplicator,
            goal_correlator=self.goal_correlator,
            trigger_engine=self.trigger_engine
        )
        self.supervisor = RuntimeSupervisor(storage_dir=self.test_dir)
        self.proactive_engine = ProactiveActionEngine(
            supervisor=self.supervisor,
            deduplicator=self.deduplicator
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_new_email_generates_event(self):
        """Test 1: New email publishes structured event to EventBus & EventStore."""
        published = []
        self.event_bus.subscribe(EVENT_EMAIL_RECEIVED, lambda e: published.append(e))

        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_101",
            payload={"sender": "prof@univ.edu", "subject": "Thesis draft feedback"}
        )
        self.event_bus.publish(evt)

        self.assertEqual(len(published), 1)
        self.assertEqual(published[0].entity_id, "msg_101")
        self.assertEqual(len(self.event_store.get_all_events()), 1)

    def test_2_duplicate_event_suppressed(self):
        """Test 2: Duplicate event is suppressed by EventDeduplicator."""
        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_102",
            payload={"subject": "Weekly newsletter"}
        )

        res1 = self.processor.process_event(evt)
        self.assertFalse(res1.is_duplicate)

        res2 = self.processor.process_event(evt)
        self.assertTrue(res2.is_duplicate)
        self.assertEqual(res2.recommended_outcome, "IGNORE")

    def test_3_irrelevant_event_ignored(self):
        """Test 3: Irrelevant / low priority event produces IGNORE outcome."""
        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_103",
            payload={"subject": "Marketing offer", "requires_action": False, "requires_planning": False}
        )

        res = self.processor.process_event(evt)
        self.assertEqual(res.recommended_outcome, "IGNORE")

        outcome_res = self.proactive_engine.handle_event_result(res)
        self.assertEqual(outcome_res["status"], "IGNORED")

    def test_4_important_event_linked_to_goal(self):
        """Test 4: Important email from professor correlates to active Goal and boosts priority."""
        goal_thesis = Goal("g_thesis", "Complete thesis proposal", priority="NORMAL", constraints=["thesis"])
        
        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_104",
            payload={"sender": "advisor@univ.edu", "subject": "Urgent feedback on thesis proposal draft"}
        )

        res = self.processor.process_event(evt, active_goals=[goal_thesis])
        self.assertTrue(len(res.correlated_goals) > 0)
        self.assertEqual(res.correlated_goals[0][0].goal_id, "g_thesis")
        self.assertIn(goal_thesis.priority, ("HIGH", "URGENT"))

    def test_5_deadline_event_generated(self):
        """Test 5: Deadline approaching event generates TRIGGER_DEADLINE_WARNING."""
        evt = AgentEvent(
            event_type=EVENT_DEADLINE_APPROACHING,
            source="task_scheduler",
            entity_id="task_thesis_submission",
            payload={"subject": "Thesis submission deadline in 24h"}
        )

        triggers = self.trigger_engine.evaluate_triggers([evt], [], [])
        self.assertTrue(any(t["trigger_id"] == TRIGGER_DEADLINE_WARNING for t in triggers))

    def test_6_event_creates_task_proposal(self):
        """Test 6: Urgent email event produces PROPOSE_ACTION / CREATE_TASK recommendation."""
        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_106",
            payload={"sender": "prof@univ.edu", "subject": "Please submit course assignment", "requires_action": True, "requires_planning": True}
        )

        res = self.processor.process_event(evt)
        self.assertIn(res.recommended_outcome, ("PROPOSE_ACTION", "CREATE_TASK"))
        
        outcome_res = self.proactive_engine.handle_event_result(res)
        self.assertEqual(outcome_res["status"], "PROPOSED")

    def test_7_autonomous_action_passes_governor(self):
        """Test 7: Low risk event with allow_auto executes autonomous action under LEVEL_3_BOUNDED_AUTO."""
        self.supervisor.start()
        
        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_107",
            payload={"subject": "Urgent deadline", "requires_action": True, "requires_planning": True, "allow_auto": True}
        )

        res = self.processor.process_event(evt)
        res.action_type = "get_current_time"  # Low risk tool
        self.assertEqual(res.recommended_outcome, "AUTONOMOUS_ACTION")

        outcome_res = self.proactive_engine.handle_event_result(res, goal_id="goal_100")
        self.assertEqual(outcome_res["status"], "SUCCESS")

    def test_8_unauthorized_action_blocked(self):
        """Test 8: High risk autonomous action or non-RUNNING supervisor state is blocked."""
        self.supervisor.start()
        self.supervisor.current_state = AgentLifecycleState.PAUSED  # Pause supervisor

        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_108",
            payload={"subject": "Urgent deadline", "requires_action": True, "requires_planning": True, "allow_auto": True}
        )

        res = self.processor.process_event(evt)
        res.action_type = "get_current_time"
        
        outcome_res = self.proactive_engine.handle_event_result(res, goal_id="goal_100")
        self.assertEqual(outcome_res["status"], "BLOCKED")
        self.assertIn("must be RUNNING", outcome_res["reason"])

    def test_9_event_survives_restart(self):
        """Test 9: Unprocessed events in EventStore survive process restart."""
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_109", payload={"text": "hello"})
        self.event_store.append_event(evt)

        # Re-instantiate EventStore from disk
        restarted_store = EventStore(storage_dir=self.test_dir)
        all_events = restarted_store.get_all_events()
        self.assertEqual(len(all_events), 1)
        self.assertEqual(all_events[0].entity_id, "msg_109")

    def test_10_event_processing_failure_recovered(self):
        """Test 10: Exception during handler is safely caught without crashing EventBus dispatch."""
        def faulty_handler(e):
            raise ValueError("Simulated subscriber crash!")

        self.event_bus.subscribe(EVENT_EMAIL_RECEIVED, faulty_handler)

        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_110")
        # Should catch exception and proceed without re-throwing
        self.event_bus.publish(evt)
        self.assertTrue(evt.processed)

    def test_11_idempotency_prevents_duplicate_execution(self):
        """Test 11: Receiving same autonomous event 10x results in exactly 1 action execution."""
        self.supervisor.start()

        evt = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="gmail",
            entity_id="msg_idem_111",
            payload={"subject": "Urgent task", "requires_action": True, "requires_planning": True, "allow_auto": True}
        )

        # First processing execution
        res1 = self.processor.process_event(evt)
        res1.action_type = "get_current_time"
        outcome1 = self.proactive_engine.handle_event_result(res1, goal_id="goal_100")
        self.assertEqual(outcome1["status"], "SUCCESS")

        # Subsequent 9 attempts with duplicate event or same idempotency key
        for _ in range(9):
            res_repeat = self.processor.process_event(evt)
            outcome_repeat = self.proactive_engine.handle_event_result(res_repeat, goal_id="goal_100")
            self.assertIn(outcome_repeat["status"], ("DUPLICATE_SUPPRESSED", "IDEMPOTENT_SKIPPED"))

    def test_12_event_storm_handling(self):
        """Test 12: Burst of 50 events processed rapidly without runtime crash or leak."""
        self.supervisor.start()

        for i in range(50):
            evt = AgentEvent(
                event_type=EVENT_EMAIL_RECEIVED,
                source="gmail",
                entity_id=f"msg_burst_{i}",
                payload={"subject": f"Burst email {i}", "requires_action": (i % 2 == 0)}
            )
            res = self.processor.process_event(evt)
            outcome = self.proactive_engine.handle_event_result(res)
            self.assertIn(outcome["status"], ("IGNORED", "NOTIFIED", "PROPOSED", "SUCCESS"))

if __name__ == "__main__":
    unittest.main()
