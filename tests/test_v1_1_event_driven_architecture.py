import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.events.event import (
    AgentEvent, EVENT_PROPOSAL_CREATED, EVENT_PROPOSAL_APPROVED, EVENT_ACTION_EXECUTED, EVENT_EMAIL_RECEIVED
)
from personal_agent.events.store import EventStore
from personal_agent.events.bus import EventBus
from personal_agent.policy.proposal import ActionProposal
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.tools.registry import ToolRegistry
from personal_agent.security.audit import AuditLogger
from personal_agent.state.manager import StateManager

class TestV11EventDrivenArchitecture(unittest.TestCase):

    def setUp(self):
        self.test_events_dir = "data/test_events"
        self.test_state_dir = "data/test_event_state"
        
        if os.path.exists(self.test_events_dir):
            shutil.rmtree(self.test_events_dir)
        if os.path.exists(self.test_state_dir):
            shutil.rmtree(self.test_state_dir)

        self.event_store = EventStore(events_dir=self.test_events_dir, log_filename="test_events.jsonl")
        self.event_bus = EventBus(event_store=self.event_store)
        self.state_manager = StateManager(state_dir=self.test_state_dir)
        self.policy = PolicyEngine()
        self.registry = ToolRegistry()
        self.audit_logger = AuditLogger(log_dir="data/logs", log_filename="test_v1_1_audit.jsonl")
        self.audit_logger.clear_logs()

    def tearDown(self):
        if os.path.exists(self.test_events_dir):
            shutil.rmtree(self.test_events_dir)
        if os.path.exists(self.test_state_dir):
            shutil.rmtree(self.test_state_dir)
        self.audit_logger.clear_logs()

    def test_event_bus_pub_sub_dispatch(self):
        """Test EventBus registering subscribers and dispatching matching events."""
        mock_handler = MagicMock()
        self.event_bus.subscribe(EVENT_EMAIL_RECEIVED, mock_handler)

        event = AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="GmailTool",
            entity_id="email_99",
            payload={"subject": "Important Meeting"}
        )

        self.event_bus.publish(event)
        mock_handler.assert_called_once()
        self.assertEqual(mock_handler.call_args[0][0].entity_id, "email_99")

    def test_event_store_crash_recovery_replay(self):
        """Test EventStore logging to disk and replaying unprocessed events on crash recovery."""
        evt1 = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="test", entity_id="m1", processed=True)
        evt2 = AgentEvent(event_type=EVENT_PROPOSAL_CREATED, source="test", entity_id="prop_22", processed=False)

        self.event_store.append_event(evt1)
        self.event_store.append_event(evt2)

        unprocessed = self.event_store.get_unprocessed_events()
        self.assertEqual(len(unprocessed), 1)
        self.assertEqual(unprocessed[0].entity_id, "prop_22")

        # Test replay
        mock_handler = MagicMock()
        self.event_bus.subscribe(EVENT_PROPOSAL_CREATED, mock_handler)
        self.event_bus.replay_unprocessed()

        mock_handler.assert_called_once()
        # Verify event now marked processed on disk
        self.assertEqual(len(self.event_store.get_unprocessed_events()), 0)

    def test_approval_queue_event_publishing(self):
        """Test ApprovalQueue publishing events to EventBus on proposal addition and approval."""
        queue = ApprovalQueue(
            tool_registry=self.registry,
            audit_logger=self.audit_logger,
            state_manager=self.state_manager,
            event_bus=self.event_bus
        )

        prop = self.policy.create_proposal("archive_email", "msg_777", {"msg_id": "msg_777"}, reason="Inbox Zero")
        self.policy.check_proposal(prop, user_approved=False)

        # 1. Add proposal
        queue.add_proposal(prop)
        all_events = self.event_store.load_all_events()
        self.assertTrue(any(e.event_type == EVENT_PROPOSAL_CREATED and e.entity_id == prop.proposal_id for e in all_events))

        # Register mock tool for approval execution
        self.registry.register("archive_email", schema={}, func=lambda msg_id: f"Archived {msg_id}")

        # 2. Approve proposal
        queue.approve_proposal(prop.proposal_id)
        all_events_after = self.event_store.load_all_events()
        
        self.assertTrue(any(e.event_type == EVENT_PROPOSAL_APPROVED and e.entity_id == prop.proposal_id for e in all_events_after))
        self.assertTrue(any(e.event_type == EVENT_ACTION_EXECUTED and e.entity_id == prop.proposal_id for e in all_events_after))

if __name__ == "__main__":
    unittest.main()
