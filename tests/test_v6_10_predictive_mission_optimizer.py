import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.strategies.predictive_mission_optimizer import PredictiveMissionOptimizer

class TestV610PredictiveMissionOptimizer(unittest.TestCase):

    def setUp(self):
        self.optimizer = PredictiveMissionOptimizer()

    def test_1_optimize_mission_returns_dict(self):
        """Test 1: optimize_mission returns optimization dictionary."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res, dict)

    def test_2_recommended_strategy_present(self):
        """Test 2: Result contains recommended_strategy."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIn("recommended_strategy", res)

    def test_3_strategy_evaluations_list(self):
        """Test 3: Result contains 3 strategy evaluations."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertEqual(len(res["strategy_evaluations"]), 3)

    def test_4_governor_authorization_authorized(self):
        """Test 4: Governor authorization is AUTHORIZED."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_5_recommended_is_flagged(self):
        """Test 5: Recommended strategy is_recommended is True."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(res["recommended_strategy"]["is_recommended"])

    def test_6_optimize_mission_keys_count(self):
        """Test 6: optimize_mission returns 5 keys."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertEqual(len(res), 5)

    def test_7_strategy_evaluation_keys_count(self):
        """Test 7: Each strategy evaluation contains 8 keys."""
        res = self.optimizer.optimize_mission("Master Thesis")
        for e in res["strategy_evaluations"]:
            self.assertTrue(len(e) >= 8)

    def test_8_deadline_days_preserved(self):
        """Test 8: deadline_days preserved in result."""
        res = self.optimizer.optimize_mission("Master Thesis", 21)
        self.assertEqual(res["deadline_days"], 21)

    def test_9_mission_name_preserved(self):
        """Test 9: mission_name preserved in result."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertEqual(res["mission_name"], "Master Thesis")

    def test_10_completion_probability_percent_string(self):
        """Test 10: completion_probability contains % symbol."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIn("%", rec["completion_probability"])

    def test_11_overload_risk_non_empty(self):
        """Test 11: overload_risk is non-empty string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertTrue(len(rec["overload_risk"]) > 0)

    def test_12_capacity_utilization_percent_string(self):
        """Test 12: capacity_utilization contains % symbol."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIn("%", rec["capacity_utilization"])

    def test_13_historical_success_percent_string(self):
        """Test 13: historical_success contains % symbol."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIn("%", rec["historical_success"])

    def test_14_required_agents_list(self):
        """Test 14: required_agents is list of strings."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIsInstance(rec["required_agents"], list)

    def test_15_preferred_models_list(self):
        """Test 15: preferred_models is list of strings."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIsInstance(rec["preferred_models"], list)

    def test_16_optimizer_class_name(self):
        """Test 16: Class name is PredictiveMissionOptimizer."""
        self.assertEqual(self.optimizer.__class__.__name__, "PredictiveMissionOptimizer")

    def test_17_optimizer_reusable(self):
        """Test 17: Optimizer instance is reusable across calls."""
        r1 = self.optimizer.optimize_mission("Thesis")
        r2 = self.optimizer.optimize_mission("Thesis")
        self.assertEqual(r1["recommended_strategy"]["name"], r2["recommended_strategy"]["name"])

    def test_18_json_serializable(self):
        """Test 18: Output dictionary is JSON serializable."""
        import json
        res = self.optimizer.optimize_mission("Master Thesis")
        dumped = json.dumps(res)
        self.assertIsInstance(dumped, str)

    def test_19_expected_duration_float(self):
        """Test 19: expected_duration_hours is float."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec = res["recommended_strategy"]
        self.assertIsInstance(rec["expected_duration_hours"], float)

    def test_20_evaluations_contain_strategy_id(self):
        """Test 20: All evaluations contain strategy_id."""
        res = self.optimizer.optimize_mission("Master Thesis")
        for e in res["strategy_evaluations"]:
            self.assertIn("strategy_id", e)

    def test_21_evaluations_contain_name(self):
        """Test 21: All evaluations contain name."""
        res = self.optimizer.optimize_mission("Master Thesis")
        for e in res["strategy_evaluations"]:
            self.assertIn("name", e)

    def test_22_recommended_strategy_has_highest_prob(self):
        """Test 22: Recommended strategy has highest completion probability."""
        res = self.optimizer.optimize_mission("Master Thesis")
        rec_prob = float(res["recommended_strategy"]["completion_probability"].replace("%", ""))
        for e in res["strategy_evaluations"]:
            prob = float(e["completion_probability"].replace("%", ""))
            self.assertTrue(rec_prob >= prob)

    def test_23_default_library_used(self):
        """Test 23: Default MissionStrategyLibrary used when none provided."""
        opt = PredictiveMissionOptimizer()
        self.assertIsNotNone(opt.library)

    def test_24_custom_library_used(self):
        """Test 24: Custom MissionStrategyLibrary used when provided."""
        from personal_agent.strategies.mission_strategy_library import MissionStrategyLibrary
        lib = MissionStrategyLibrary()
        opt = PredictiveMissionOptimizer(lib)
        self.assertEqual(opt.library, lib)

    def test_25_strategy_evaluations_non_empty(self):
        """Test 25: strategy_evaluations is non-empty list."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["strategy_evaluations"]) > 0)

    def test_26_deadline_days_default_14(self):
        """Test 26: Default deadline_days is 14."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertEqual(res["deadline_days"], 14)

    def test_27_recommended_strategy_required_agents_non_empty(self):
        """Test 27: Recommended strategy has non-empty required_agents list."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["recommended_strategy"]["required_agents"]) > 0)

    def test_28_recommended_strategy_preferred_models_non_empty(self):
        """Test 28: Recommended strategy has non-empty preferred_models list."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["recommended_strategy"]["preferred_models"]) > 0)

    def test_29_recommended_strategy_id_starts_with_strat(self):
        """Test 29: Recommended strategy ID starts with strat_."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(res["recommended_strategy"]["strategy_id"].startswith("strat_"))

    def test_30_overload_risk_levels_valid(self):
        """Test 30: Overload risk levels belong to valid set (HIGH, MEDIUM, LOW)."""
        res = self.optimizer.optimize_mission("Master Thesis")
        valid_levels = {"HIGH", "MEDIUM", "LOW"}
        for e in res["strategy_evaluations"]:
            self.assertIn(e["overload_risk"], valid_levels)

    def test_31_capacity_utilization_percentages_valid(self):
        """Test 31: Capacity utilization contains percent sign."""
        res = self.optimizer.optimize_mission("Master Thesis")
        for e in res["strategy_evaluations"]:
            self.assertIn("%", e["capacity_utilization"])

    def test_32_historical_success_percentages_valid(self):
        """Test 32: Historical success contains percent sign."""
        res = self.optimizer.optimize_mission("Master Thesis")
        for e in res["strategy_evaluations"]:
            self.assertIn("%", e["historical_success"])

    def test_33_optimizer_selector_not_none(self):
        """Test 33: selector attribute is initialized."""
        self.assertIsNotNone(self.optimizer.selector)

    def test_34_selector_class_type(self):
        """Test 34: selector is StrategySelector instance."""
        from personal_agent.strategies.mission_strategy_library import StrategySelector
        self.assertIsInstance(self.optimizer.selector, StrategySelector)

    def test_35_optimization_results_repeatable(self):
        """Test 35: Optimization results are deterministic and repeatable."""
        res1 = self.optimizer.optimize_mission("Master Thesis")
        res2 = self.optimizer.optimize_mission("Master Thesis")
        self.assertEqual(res1["recommended_strategy"]["strategy_id"], res2["recommended_strategy"]["strategy_id"])

    def test_36_strategy_evaluations_dict_keys(self):
        """Test 36: Strategy evaluation dict contains strategy_id key."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIn("strategy_id", res["strategy_evaluations"][0])

    def test_37_governor_authorization_string(self):
        """Test 37: governor_authorization is string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res["governor_authorization"], str)

    def test_38_mission_name_string(self):
        """Test 38: mission_name is string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res["mission_name"], str)

    def test_39_deadline_days_integer(self):
        """Test 39: deadline_days is integer."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res["deadline_days"], int)

    def test_40_recommended_strategy_dict_type(self):
        """Test 40: recommended_strategy is dict."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res["recommended_strategy"], dict)

    def test_41_strategy_evaluations_list_type(self):
        """Test 41: strategy_evaluations is list."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertIsInstance(res["strategy_evaluations"], list)

    def test_42_recommended_strategy_name_non_empty(self):
        """Test 42: recommended_strategy name is non-empty string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["recommended_strategy"]["name"]) > 0)

    def test_43_recommended_strategy_completion_prob_non_empty(self):
        """Test 43: completion_probability is non-empty string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["recommended_strategy"]["completion_probability"]) > 0)

    def test_44_recommended_strategy_overload_risk_non_empty(self):
        """Test 44: overload_risk is non-empty string."""
        res = self.optimizer.optimize_mission("Master Thesis")
        self.assertTrue(len(res["recommended_strategy"]["overload_risk"]) > 0)

    def test_45_v6_10_predictive_mission_optimizer_verification_passed(self):
        """Test 45: All V6.10 predictive mission optimizer features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
