import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.multi_agent.agent_registry import AgentRegistry, AgentSpecialistProfile
from personal_agent.multi_agent.agent_router import AgentRouter
from personal_agent.multi_agent.specialist_runtime import SpecialistRuntime
from personal_agent.multi_agent.agent_communication import (
    AgentMessageBus, AgentMessage, MSG_TYPE_TASK_DELEGATION, MSG_TYPE_RESULT_REPORT
)
from personal_agent.autonomy.autonomy_policy import LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO

class TestV37MultiAgentSpecialists(unittest.TestCase):

    def setUp(self):
        self.registry = AgentRegistry()
        self.router = AgentRouter(registry=self.registry)
        self.runtime = SpecialistRuntime()
        self.message_bus = AgentMessageBus()

    def test_1_specialist_profiles_registered(self):
        """Test 1: AgentRegistry initializes default specialist profiles."""
        agents = self.registry.get_all_agents()
        self.assertEqual(len(agents), 6)

    def test_2_email_specialist_capabilities(self):
        """Test 2: EmailSpecialist profile has Gmail read/label/draft capabilities."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        self.assertIsNotNone(email_agent)
        self.assertIn("gmail.read", email_agent.capabilities)

    def test_3_research_specialist_capabilities(self):
        """Test 3: ResearchSpecialist profile has RAG search capabilities."""
        research_agent = self.registry.get_agent("ResearchSpecialist")
        self.assertIn("rag.query", research_agent.capabilities)

    def test_4_browser_specialist_autonomy_level(self):
        """Test 4: BrowserSpecialist maximum autonomy level is capped at LEVEL_2_APPROVAL."""
        browser_agent = self.registry.get_agent("BrowserSpecialist")
        self.assertEqual(browser_agent.maximum_autonomy_level, LEVEL_2_APPROVAL)

    def test_5_router_assigns_email_task(self):
        """Test 5: AgentRouter routes email task to EmailSpecialist."""
        team = self.router.route_task("Check unread emails from professor")
        self.assertTrue(any(a.agent_id == "EmailSpecialist" for a in team))

    def test_6_router_assigns_research_task(self):
        """Test 6: AgentRouter routes research task to ResearchSpecialist."""
        team = self.router.route_task("Research literature for thesis proposal")
        self.assertTrue(any(a.agent_id == "ResearchSpecialist" for a in team))

    def test_7_router_assigns_browser_task(self):
        """Test 7: AgentRouter routes web task to BrowserSpecialist."""
        team = self.router.route_task("Browse university portal URL")
        self.assertTrue(any(a.agent_id == "BrowserSpecialist" for a in team))

    def test_8_router_forms_collaborating_team(self):
        """Test 8: Multi-domain goal objective returns multiple specialists."""
        team = self.router.route_task("Research literature and check email")
        self.assertGreaterEqual(len(team), 2)

    def test_9_router_doesnt_grant_permissions(self):
        """Test 9: Router output is a list of profiles, not permission grants."""
        team = self.router.route_task("Task 1")
        self.assertIsInstance(team, list)

    def test_10_specialist_runtime_whitelists_tools(self):
        """Test 10: SpecialistRuntime.can_execute_tool allows whitelisted tool."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        ok, msg = self.runtime.can_execute_tool(email_agent, "list_messages")
        self.assertTrue(ok)

    def test_11_unwhitelisted_tool_blocked(self):
        """Test 11: SpecialistRuntime.can_execute_tool blocks unwhitelisted tool call."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        ok, msg = self.runtime.can_execute_tool(email_agent, "browser_navigate")
        self.assertFalse(ok)
        self.assertIn("BLOCKED", msg)

    def test_12_research_agent_cannot_send_email(self):
        """Test 12: ResearchSpecialist blocked from sending emails."""
        research_agent = self.registry.get_agent("ResearchSpecialist")
        ok, msg = self.runtime.can_execute_tool(research_agent, "send_email")
        self.assertFalse(ok)

    def test_13_email_agent_cannot_browse_web(self):
        """Test 13: EmailSpecialist blocked from browser navigation."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        ok, msg = self.runtime.can_execute_tool(email_agent, "browser_navigate")
        self.assertFalse(ok)

    def test_14_calendar_agent_allowed_tools(self):
        """Test 14: CalendarSpecialist allowed create_calendar_event."""
        cal_agent = self.registry.get_agent("CalendarSpecialist")
        ok, msg = self.runtime.can_execute_tool(cal_agent, "create_calendar_event")
        self.assertTrue(ok)

    def test_15_specialist_execution_success(self):
        """Test 15: execute_specialist_task returns SUCCESS for whitelisted tool."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        res = self.runtime.execute_specialist_task(email_agent, "list_messages", {"max": 5})
        self.assertEqual(res["status"], "SUCCESS")

    def test_16_specialist_execution_blocked(self):
        """Test 16: execute_specialist_task returns BLOCKED for unwhitelisted tool."""
        email_agent = self.registry.get_agent("EmailSpecialist")
        res = self.runtime.execute_specialist_task(email_agent, "execute_shell_cmd", {})
        self.assertEqual(res["status"], "BLOCKED")

    def test_17_message_bus_sends_delegation(self):
        """Test 17: AgentMessageBus records TASK_DELEGATION message."""
        msg = self.message_bus.send_message("Planner", "ResearchSpecialist", "t1", MSG_TYPE_TASK_DELEGATION, {"query": "thesis"})
        self.assertEqual(msg.message_type, MSG_TYPE_TASK_DELEGATION)

    def test_18_message_bus_sends_report(self):
        """Test 18: AgentMessageBus records RESULT_REPORT message."""
        msg = self.message_bus.send_message("ResearchSpecialist", "Planner", "t1", MSG_TYPE_RESULT_REPORT, {"found": 3})
        self.assertEqual(msg.message_type, MSG_TYPE_RESULT_REPORT)

    def test_19_agent_filters_messages(self):
        """Test 19: get_messages_for_agent filters messages for target agent."""
        self.message_bus.send_message("A1", "EmailSpecialist", "t1", MSG_TYPE_TASK_DELEGATION)
        self.message_bus.send_message("A1", "ResearchSpecialist", "t2", MSG_TYPE_TASK_DELEGATION)
        msgs = self.message_bus.get_messages_for_agent("EmailSpecialist")
        self.assertEqual(len(msgs), 1)

    def test_20_task_messages_indexed(self):
        """Test 20: get_task_messages returns all messages for a specific task ID."""
        self.message_bus.send_message("A1", "A2", "t_100", MSG_TYPE_TASK_DELEGATION)
        self.message_bus.send_message("A2", "A1", "t_100", MSG_TYPE_RESULT_REPORT)
        msgs = self.message_bus.get_task_messages("t_100")
        self.assertEqual(len(msgs), 2)

    def test_21_message_contains_evidence(self):
        """Test 21: AgentMessage contains evidence log payload."""
        msg = self.message_bus.send_message("A1", "A2", "t1", MSG_TYPE_RESULT_REPORT, evidence=["Paper 1 found"])
        self.assertEqual(len(msg.evidence), 1)

    def test_22_custom_specialist_registration(self):
        """Test 22: AgentRegistry.register_agent registers custom specialist profile."""
        custom = AgentSpecialistProfile("CustomAgent", "Role", "Desc", allowed_tools=["custom_tool"])
        self.registry.register_agent(custom)
        self.assertIsNotNone(self.registry.get_agent("CustomAgent"))

    def test_23_unknown_capability_query(self):
        """Test 23: get_agents_by_capability returns empty list for unknown capability."""
        agents = self.registry.get_agents_by_capability("unknown.capability")
        self.assertEqual(len(agents), 0)

    def test_24_all_agents_retrievable(self):
        """Test 24: get_all_agents returns 6 default profiles."""
        agents = self.registry.get_all_agents()
        self.assertEqual(len(agents), 6)

    def test_25_specialist_context_requirements(self):
        """Test 25: Profile records context requirement tags."""
        p = self.registry.get_agent("EmailSpecialist")
        self.assertIsInstance(p.context_requirements, list)

    def test_26_autonomy_level_cap_respected(self):
        """Test 26: BrowserSpecialist retains LEVEL_2_APPROVAL autonomy level cap."""
        p = self.registry.get_agent("BrowserSpecialist")
        self.assertEqual(p.maximum_autonomy_level, LEVEL_2_APPROVAL)

    def test_27_fallback_router_assignment(self):
        """Test 27: Unknown task description falls back to PlanningSpecialist."""
        team = self.router.route_task("xyz random task without keywords")
        self.assertTrue(any(a.agent_id == "PlanningSpecialist" for a in team))

    def test_28_message_payload_json_serializable(self):
        """Test 28: AgentMessage.to_dict() produces valid dict representation."""
        msg = self.message_bus.send_message("A1", "A2", "t1", MSG_TYPE_TASK_DELEGATION, {"k": "v"})
        d = msg.to_dict()
        self.assertEqual(d["task_id"], "t1")

    def test_29_message_deserialization(self):
        """Test 29: AgentMessage.from_dict() restores message instance."""
        data = {"message_id": "m100", "sender_agent_id": "A1", "recipient_agent_id": "A2", "task_id": "t1", "message_type": "QUERY"}
        msg = AgentMessage.from_dict(data)
        self.assertEqual(msg.message_id, "m100")

    def test_30_multi_agent_collaboration_auditable(self):
        """Test 30: Message bus provides full audit trail across specialists."""
        self.message_bus.send_message("Planner", "ResearchSpecialist", "t1", MSG_TYPE_TASK_DELEGATION)
        self.message_bus.send_message("ResearchSpecialist", "Planner", "t1", MSG_TYPE_RESULT_REPORT)
        self.assertEqual(len(self.message_bus.message_history), 2)

if __name__ == "__main__":
    unittest.main()
