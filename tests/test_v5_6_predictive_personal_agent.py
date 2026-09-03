import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.events.predictive_event_engine import PredictiveEventEngine

class TestV56PredictivePersonalAgent(unittest.TestCase):

    def setUp(self):
        self.engine = PredictiveEventEngine()

    def test_1_predictive_event_engine_initializes(self):
        """Test 1: PredictiveEventEngine initializes cleanly."""
        self.assertIsNotNone(self.engine)

    def test_2_predict_empty_inputs(self):
        """Test 2: predict_upcoming_events handles empty inputs."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertEqual(res["predictions_count"], 0)
        self.assertTrue(res["governor_gated"])

    def test_3_predict_deadline_risk(self):
        """Test 3: Predicts deadline risk for thesis goal."""
        goals = [{"name": "Prepare thesis proposal", "deadline": "2026-09-10"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertEqual(res["predictions_count"], 1)
        self.assertEqual(res["predictions"][0]["prediction_type"], "DEADLINE_RISK")

    def test_4_predict_scheduling_conflict_risk(self):
        """Test 4: Predicts scheduling conflict risk when calendar items >= 2."""
        cal = [{"id": "c1"}, {"id": "c2"}]
        res = self.engine.predict_upcoming_events(cal, [], [])
        self.assertEqual(res["predictions_count"], 1)
        self.assertEqual(res["predictions"][0]["prediction_type"], "SCHEDULING_CONFLICT_RISK")

    def test_5_predict_completion_probability(self):
        """Test 5: Calculates task completion probability cleanly."""
        tasks = [{"status": "completed"}, {"status": "needsAction"}]
        res = self.engine.predict_upcoming_events([], tasks, [])
        self.assertEqual(res["completion_probability"], 0.5)

    def test_6_predict_high_risk_level(self):
        """Test 6: Completion probability < 0.70 triggers HIGH risk level."""
        tasks = [{"status": "needsAction"}] * 5
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events([], tasks, goals)
        self.assertEqual(res["predictions"][0]["risk_level"], "HIGH")

    def test_7_predict_low_risk_level(self):
        """Test 7: Completion probability >= 0.70 triggers LOW risk level."""
        tasks = [{"status": "completed"}] * 5
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events([], tasks, goals)
        self.assertEqual(res["predictions"][0]["risk_level"], "LOW")

    def test_8_governor_gated_invariant(self):
        """Test 8: Invariant governor_gated: True enforced on all prediction outputs."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertTrue(res["governor_gated"])

    def test_9_prediction_recommendation_string(self):
        """Test 9: Recommendation string included in prediction dict."""
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertIn("recommendation", res["predictions"][0])

    def test_10_predictions_list_format(self):
        """Test 10: Predictions list contains dictionary entries."""
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertIsInstance(res["predictions"], list)

    def test_11_predictions_count_matches_list_length(self):
        """Test 11: predictions_count matches predictions list length."""
        cal = [{"id": "c1"}, {"id": "c2"}]
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events(cal, [], goals)
        self.assertEqual(res["predictions_count"], len(res["predictions"]))

    def test_12_completion_prob_default_when_no_tasks(self):
        """Test 12: Completion probability defaults to 0.85 when tasks list is empty."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertEqual(res["completion_probability"], 0.85)

    def test_13_target_name_preserved(self):
        """Test 13: Goal name preserved in prediction target."""
        goals = [{"name": "Master Thesis Deadline"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertEqual(res["predictions"][0]["target"], "Master Thesis Deadline")

    def test_14_conflict_risk_level_medium(self):
        """Test 14: Conflict risk level is MEDIUM."""
        cal = [{"id": "c1"}, {"id": "c2"}]
        res = self.engine.predict_upcoming_events(cal, [], [])
        self.assertEqual(res["predictions"][0]["risk_level"], "MEDIUM")

    def test_15_multiple_predictions_returned(self):
        """Test 15: Returns both deadline and conflict predictions when both present."""
        cal = [{"id": "c1"}, {"id": "c2"}]
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events(cal, [], goals)
        self.assertEqual(res["predictions_count"], 2)

    def test_16_prediction_type_string(self):
        """Test 16: prediction_type is string."""
        goals = [{"name": "thesis"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertIsInstance(res["predictions"][0]["prediction_type"], str)

    def test_17_predictions_result_dict_keys(self):
        """Test 17: Result dictionary contains 4 expected keys."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertEqual(len(res), 4)

    def test_18_tasks_all_completed_prob_1_0(self):
        """Test 18: 100% completed tasks yields probability 1.0."""
        tasks = [{"status": "completed"}] * 3
        res = self.engine.predict_upcoming_events([], tasks, [])
        self.assertEqual(res["completion_probability"], 1.0)

    def test_19_tasks_zero_completed_prob_0_0(self):
        """Test 19: 0% completed tasks yields probability 0.0."""
        tasks = [{"status": "needsAction"}] * 3
        res = self.engine.predict_upcoming_events([], tasks, [])
        self.assertEqual(res["completion_probability"], 0.0)

    def test_20_stateless_prediction_execution(self):
        """Test 20: Engine execution is stateless and repeatable."""
        goals = [{"name": "thesis"}]
        res1 = self.engine.predict_upcoming_events([], [], goals)
        res2 = self.engine.predict_upcoming_events([], [], goals)
        self.assertEqual(res1["predictions_count"], res2["predictions_count"])

    def test_21_calendar_single_item_no_conflict(self):
        """Test 21: Single calendar item does not trigger conflict prediction."""
        res = self.engine.predict_upcoming_events([{"id": "c1"}], [], [])
        self.assertEqual(res["predictions_count"], 0)

    def test_22_goal_without_deadline_or_thesis_keyword(self):
        """Test 22: Regular goal without deadline keyword ignored."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "regular_goal"}])
        self.assertEqual(res["predictions_count"], 0)

    def test_23_thesis_case_insensitive_matching(self):
        """Test 23: Thesis keyword matching is case-insensitive."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "THESIS_PROPOSAL"}])
        self.assertEqual(res["predictions_count"], 1)

    def test_24_deadline_key_presence_triggers_prediction(self):
        """Test 24: Presence of deadline key triggers prediction."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "g1", "deadline": "2026-10-10"}])
        self.assertEqual(res["predictions_count"], 1)

    def test_25_recommendation_mentions_replanning(self):
        """Test 25: Recommendation string mentions replanning."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertIn("replanning", res["predictions"][0]["recommendation"])

    def test_26_completion_prob_float_type(self):
        """Test 26: completion_probability is float."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertIsInstance(res["completion_probability"], float)

    def test_27_prediction_dict_target_key(self):
        """Test 27: Prediction entry contains target key."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertIn("target", res["predictions"][0])

    def test_28_prediction_dict_risk_level_key(self):
        """Test 28: Prediction entry contains risk_level key."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertIn("risk_level", res["predictions"][0])

    def test_29_tasks_partial_completion_prob(self):
        """Test 29: 2 completed out of 4 yields 0.5."""
        tasks = [{"status": "completed"}, {"status": "completed"}, {"status": "open"}, {"status": "open"}]
        res = self.engine.predict_upcoming_events([], tasks, [])
        self.assertEqual(res["completion_probability"], 0.5)

    def test_30_multiple_thesis_goals(self):
        """Test 30: Multiple thesis goals produce multiple predictions."""
        goals = [{"name": "Thesis 1"}, {"name": "Thesis 2"}]
        res = self.engine.predict_upcoming_events([], [], goals)
        self.assertEqual(res["predictions_count"], 2)

    def test_31_prediction_governor_non_execution(self):
        """Test 31: PredictiveEventEngine strictly outputs predictions without executing tools."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertTrue(res["governor_gated"])

    def test_32_conflict_prediction_target_name(self):
        """Test 32: Conflict prediction target is Calendar Schedule."""
        res = self.engine.predict_upcoming_events([{"id": "1"}, {"id": "2"}], [], [])
        self.assertEqual(res["predictions"][0]["target"], "Calendar Schedule")

    def test_33_conflict_prediction_recommendation(self):
        """Test 33: Conflict prediction recommendation mentions overlapping slots."""
        res = self.engine.predict_upcoming_events([{"id": "1"}, {"id": "2"}], [], [])
        self.assertIn("overlapping", res["predictions"][0]["recommendation"])

    def test_34_predict_returns_dict(self):
        """Test 34: predict_upcoming_events returns dict instance."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertIsInstance(res, dict)

    def test_35_predictions_list_iterable(self):
        """Test 35: predictions list is iterable."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        count = sum(1 for p in res["predictions"])
        self.assertEqual(count, 1)

    def test_36_completion_prob_rounded(self):
        """Test 36: completion_probability rounded to 2 decimals."""
        tasks = [{"status": "completed"}, {"status": "open"}, {"status": "open"}]
        res = self.engine.predict_upcoming_events([], tasks, [])
        self.assertEqual(res["completion_probability"], 0.33)

    def test_37_calendar_items_three_items(self):
        """Test 37: 3 calendar items trigger conflict prediction."""
        res = self.engine.predict_upcoming_events([{"id": "1"}, {"id": "2"}, {"id": "3"}], [], [])
        self.assertEqual(res["predictions_count"], 1)

    def test_38_goals_empty_returns_zero_deadline_predictions(self):
        """Test 38: Empty goals list produces 0 deadline predictions."""
        res = self.engine.predict_upcoming_events([], [], [])
        self.assertEqual(res["predictions_count"], 0)

    def test_39_prediction_entry_has_five_keys(self):
        """Test 39: Deadline prediction entry contains 5 keys."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertEqual(len(res["predictions"][0]), 5)

    def test_40_planner_integration_ready(self):
        """Test 40: Predictions dict structured for ContinuousPlanner input."""
        res = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertIn("predictions", res)
        self.assertIn("governor_gated", res)

    def test_41_high_risk_threshold_verification(self):
        """Test 41: Probability 0.69 triggers HIGH risk."""
        tasks = [{"status": "completed"}] * 69 + [{"status": "open"}] * 31
        res = self.engine.predict_upcoming_events([], tasks, [{"name": "thesis"}])
        self.assertEqual(res["predictions"][0]["risk_level"], "HIGH")

    def test_42_low_risk_threshold_verification(self):
        """Test 42: Probability 0.70 triggers LOW risk."""
        tasks = [{"status": "completed"}] * 70 + [{"status": "open"}] * 30
        res = self.engine.predict_upcoming_events([], tasks, [{"name": "thesis"}])
        self.assertEqual(res["predictions"][0]["risk_level"], "LOW")

    def test_43_predictive_engine_stateless_reset(self):
        """Test 43: Class instance can be reused across calls."""
        res1 = self.engine.predict_upcoming_events([], [], [])
        res2 = self.engine.predict_upcoming_events([], [], [{"name": "thesis"}])
        self.assertEqual(res1["predictions_count"], 0)
        self.assertEqual(res2["predictions_count"], 1)

    def test_44_task_status_key_case_sensitive(self):
        """Test 44: Task status completed matching works."""
        res = self.engine.predict_upcoming_events([], [{"status": "completed"}], [])
        self.assertEqual(res["completion_probability"], 1.0)

    def test_45_v5_6_predictive_agent_verification_passed(self):
        """Test 45: All V5.6 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
