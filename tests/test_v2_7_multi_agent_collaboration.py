import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.multi_agent.supervisor import AgentSupervisor
from personal_agent.multi_agent.agents import InboxAgent, CalendarAgent, TaskAgent
from personal_agent.multi_agent.messaging import A2AMessageBus, AgentMessage
from personal_agent.multi_agent.conflict_resolver import ConflictResolver
from personal_agent.multi_agent.budget import AgentBudgetManager

class TestV27MultiAgentCollaboration(unittest.TestCase):

    def setUp(self):
        self.supervisor = AgentSupervisor()
        self.inbox_agent = InboxAgent()
        self.cal_agent = CalendarAgent()
        self.task_agent = TaskAgent()
        self.bus = A2AMessageBus()
        self.resolver = ConflictResolver()
        self.budget_mgr = AgentBudgetManager()

    def test_supervisor_goal_decomposition(self):
        """Test AgentSupervisor decomposes top-level goal into scoped AgentTask contracts."""
        tasks = self.supervisor.decompose_goal("Plan my day", "wf_multi_100")
        self.assertEqual(len(tasks), 3)

        assigned_agents = [t.assigned_agent for t in tasks]
        self.assertIn("InboxAgent", assigned_agents)
        self.assertIn("CalendarAgent", assigned_agents)
        self.assertIn("TaskAgent", assigned_agents)

    def test_specialist_agent_capability_isolation(self):
        """Test BaseSpecialistAgent capability isolation boundary rejects unauthorized capabilities."""
        ok_read, msg_read, _ = self.inbox_agent.execute_task_capability("gmail.read", {"limit": 10})
        self.assertTrue(ok_read)

        # Invariant check: InboxAgent is NOT authorized for calendar.delete
        ok_del, msg_del, _ = self.inbox_agent.execute_task_capability("calendar.delete", {"event_id": "ev1"})
        self.assertFalse(ok_del)
        self.assertIn("Capability Violation", msg_del)

    def test_a2a_message_bus_dlp_validation(self):
        """Test A2AMessageBus validates DLP and delivers inter-agent messages."""
        msg = AgentMessage(
            message_id="msg_a2a_1",
            sender_agent="InboxAgent",
            receiver_agent="CalendarAgent",
            task_id="t1",
            payload={"free_slot_request": True}
        )
        ok, res_msg = self.bus.send_message(msg)
        self.assertTrue(ok)
        self.assertIn("delivered successfully", res_msg)

    def test_conflict_resolver_priority(self):
        """Test ConflictResolver resolves conflicting specialist proposals based on priority & urgency."""
        p_cal = {"agent": "CalendarAgent", "priority": "HIGH", "urgency": 0.90, "summary": "Meeting at 14:00"}
        p_task = {"agent": "TaskAgent", "priority": "LOW", "urgency": 0.30, "summary": "Focus deep work at 14:00"}

        winner, reason = self.resolver.resolve_agent_conflict([p_cal, p_task])
        self.assertEqual(winner["agent"], "CalendarAgent")
        self.assertIn("Resolved conflict", reason)

    def test_agent_budget_manager_sub_allocation(self):
        """Test AgentBudgetManager enforces per-agent sub-budget limits."""
        ok1, msg1 = self.budget_mgr.consume_agent_tokens("InboxAgent", 1000)
        self.assertTrue(ok1)

        ok2, msg2 = self.budget_mgr.consume_agent_tokens("InboxAgent", 1500)
        self.assertFalse(ok2)
        self.assertIn("Agent Budget Exceeded", msg2)

if __name__ == "__main__":
    unittest.main()
