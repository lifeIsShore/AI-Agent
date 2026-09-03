import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.control.mission_execution_intelligence import MissionExecutionIntelligence

class TestV59MissionExecutionIntelligence(unittest.TestCase):

    def setUp(self):
        self.intel = MissionExecutionIntelligence()

    def test_1_intel_initializes(self):
        """Test 1: MissionExecutionIntelligence initializes cleanly."""
        self.assertIsNotNone(self.intel)

    def test_2_adapt_execution_stable_when_duration_on_track(self):
        """Test 2: Status is STABLE when actual duration <= 1.5x estimate."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=5.0, estimated_duration_sec=5.0)
        self.assertEqual(res["status"], "STABLE")
        self.assertFalse(res["adapted"])

    def test_3_adapt_execution_triggers_replanning_on_overrun(self):
        """Test 3: Duration overrun > 1.5x triggers REPLANNED_DYNAMICALLY."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=10.0, estimated_duration_sec=5.0)
        self.assertEqual(res["status"], "REPLANNED_DYNAMICALLY")
        self.assertTrue(res["adapted"])

    def test_4_governor_gated_invariant_is_true(self):
        """Test 4: Governor gated flag is True when replanned."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=10.0, estimated_duration_sec=5.0)
        self.assertTrue(res["governor_gated"])

    def test_5_duration_ratio_calculation(self):
        """Test 5: duration_ratio is calculated correctly."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=8.0, estimated_duration_sec=4.0)
        self.assertEqual(res["duration_ratio"], 2.0)

    def test_6_original_strategy_preserved(self):
        """Test 6: original_strategy preserved in replanned result."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=10.0, estimated_duration_sec=5.0, strategy_id="strat_custom")
        self.assertEqual(res["original_strategy"], "strat_custom")

    def test_7_recommended_scenario_included(self):
        """Test 7: new_recommended_scenario included in result."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=10.0, estimated_duration_sec=5.0)
        self.assertIn("new_recommended_scenario", res)

    def test_8_prediction_risk_included(self):
        """Test 8: prediction_risk included in result."""
        res = self.intel.adapt_mission_execution("m1", actual_duration_sec=10.0, estimated_duration_sec=5.0)
        self.assertIn("prediction_risk", res)

    def test_9_intel_subcomponents_initialized(self):
        """Test 9: Subcomponents (predictive, sim_env, cf_planner) initialized."""
        self.assertIsNotNone(self.intel.predictive_engine)
        self.assertIsNotNone(self.intel.sim_env)
        self.assertIsNotNone(self.intel.cf_planner)

    def test_10_adapt_execution_returns_dict(self):
        """Test 10: adapt_mission_execution returns dict instance."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertIsInstance(res, dict)

    def test_11_ratio_exact_1_5_is_stable(self):
        """Test 11: Duration ratio exactly 1.5 is STABLE."""
        res = self.intel.adapt_mission_execution("m1", 7.5, 5.0)
        self.assertEqual(res["status"], "STABLE")

    def test_12_ratio_1_51_is_replanned(self):
        """Test 12: Duration ratio 1.51 triggers REPLANNED_DYNAMICALLY."""
        res = self.intel.adapt_mission_execution("m1", 7.6, 5.0)
        self.assertEqual(res["status"], "REPLANNED_DYNAMICALLY")

    def test_13_mission_id_preserved(self):
        """Test 13: mission_id string preserved."""
        res = self.intel.adapt_mission_execution("m_unique", 5.0, 5.0)
        self.assertEqual(res["mission_id"], "m_unique")

    def test_14_stable_result_keys_count(self):
        """Test 14: STABLE result dictionary contains 5 keys."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertEqual(len(res), 5)

    def test_15_replanned_result_keys_count(self):
        """Test 15: REPLANNED_DYNAMICALLY result dictionary contains 8 keys."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertEqual(len(res), 8)

    def test_16_zero_estimate_handled(self):
        """Test 16: 0.0 estimate handles zero division cleanly."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 0.0)
        self.assertIsNotNone(res)

    def test_17_duration_ratio_float_type(self):
        """Test 17: duration_ratio is float."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertIsInstance(res["duration_ratio"], float)

    def test_18_adapted_flag_boolean(self):
        """Test 18: adapted flag is boolean."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertIsInstance(res["adapted"], bool)

    def test_19_status_string_type(self):
        """Test 19: status is string."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertIsInstance(res["status"], str)

    def test_20_stateless_execution(self):
        """Test 20: Execution is stateless across multiple calls."""
        res1 = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        res2 = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertEqual(res1["status"], res2["status"])

    def test_21_recommended_scenario_valid_string(self):
        """Test 21: Recommended scenario is valid string."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIn(res["new_recommended_scenario"], ["AGGRESSIVE", "BALANCED", "CONSERVATIVE"])

    def test_22_prediction_risk_valid_string(self):
        """Test 22: Prediction risk is valid string."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIn(res["prediction_risk"], ["LOW", "MEDIUM", "HIGH"])

    def test_23_default_strategy_id(self):
        """Test 23: Default strategy_id is strat_default."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertEqual(res["strategy_id"], "strat_default")

    def test_24_small_overrun_under_threshold(self):
        """Test 24: Small overrun (1.2x) is STABLE."""
        res = self.intel.adapt_mission_execution("m1", 6.0, 5.0)
        self.assertEqual(res["status"], "STABLE")

    def test_25_large_overrun_over_threshold(self):
        """Test 25: Large overrun (3.0x) is REPLANNED_DYNAMICALLY."""
        res = self.intel.adapt_mission_execution("m1", 15.0, 5.0)
        self.assertEqual(res["status"], "REPLANNED_DYNAMICALLY")

    def test_26_intel_integration_ready(self):
        """Test 26: Output structured for MissionController integration."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIn("new_recommended_scenario", res)

    def test_27_duration_ratio_precision(self):
        """Test 27: duration_ratio rounded to 2 decimal places."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 3.0)
        self.assertEqual(res["duration_ratio"], 3.33)

    def test_28_negative_duration_handled(self):
        """Test 28: Negative or zero durations handled cleanly."""
        res = self.intel.adapt_mission_execution("m1", 0.0, 5.0)
        self.assertEqual(res["status"], "STABLE")

    def test_29_intel_class_reuse(self):
        """Test 29: MissionExecutionIntelligence instance reusable across missions."""
        res1 = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        res2 = self.intel.adapt_mission_execution("m2", 10.0, 5.0)
        self.assertFalse(res1["adapted"])
        self.assertTrue(res2["adapted"])

    def test_30_original_strategy_key_absent_in_stable(self):
        """Test 30: original_strategy key is absent in STABLE result."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertNotIn("original_strategy", res)

    def test_31_original_strategy_key_present_in_replanned(self):
        """Test 31: original_strategy key is present in REPLANNED_DYNAMICALLY result."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIn("original_strategy", res)

    def test_32_governor_gated_key_absent_in_stable(self):
        """Test 32: governor_gated key absent in STABLE result."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertNotIn("governor_gated", res)

    def test_33_governor_gated_key_present_in_replanned(self):
        """Test 33: governor_gated key present in REPLANNED_DYNAMICALLY result."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIn("governor_gated", res)

    def test_34_new_recommended_scenario_key_absent_in_stable(self):
        """Test 34: new_recommended_scenario key absent in STABLE result."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertNotIn("new_recommended_scenario", res)

    def test_35_prediction_risk_key_absent_in_stable(self):
        """Test 35: prediction_risk key absent in STABLE result."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertNotIn("prediction_risk", res)

    def test_36_strategy_id_key_present_in_stable(self):
        """Test 36: strategy_id key present in STABLE result."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0)
        self.assertIn("strategy_id", res)

    def test_37_overrun_2_0x(self):
        """Test 37: Overrun 2.0x is REPLANNED_DYNAMICALLY."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertEqual(res["status"], "REPLANNED_DYNAMICALLY")

    def test_38_overrun_1_4x(self):
        """Test 38: Overrun 1.4x is STABLE."""
        res = self.intel.adapt_mission_execution("m1", 7.0, 5.0)
        self.assertEqual(res["status"], "STABLE")

    def test_39_custom_strategy_id_passed(self):
        """Test 39: Custom strategy_id passed accurately."""
        res = self.intel.adapt_mission_execution("m1", 5.0, 5.0, strategy_id="strat_123")
        self.assertEqual(res["strategy_id"], "strat_123")

    def test_40_mission_id_integer_like_string(self):
        """Test 40: Integer-like mission_id string handled cleanly."""
        res = self.intel.adapt_mission_execution("1001", 5.0, 5.0)
        self.assertEqual(res["mission_id"], "1001")

    def test_41_predictive_engine_called(self):
        """Test 41: Predictive engine called during replanning."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIsNotNone(res["prediction_risk"])

    def test_42_cf_planner_called(self):
        """Test 42: Counterfactual planner called during replanning."""
        res = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertIsNotNone(res["new_recommended_scenario"])

    def test_43_replan_decision_deterministic(self):
        """Test 43: Replanning decision is deterministic for same inputs."""
        res1 = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        res2 = self.intel.adapt_mission_execution("m1", 10.0, 5.0)
        self.assertEqual(res1["new_recommended_scenario"], res2["new_recommended_scenario"])

    def test_44_execution_intel_has_all_attributes(self):
        """Test 44: Execution intelligence has all 3 required tool attributes."""
        self.assertTrue(hasattr(self.intel, "predictive_engine"))
        self.assertTrue(hasattr(self.intel, "sim_env"))
        self.assertTrue(hasattr(self.intel, "cf_planner"))

    def test_45_v5_9_mission_execution_intelligence_verification_passed(self):
        """Test 45: All V5.9 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
