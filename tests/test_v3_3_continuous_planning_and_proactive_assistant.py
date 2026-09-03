import sys
import os
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.context.situation_model import SituationModel, CurrentSituation
from personal_agent.goals.goal import Goal, GOAL_ACTIVE, GOAL_STALLED
from personal_agent.goals.arbitration import GoalArbitrator
from personal_agent.planner.replanning_policy import ReplanningPolicy
from personal_agent.planner.resource_planner import ResourceAwarePlanner
from personal_agent.planner.continuous_planner import ContinuousPlanner
from personal_agent.autonomy.proactivity_budget import ProactivityBudget
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.runtime.lifecycle import AgentLifecycleState
from personal_agent.events.event import (
    AgentEvent, EVENT_EMAIL_RECEIVED, EVENT_TASK_COMPLETED,
    EVENT_CALENDAR_UPDATED, EVENT_DEADLINE_APPROACHING, EVENT_GOAL_CHANGED
)

class TestV33ContinuousPlanningAndProactiveAssistant(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_3_")
        self.situation_model = SituationModel()
        self.replanning_policy = ReplanningPolicy(min_replan_interval_sec=0.1)
        self.goal_arbitrator = GoalArbitrator()
        self.resource_planner = ResourceAwarePlanner()
        self.budget = ProactivityBudget(
            max_notifications_per_hour=3,
            max_replans_per_hour=5,
            max_autonomous_actions_per_hour=10,
            max_same_goal_interventions=2
        )
        self.supervisor = RuntimeSupervisor(storage_dir=self.test_dir)
        self.planner = ContinuousPlanner(
            situation_model=self.situation_model,
            replanning_policy=self.replanning_policy,
            goal_arbitrator=self.goal_arbitrator,
            resource_planner=self.resource_planner,
            budget=self.budget,
            supervisor=self.supervisor
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_situation_correctly_aggregates(self):
        """Test 1: SituationModel aggregates goals, tasks, events, and deadlines."""
        g1 = Goal("g1", "Complete thesis proposal", priority="HIGH", deadline="2026-10-01")
        t1 = {"task_id": "t1", "title": "Literature review", "deadline": "2026-09-15"}
        
        sit = self.situation_model.build_situation(
            goals=[g1],
            tasks=[t1],
            constraints=["No meetings after 17:00"]
        )
        self.assertEqual(len(sit.active_goals), 1)
        self.assertEqual(len(sit.tasks), 1)
        self.assertEqual(len(sit.deadlines), 2)
        self.assertIn("No meetings after 17:00", sit.constraints)

    def test_2_relevant_events_affect_situation(self):
        """Test 2: Relevant event updates recent event list in CurrentSituation."""
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_301", payload={"subject": "Thesis review"})
        sit = self.situation_model.build_situation(events=[evt])
        self.assertEqual(len(sit.recent_events), 1)
        self.assertEqual(sit.recent_events[0].entity_id, "msg_301")

    def test_3_irrelevant_events_dont_trigger_replan(self):
        """Test 3: Marketing / FYI email evaluates should_replan = False."""
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_302", payload={"subject": "Weekly Newsletter", "requires_action": False, "requires_planning": False})
        sit = self.situation_model.build_situation(events=[evt])
        
        should_replan, reason = self.replanning_policy.should_replan(evt, sit)
        self.assertFalse(should_replan)
        self.assertIn("Irrelevant", reason)

    def test_4_important_event_triggers_replan(self):
        """Test 4: Important email from professor triggers replanning."""
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_303", payload={"sender": "prof@univ.edu", "subject": "Urgent thesis review", "requires_action": True, "requires_planning": True})
        sit = self.situation_model.build_situation(events=[evt])

        should_replan, reason = self.replanning_policy.should_replan(evt, sit)
        self.assertTrue(should_replan)
        self.assertIn("Actionable email", reason)

    def test_5_calendar_conflict_triggers_replan(self):
        """Test 5: Calendar conflict triggers replanning."""
        evt = AgentEvent(event_type=EVENT_CALENDAR_UPDATED, source="calendar", entity_id="cal_101", payload={"summary": "Lecture room change conflict"})
        sit = self.situation_model.build_situation(events=[evt])

        should_replan, reason = self.replanning_policy.should_replan(evt, sit)
        self.assertTrue(should_replan)
        self.assertIn("Calendar event changed", reason)

    def test_6_deadline_triggers_replan(self):
        """Test 6: Approaching deadline event triggers replanning."""
        evt = AgentEvent(event_type=EVENT_DEADLINE_APPROACHING, source="scheduler", entity_id="task_thesis", payload={"subject": "Deadline in 24h"})
        sit = self.situation_model.build_situation(events=[evt])

        should_replan, reason = self.replanning_policy.should_replan(evt, sit)
        self.assertTrue(should_replan)
        self.assertIn("Approaching deadline", reason)

    def test_7_goal_priority_changes_correctly(self):
        """Test 7: Goal priority boost alters goal arbitration ordering."""
        g_normal = Goal("g_normal", "Routine task", priority="NORMAL")
        g_urgent = Goal("g_urgent", "Urgent exam prep", priority="URGENT")

        scored = self.goal_arbitrator.select_prioritized_goals([g_normal, g_urgent])
        self.assertEqual(scored[0][0].goal_id, "g_urgent")

    def test_8_planner_respects_calendar_constraints(self):
        """Test 8: Task scheduling fits around existing calendar blocks."""
        cal_events = [{"summary": "Lecture", "start_hour": 9, "end_hour": 11}]
        free_slots = self.resource_planner.get_free_time_slots(cal_events, start_hour=9, end_hour=13)
        
        # 9-11 is occupied, so free slots should start at 11:00
        self.assertEqual(free_slots[0], (11, 12))
        self.assertEqual(free_slots[1], (12, 13))

    def test_9_planner_respects_task_dependencies(self):
        """Test 9: Tasks are allocated into free time blocks sequentially."""
        tasks = [{"task_id": "t1", "title": "Draft proposal"}, {"task_id": "t2", "title": "Review proposal"}]
        cal_events = [{"summary": "Meeting", "start_hour": 9, "end_hour": 10}]
        
        allocations = self.resource_planner.allocate_task_schedules(tasks, cal_events, start_hour=9, end_hour=13)
        self.assertEqual(len(allocations), 2)
        self.assertEqual(allocations[0]["task_id"], "t1")
        self.assertEqual(allocations[0]["start_hour"], 10)
        self.assertEqual(allocations[1]["task_id"], "t2")
        self.assertEqual(allocations[1]["start_hour"], 11)

    def test_10_planner_doesnt_double_book(self):
        """Test 10: Tasks are assigned to distinct non-overlapping time slots."""
        tasks = [{"task_id": "t1"}, {"task_id": "t2"}]
        cal = [{"start_hour": 9, "end_hour": 10}]
        
        allocations = self.resource_planner.allocate_task_schedules(tasks, cal, start_hour=9, end_hour=12)
        hours = [a["start_hour"] for a in allocations]
        self.assertEqual(len(hours), len(set(hours)))  # All allocated hours are unique

    def test_11_planner_prevents_infinite_loops(self):
        """Test 11: Rapid consecutive events within min_replan_interval_sec are throttled."""
        policy = ReplanningPolicy(min_replan_interval_sec=10.0)
        evt = AgentEvent(event_type=EVENT_TASK_COMPLETED, source="task", entity_id="t1", payload={"subject": "done"})
        sit = self.situation_model.build_situation()

        s1, _ = policy.should_replan(evt, sit)
        self.assertTrue(s1)

        s2, msg2 = policy.should_replan(evt, sit)
        self.assertFalse(s2)
        self.assertIn("throttled", msg2)

    def test_12_proactivity_budget_notifications(self):
        """Test 12: ProactivityBudget limits max notification count per hour."""
        budget = ProactivityBudget(max_notifications_per_hour=2)
        budget.record_notification("g1")
        budget.record_notification("g2")

        ok, msg = budget.can_notify("g3")
        self.assertFalse(ok)
        self.assertIn("limit reached", msg)

    def test_13_proactivity_budget_replans(self):
        """Test 13: ProactivityBudget limits max replan count per hour."""
        budget = ProactivityBudget(max_replans_per_hour=2)
        budget.record_replan()
        budget.record_replan()

        ok, msg = budget.can_replan()
        self.assertFalse(ok)
        self.assertIn("limit reached", msg)

    def test_14_repeated_notification_suppressed(self):
        """Test 14: Suppresses nagging for goal when user has not acknowledged previous notifications."""
        budget = ProactivityBudget(max_notifications_per_hour=10)
        budget.record_notification("g_nag")
        budget.record_notification("g_nag")

        ok, msg = budget.can_notify("g_nag")
        self.assertFalse(ok)
        self.assertIn("Nagging suppressed", msg)

        # Clear nagging with user response
        budget.record_user_acknowledgement("g_nag")
        ok_after, _ = budget.can_notify("g_nag")
        self.assertTrue(ok_after)

    def test_15_autonomous_action_passes_governor(self):
        """Test 15: Low risk autonomous action passes governor when supervisor is RUNNING."""
        self.supervisor.start()
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_315", payload={"sender": "prof@univ.edu", "subject": "Urgent deadline", "requires_action": True, "requires_planning": True, "allow_auto": True})
        sit = self.situation_model.build_situation(goals=[Goal("g15", "Thesis", priority="HIGH")])

        res = self.planner.evaluate_and_replan(evt, sit)
        self.assertEqual(res["status"], "REPLANNED")
        self.assertEqual(res["proactive_output"]["status"], "SUCCESS")

    def test_16_paused_runtime_prevents_execution(self):
        """Test 16: Autonomous action execution is strictly blocked when supervisor is PAUSED."""
        self.supervisor.start()
        self.supervisor.current_state = AgentLifecycleState.PAUSED

        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_316", payload={"sender": "prof@univ.edu", "subject": "Urgent deadline", "requires_action": True, "requires_planning": True, "allow_auto": True})
        sit = self.situation_model.build_situation()

        res = self.planner.evaluate_and_replan(evt, sit)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("must be RUNNING", res["reason"])

    def test_17_recovering_runtime_prevents_planning(self):
        """Test 17: Continuous planning is strictly blocked when supervisor is RECOVERING."""
        self.supervisor.start()
        self.supervisor.current_state = AgentLifecycleState.RECOVERING

        evt = AgentEvent(event_type=EVENT_TASK_COMPLETED, source="task", entity_id="t17")
        sit = self.situation_model.build_situation()

        res = self.planner.evaluate_and_replan(evt, sit)
        self.assertEqual(res["status"], "BLOCKED")

    def test_18_restart_restores_pending_plan(self):
        """Test 18: Unprocessed starvation cycles persist across simulation cycles."""
        arb = GoalArbitrator()
        g_low = Goal("g_low", "Low priority cleanup", priority="LOW")
        g_high = Goal("g_high", "High priority assignment", priority="HIGH")

        arb.select_prioritized_goals([g_low, g_high])
        self.assertEqual(arb.unprocessed_cycles.get("g_low"), 1)

    def test_19_plan_verification_detects_failure(self):
        """Test 19: ProactivityBudget correctly blocks when budget limit is hit."""
        self.supervisor.start()
        for _ in range(5):
            self.planner.budget.record_replan()

        evt = AgentEvent(event_type=EVENT_TASK_COMPLETED, source="task", entity_id="t19")
        sit = self.situation_model.build_situation()

        res = self.planner.evaluate_and_replan(evt, sit)
        self.assertEqual(res["status"], "BUDGET_EXCEEDED")

    def test_20_failed_plan_produces_safe_replan(self):
        """Test 20: Event requiring action produces safe fallback proposal if auto action is unavailable."""
        self.supervisor.start()
        evt = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="gmail", entity_id="msg_320", payload={"sender": "prof@univ.edu", "subject": "Course task", "requires_action": True, "requires_planning": True, "allow_auto": False})
        sit = self.situation_model.build_situation(goals=[Goal("g20", "Coursework")])

        res = self.planner.evaluate_and_replan(evt, sit)
        self.assertEqual(res["status"], "REPLANNED")
        self.assertEqual(res["proactive_output"]["status"], "NOTIFIED")

    def test_21_event_storm_doesnt_cause_planning_storm(self):
        """Test 21: 50 rapid events hit replan budget cap without thrashing system."""
        self.supervisor.start()
        sit = self.situation_model.build_situation()

        replan_count = 0
        budget_exceeded_count = 0

        for i in range(50):
            evt = AgentEvent(event_type=EVENT_TASK_COMPLETED, source="task", entity_id=f"t_storm_{i}")
            res = self.planner.evaluate_and_replan(evt, sit)
            if res["status"] == "REPLANNED":
                replan_count += 1
            elif res["status"] in ("BUDGET_EXCEEDED", "NO_REPLAN_NEEDED"):
                budget_exceeded_count += 1

        self.assertLessEqual(replan_count, 5)
        self.assertTrue(budget_exceeded_count > 40)

    def test_22_long_running_goal_receives_attention(self):
        """Test 22: GoalArbitrator boosts score of unprocessed goals over cycles."""
        g1 = Goal("g1", "Main task", priority="HIGH")
        arb = GoalArbitrator()

        score1 = arb.score_goal(g1)
        arb.unprocessed_cycles["g1"] = 5
        score2 = arb.score_goal(g1)
        self.assertGreater(score2, score1)

    def test_23_low_priority_goals_dont_starve(self):
        """Test 23: Low priority goal receives starvation boost (+1.0 per cycle) and eventually surpasses un-updated goals."""
        g_low = Goal("g_low", "Low priority cleanup", priority="LOW") # Base 2.0
        g_normal = Goal("g_normal", "Normal priority item", priority="NORMAL") # Base 4.0

        arb = GoalArbitrator(starvation_increment=1.0)
        
        # Simulate g_low being unselected for 4 cycles
        arb.unprocessed_cycles["g_low"] = 4  # 2.0 + 4.0 = 6.0

        scored = arb.select_prioritized_goals([g_low, g_normal])
        # g_low (6.0) should now beat g_normal (4.0)
        self.assertEqual(scored[0][0].goal_id, "g_low")

if __name__ == "__main__":
    unittest.main()
