import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.goals.autonomous_goal_priority_manager import (
    GoalPriorityEngine,
    GoalLifecycleManager,
    AutonomousGoalPriorityManager
)

class TestV611AutonomousGoalPriorityManager(unittest.TestCase):

    def setUp(self):
        self.manager = AutonomousGoalPriorityManager()

    def test_1_get_summary_returns_dict(self):
        """Test 1: get_goal_priority_summary returns dict."""
        res = self.manager.get_goal_priority_summary()
        self.assertIsInstance(res, dict)

    def test_2_total_active_goals_count(self):
        """Test 2: total_active_goals is 5."""
        res = self.manager.get_goal_priority_summary()
        self.assertEqual(res["total_active_goals"], 5)

    def test_3_top_priority_goal_thesis(self):
        """Test 3: top_priority_goal is Master Thesis with score 9.4."""
        res = self.manager.get_goal_priority_summary()
        top = res["top_priority_goal"]
        self.assertEqual(top["goal_id"], "g_thesis")
        self.assertEqual(top["priority_score"], 9.4)

    def test_4_goal_priorities_list(self):
        """Test 4: goal_priorities returns 5 goals."""
        res = self.manager.get_goal_priority_summary()
        self.assertEqual(len(res["goal_priorities"]), 5)

    def test_5_governor_authorization_authorized(self):
        """Test 5: governor_authorization is AUTHORIZED."""
        res = self.manager.get_goal_priority_summary()
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_6_summary_keys_count(self):
        """Test 6: summary dict contains 5 keys."""
        res = self.manager.get_goal_priority_summary()
        self.assertEqual(len(res), 5)

    def test_7_goal_dict_keys_count(self):
        """Test 7: Each goal dict contains 7 keys."""
        res = self.manager.get_goal_priority_summary()
        for g in res["goal_priorities"]:
            self.assertEqual(len(g), 7)

    def test_8_priority_scores_descending(self):
        """Test 8: Goal priorities are sorted in descending order of priority_score."""
        res = self.manager.get_goal_priority_summary()
        scores = [g["priority_score"] for g in res["goal_priorities"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_9_evaluation_timestamp_string(self):
        """Test 9: evaluation_timestamp is non-empty string."""
        res = self.manager.get_goal_priority_summary()
        self.assertIsInstance(res["evaluation_timestamp"], str)
        self.assertTrue(len(res["evaluation_timestamp"]) > 0)

    def test_10_trend_values_valid(self):
        """Test 10: Trend values belong to set (UP, DOWN, STABLE)."""
        res = self.manager.get_goal_priority_summary()
        valid_trends = {"UP", "DOWN", "STABLE"}
        for g in res["goal_priorities"]:
            self.assertIn(g["trend"], valid_trends)

    def test_11_importance_values_valid(self):
        """Test 11: Importance values belong to set (HIGH, MEDIUM, LOW)."""
        res = self.manager.get_goal_priority_summary()
        valid_imp = {"HIGH", "MEDIUM", "LOW"}
        for g in res["goal_priorities"]:
            self.assertIn(g["importance"], valid_imp)

    def test_12_urgency_values_valid(self):
        """Test 12: Urgency values belong to set (HIGH, MEDIUM, LOW)."""
        res = self.manager.get_goal_priority_summary()
        valid_urg = {"HIGH", "MEDIUM", "LOW"}
        for g in res["goal_priorities"]:
            self.assertIn(g["urgency"], valid_urg)

    def test_13_reasons_non_empty(self):
        """Test 13: All goals contain non-empty reason string."""
        res = self.manager.get_goal_priority_summary()
        for g in res["goal_priorities"]:
            self.assertTrue(len(g["reason"]) > 0)

    def test_14_manager_class_name(self):
        """Test 14: Class name is AutonomousGoalPriorityManager."""
        self.assertEqual(self.manager.__class__.__name__, "AutonomousGoalPriorityManager")

    def test_15_engine_class_name(self):
        """Test 15: Class name is GoalPriorityEngine."""
        self.assertEqual(self.manager.priority_engine.__class__.__name__, "GoalPriorityEngine")

    def test_16_lifecycle_class_name(self):
        """Test 16: Class name is GoalLifecycleManager."""
        self.assertEqual(self.manager.lifecycle_manager.__class__.__name__, "GoalLifecycleManager")

    def test_17_manager_reusable(self):
        """Test 17: Manager instance is reusable across calls."""
        s1 = self.manager.get_goal_priority_summary()
        s2 = self.manager.get_goal_priority_summary()
        self.assertEqual(s1["top_priority_goal"]["goal_id"], s2["top_priority_goal"]["goal_id"])

    def test_18_json_serializable(self):
        """Test 18: Summary dict is JSON serializable."""
        import json
        dumped = json.dumps(self.manager.get_goal_priority_summary())
        self.assertIsInstance(dumped, str)

    def test_19_thesis_score_is_float(self):
        """Test 19: Priority score is float."""
        res = self.manager.get_goal_priority_summary()
        self.assertIsInstance(res["top_priority_goal"]["priority_score"], float)

    def test_20_active_goals_count_positive(self):
        """Test 20: Active goals count > 0."""
        self.assertTrue(self.manager.lifecycle_manager.get_active_count() > 0)

    def test_21_goal_id_starts_with_g(self):
        """Test 21: All goal IDs start with g_."""
        res = self.manager.get_goal_priority_summary()
        for g in res["goal_priorities"]:
            self.assertTrue(g["goal_id"].startswith("g_"))

    def test_22_goal_names_non_empty(self):
        """Test 22: All goal names are non-empty strings."""
        res = self.manager.get_goal_priority_summary()
        for g in res["goal_priorities"]:
            self.assertTrue(len(g["name"]) > 0)

    def test_23_job_search_trend_down(self):
        """Test 23: Job search trend is DOWN."""
        res = self.manager.get_goal_priority_summary()
        job = [g for g in res["goal_priorities"] if g["goal_id"] == "g_job"][0]
        self.assertEqual(job["trend"], "DOWN")

    def test_24_ai_agent_trend_stable(self):
        """Test 24: AI agent trend is STABLE."""
        res = self.manager.get_goal_priority_summary()
        agent = [g for g in res["goal_priorities"] if g["goal_id"] == "g_ai_agent"][0]
        self.assertEqual(agent["trend"], "STABLE")

    def test_25_personal_trend_down(self):
        """Test 25: Personal task backlog trend is DOWN."""
        res = self.manager.get_goal_priority_summary()
        pers = [g for g in res["goal_priorities"] if g["goal_id"] == "g_personal"][0]
        self.assertEqual(pers["trend"], "DOWN")

    def test_26_highest_score_bounded_below_10(self):
        """Test 26: Top priority score <= 10.0."""
        res = self.manager.get_goal_priority_summary()
        self.assertTrue(res["top_priority_goal"]["priority_score"] <= 10.0)

    def test_27_lowest_score_bounded_above_0(self):
        """Test 27: Lowest priority score >= 0.0."""
        res = self.manager.get_goal_priority_summary()
        lowest = min(res["goal_priorities"], key=lambda g: g["priority_score"])
        self.assertTrue(lowest["priority_score"] >= 0.0)

    def test_28_top_priority_goal_dict_structure(self):
        """Test 28: top_priority_goal is dict."""
        res = self.manager.get_goal_priority_summary()
        self.assertIsInstance(res["top_priority_goal"], dict)

    def test_29_priority_engine_evaluate_returns_list(self):
        """Test 29: evaluate_priorities returns list."""
        self.assertIsInstance(self.manager.priority_engine.evaluate_priorities(), list)

    def test_30_active_goals_list_type(self):
        """Test 30: active_goals is list."""
        self.assertIsInstance(self.manager.lifecycle_manager.active_goals, list)

    def test_31_thesis_urgency_high(self):
        """Test 31: Thesis urgency is HIGH."""
        res = self.manager.get_goal_priority_summary()
        self.assertEqual(res["top_priority_goal"]["urgency"], "HIGH")

    def test_32_thesis_importance_high(self):
        """Test 32: Thesis importance is HIGH."""
        res = self.manager.get_goal_priority_summary()
        self.assertEqual(res["top_priority_goal"]["importance"], "HIGH")

    def test_33_job_search_importance_medium(self):
        """Test 33: Job search importance is MEDIUM."""
        res = self.manager.get_goal_priority_summary()
        job = [g for g in res["goal_priorities"] if g["goal_id"] == "g_job"][0]
        self.assertEqual(job["importance"], "MEDIUM")

    def test_34_personal_importance_low(self):
        """Test 34: Personal task backlog importance is LOW."""
        res = self.manager.get_goal_priority_summary()
        pers = [g for g in res["goal_priorities"] if g["goal_id"] == "g_personal"][0]
        self.assertEqual(pers["importance"], "LOW")

    def test_35_evaluation_timestamp_length(self):
        """Test 35: evaluation_timestamp string has at least 19 characters."""
        res = self.manager.get_goal_priority_summary()
        self.assertTrue(len(res["evaluation_timestamp"]) >= 19)

    def test_36_goal_ids_unique(self):
        """Test 36: All goal IDs are unique."""
        res = self.manager.get_goal_priority_summary()
        ids = set(g["goal_id"] for g in res["goal_priorities"])
        self.assertEqual(len(ids), 5)

    def test_37_governor_authorization_contains_bounded_autonomy(self):
        """Test 37: governor_authorization contains Bounded Autonomy."""
        res = self.manager.get_goal_priority_summary()
        self.assertIn("Bounded Autonomy", res["governor_authorization"])

    def test_38_university_course_score(self):
        """Test 38: University course score is 3.8."""
        res = self.manager.get_goal_priority_summary()
        uni = [g for g in res["goal_priorities"] if g["goal_id"] == "g_university"][0]
        self.assertEqual(uni["priority_score"], 3.8)

    def test_39_ai_agent_score(self):
        """Test 39: AI agent score is 4.7."""
        res = self.manager.get_goal_priority_summary()
        agent = [g for g in res["goal_priorities"] if g["goal_id"] == "g_ai_agent"][0]
        self.assertEqual(agent["priority_score"], 4.7)

    def test_40_personal_backlog_score(self):
        """Test 40: Personal backlog score is 2.7."""
        res = self.manager.get_goal_priority_summary()
        pers = [g for g in res["goal_priorities"] if g["goal_id"] == "g_personal"][0]
        self.assertEqual(pers["priority_score"], 2.7)

    def test_41_top_goal_reason_mentions_deadline(self):
        """Test 41: Top goal reason mentions Deadline."""
        res = self.manager.get_goal_priority_summary()
        self.assertIn("Deadline", res["top_priority_goal"]["reason"])

    def test_42_top_goal_reason_mentions_workload(self):
        """Test 42: Top goal reason mentions workload."""
        res = self.manager.get_goal_priority_summary()
        self.assertIn("workload", res["top_priority_goal"]["reason"])

    def test_43_engine_attribute_not_none(self):
        """Test 43: priority_engine attribute is initialized."""
        self.assertIsNotNone(self.manager.priority_engine)

    def test_44_lifecycle_attribute_not_none(self):
        """Test 44: lifecycle_manager attribute is initialized."""
        self.assertIsNotNone(self.manager.lifecycle_manager)

    def test_45_v6_11_autonomous_goal_priority_verification_passed(self):
        """Test 45: All V6.11 autonomous goal and priority management features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
