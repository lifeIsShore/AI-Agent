import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.policy.engine import PolicyEngine, PermissionLevel
from personal_agent.tools.calendar import GoogleCalendarTool
from personal_agent.tools.tasks import GoogleTasksTool
from personal_agent.planner.daily_planner import DailyPlannerEngine
from personal_agent.context.package import ContextPackage

class TestV05SecurityAndPlanner(unittest.TestCase):

    def setUp(self):
        self.policy = PolicyEngine()
        self.planner = DailyPlannerEngine(user_name="Ahmet")

    def test_security_levels_mapping(self):
        """Test explicit V0.5 security levels mapping."""
        # Read calendar -> READ_ONLY
        self.assertEqual(self.policy.get_permission_level("get_today_events"), PermissionLevel.READ_ONLY)
        self.assertEqual(self.policy.get_permission_level("get_week_events"), PermissionLevel.READ_ONLY)
        
        # Read tasks -> READ_ONLY
        self.assertEqual(self.policy.get_permission_level("list_tasks"), PermissionLevel.READ_ONLY)
        self.assertEqual(self.policy.get_permission_level("get_task"), PermissionLevel.READ_ONLY)
        
        # Calculate free time -> ANALYZE
        self.assertEqual(self.policy.get_permission_level("get_free_slots"), PermissionLevel.ANALYZE)
        
        # Suggest schedule -> PROPOSE
        self.assertEqual(self.policy.get_permission_level("generate_daily_plan"), PermissionLevel.PROPOSE)
        self.assertEqual(self.policy.get_permission_level("propose_schedule"), PermissionLevel.PROPOSE)
        
        # Create/Delete calendar event, complete task -> MODIFY
        self.assertEqual(self.policy.get_permission_level("create_calendar_event"), PermissionLevel.MODIFY)
        self.assertEqual(self.policy.get_permission_level("delete_calendar_event"), PermissionLevel.MODIFY)
        self.assertEqual(self.policy.get_permission_level("complete_task"), PermissionLevel.MODIFY)

    def test_policy_permission_check_workflow(self):
        """Test permission enforcement and human approval behavior."""
        # READ_ONLY, ANALYZE, PROPOSE should be allowed automatically
        allowed, reason = self.policy.check_permission("get_today_events", {})
        self.assertTrue(allowed)
        self.assertIn("READ_ONLY", reason)

        allowed, reason = self.policy.check_permission("get_free_slots", {})
        self.assertTrue(allowed)
        self.assertIn("ANALYZE", reason)

        allowed, reason = self.policy.check_permission("generate_daily_plan", {})
        self.assertTrue(allowed)
        self.assertIn("PROPOSE", reason)

        # MODIFY without approval should be blocked
        allowed, reason = self.policy.check_permission("create_calendar_event", {})
        self.assertFalse(allowed)
        self.assertIn("Requires Human Authorization", reason)

        # MODIFY with user approval should pass
        allowed, reason = self.policy.check_permission("create_calendar_event", {}, user_approved=True)
        self.assertTrue(allowed)
        self.assertIn("explicit human approval", reason)

    def test_free_slot_calculation(self):
        """Test calculation of free time slots from calendar events."""
        dummy_service = MagicMock()
        tool = GoogleCalendarTool(service=dummy_service)
        
        # Mock 2 events: 09:00-10:00 and 12:00-13:00
        tool.get_today_events = MagicMock(return_value=[
            {"start": "2026-09-01T09:00:00Z", "end": "2026-09-01T10:00:00Z", "summary": "Lecture"},
            {"start": "2026-09-01T12:00:00Z", "end": "2026-09-01T13:00:00Z", "summary": "Meeting"}
        ])

        free_slots = tool.get_free_slots(date_str="2026-09-01", working_hours=(9, 18))
        
        # Expect free slots: 10:00-12:00 (120 min) and 13:00-18:00 (300 min)
        self.assertEqual(len(free_slots), 2)
        self.assertEqual(free_slots[0]["start"], "10:00")
        self.assertEqual(free_slots[0]["end"], "12:00")
        self.assertEqual(free_slots[0]["duration_minutes"], 120)

        self.assertEqual(free_slots[1]["start"], "13:00")
        self.assertEqual(free_slots[1]["end"], "18:00")
        self.assertEqual(free_slots[1]["duration_minutes"], 300)

    def test_google_tasks_tool_mock(self):
        """Test Google Tasks tool list, create, and complete with mock service."""
        mock_service = MagicMock()
        mock_tasks_api = MagicMock()
        mock_service.tasks.return_value = mock_tasks_api

        # Mock list response
        mock_tasks_api.list.return_value.execute.return_value = {
            "items": [
                {"id": "t1", "title": "Thesis proposal", "status": "needsAction"},
                {"id": "t2", "title": "Review job alerts", "status": "needsAction"}
            ]
        }

        # Mock insert response
        mock_tasks_api.insert.return_value.execute.return_value = {
            "id": "t3", "title": "New task", "status": "needsAction"
        }

        # Mock update response for complete
        mock_tasks_api.get.return_value.execute.return_value = {
            "id": "t1", "title": "Thesis proposal", "status": "needsAction"
        }
        mock_tasks_api.update.return_value.execute.return_value = {
            "id": "t1", "title": "Thesis proposal", "status": "completed"
        }

        tasks_tool = GoogleTasksTool(service=mock_service)
        
        # 1. List
        tasks = tasks_tool.list_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["title"], "Thesis proposal")

        # 2. Create
        created = tasks_tool.create_task(title="New task")
        self.assertEqual(created["status"], "success")
        self.assertEqual(created["task"]["id"], "t3")

        # 3. Complete
        completed = tasks_tool.complete_task(task_id="t1")
        self.assertEqual(completed["status"], "success")
        self.assertEqual(completed["completed_task_id"], "t1")

    def test_daily_planner_memory_preference_influence(self):
        """Test that memory preferences (after 14:00 university emails) influence daily plan synthesis."""
        context = ContextPackage(
            task="plan_day",
            user_request="Plan my day",
            memory=[
                {"type": "preference", "content": "I prefer responding to university emails in the afternoon after 14:00."}
            ],
            calendar=[
                {"summary": "University lecture", "start": "2026-09-01T09:00:00Z", "end": "2026-09-01T10:00:00Z"}
            ],
            emails=[
                {"priority": "urgent", "subject": "Thesis proposal draft", "category": "thesis", "sender": "advisor@univ.edu", "requires_action": True, "requires_planning": True},
                {"priority": "important", "subject": "University course question", "category": "university", "sender": "prof@univ.edu", "requires_action": True, "requires_planning": True}
            ],
            tasks=[
                {"title": "Review job alerts", "status": "needsAction"}
            ]
        )

        plan = self.planner.generate_daily_plan(context)
        
        self.assertTrue(plan["memory_applied"])
        self.assertIn("Good morning Ahmet", plan["greeting"])
        
        # Check that proposals include university email scheduled in the afternoon (>= 14:00)
        univ_props = [p for p in plan["proposals"] if "university" in p["summary"].lower()]
        self.assertTrue(len(univ_props) > 0)
        
        univ_start_hour = int(univ_props[0]["start_time"].split(":")[0])
        self.assertGreaterEqual(univ_start_hour, 14)

if __name__ == "__main__":
    unittest.main()
