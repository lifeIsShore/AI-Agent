import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.triage.engine import PriorityEngine
from personal_agent.planner.daily_planner import DailyPlannerEngine
from personal_agent.context.manager import ContextManager
from personal_agent.tools.gmail import GmailTool
from personal_agent.triage.inbox_zero import InboxZeroEngine
from personal_agent.policy.engine import PolicyEngine as PolicyEngineSecurity, PermissionLevel

class TestV06GmailAndContextBudgets(unittest.TestCase):

    def setUp(self):
        self.gateway = MagicMock()
        self.triage_engine = PriorityEngine(self.gateway)
        self.planner = DailyPlannerEngine(user_name="Ahmet")
        self.context_manager = ContextManager(self.gateway)
        self.policy = PolicyEngineSecurity()
        self.inbox_zero = InboxZeroEngine()

    def test_requires_planning_flag_in_triage(self):
        """Test that PriorityEngine sets requires_planning = False for alerts/marketing and True for direct tasks."""
        # 1. Job Alert Digest -> requires_planning = False
        job_alert = {
            "sender": "careers@jobalerts.com",
            "subject": "Weekly job alert digest",
            "body": "10 new engineering jobs"
        }
        res, _ = self.triage_engine.evaluate(job_alert)
        self.assertFalse(res["requires_planning"])

        # 2. Marketing / Newsletter -> requires_planning = False
        newsletter = {
            "sender": "news@promotions.com",
            "subject": "50% discount on DSL plan",
            "body": "Save 50% today only!"
        }
        res, _ = self.triage_engine.evaluate(newsletter)
        self.assertFalse(res["requires_planning"])

        # 3. Direct University email -> requires_planning = True
        univ_email = {
            "sender": "advisor@univ.edu",
            "subject": "Thesis proposal review",
            "body": "Please submit your proposal by tomorrow."
        }
        res, _ = self.triage_engine.evaluate(univ_email)
        self.assertTrue(res["requires_planning"])
        self.assertTrue(res["requires_action"])

    def test_planner_filters_non_planning_emails(self):
        """Test that DailyPlannerEngine ignores emails with requires_planning == False."""
        emails = [
            {
                "priority": "important",
                "subject": "LinkedIn job alert digest",
                "category": "job_search",
                "requires_action": True,
                "requires_planning": False  # Should be IGNORED by planner schedule!
            },
            {
                "priority": "urgent",
                "subject": "Thesis proposal submission",
                "category": "thesis",
                "requires_action": True,
                "requires_planning": True  # Should be INCLUDED!
            }
        ]

        from personal_agent.context.package import ContextPackage
        context = ContextPackage(
            task="plan_day",
            user_request="Plan my day",
            emails=emails
        )

        plan = self.planner.generate_daily_plan(context)
        
        # Verify job alert is NOT scheduled
        scheduled_titles = [item["title"] for item in plan["schedule"]]
        self.assertNotIn("Reply: LinkedIn job alert digest", scheduled_titles)
        self.assertNotIn("Task: LinkedIn job alert digest", scheduled_titles)
        
        # Verify thesis email IS scheduled
        thesis_scheduled = any("Thesis proposal submission" in t for t in scheduled_titles)
        self.assertTrue(thesis_scheduled)

    def test_intent_dependent_context_budgets(self):
        """Test dynamic budget allocation in ContextManager per task type."""
        # 1. REVIEW_INBOX
        b_inbox = self.context_manager.get_intent_budgets("review_inbox")
        self.assertEqual(b_inbox["max_emails"], 15)
        self.assertEqual(b_inbox["max_rag_chunks"], 0)
        self.assertFalse(b_inbox["include_calendar"])

        # 2. QUERY_KNOWLEDGE
        b_rag = self.context_manager.get_intent_budgets("query_knowledge")
        self.assertEqual(b_rag["max_emails"], 0)
        self.assertEqual(b_rag["max_rag_chunks"], 5)
        self.assertFalse(b_rag["include_calendar"])

        # 3. PLAN_DAY
        b_plan = self.context_manager.get_intent_budgets("plan_day")
        self.assertTrue(b_plan["include_calendar"])
        self.assertTrue(b_plan["include_tasks"])
        self.assertTrue(b_plan["only_planning_emails"])

    def test_gmail_productivity_tools_mock(self):
        """Test archive, trash, mark_read, apply_label, create_draft with mock service."""
        mock_service = MagicMock()
        mock_messages_api = MagicMock()
        mock_service.users.return_value.messages.return_value = mock_messages_api
        mock_drafts_api = MagicMock()
        mock_service.users.return_value.drafts.return_value = mock_drafts_api

        mock_messages_api.modify.return_value.execute.return_value = {"id": "m1"}
        mock_messages_api.trash.return_value.execute.return_value = {"id": "m1"}
        mock_drafts_api.create.return_value.execute.return_value = {"id": "d1"}

        gmail = GmailTool(service=mock_service)

        # Archive
        res_arch = gmail.archive_email("m1")
        self.assertEqual(res_arch["status"], "success")

        # Trash
        res_trash = gmail.trash_email("m1")
        self.assertEqual(res_trash["status"], "success")

        # Mark Read
        res_read = gmail.mark_read("m1")
        self.assertEqual(res_read["status"], "success")

        # Create Draft
        res_draft = gmail.create_draft(to="prof@univ.edu", subject="Re: Thesis", body="Hello")
        self.assertEqual(res_draft["status"], "success")
        self.assertEqual(res_draft["draft_id"], "d1")

    def test_inbox_zero_engine(self):
        """Test InboxZeroEngine proposal generation for marketing emails and urgent replies."""
        emails = [
            {"id": "m1", "subject": "50% off sale", "category": "marketing", "email_type": "marketing", "priority": "normal"},
            {"id": "m2", "subject": "University grade issue", "category": "university", "priority": "urgent", "requires_response": True, "sender": "prof@univ.edu"}
        ]

        eval_res = self.inbox_zero.evaluate_inbox(emails)
        
        self.assertEqual(len(eval_res["archive_proposals"]), 1)
        self.assertEqual(eval_res["archive_proposals"][0]["msg_id"], "m1")
        
        self.assertEqual(len(eval_res["draft_proposals"]), 1)
        self.assertEqual(eval_res["draft_proposals"][0]["to"], "prof@univ.edu")

    def test_policy_engine_security_for_v0_6_gmail(self):
        """Test that all V0.6 Gmail modification tools require MODIFY human approval."""
        mod_tools = ["archive_email", "trash_email", "apply_label", "mark_read", "create_draft"]
        for tool in mod_tools:
            level = self.policy.get_permission_level(tool)
            self.assertEqual(level, PermissionLevel.MODIFY)
            allowed, reason = self.policy.check_permission(tool, {})
            self.assertFalse(allowed)
            self.assertIn("Requires Human Authorization", reason)

if __name__ == "__main__":
    unittest.main()
