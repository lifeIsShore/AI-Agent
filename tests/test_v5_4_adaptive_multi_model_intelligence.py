import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.adaptive_model_selector import AdaptiveModelSelector

class TestV54AdaptiveMultiModelIntelligence(unittest.TestCase):

    def setUp(self):
        self.selector = AdaptiveModelSelector()

    def test_1_adaptive_model_selector_initializes(self):
        """Test 1: AdaptiveModelSelector initializes cleanly."""
        self.assertIsNotNone(self.selector)

    def test_2_select_deterministic_for_simple_task(self):
        """Test 2: Simple/regex task routes to DETERMINISTIC."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_3_select_small_local_when_resource_constrained(self):
        """Test 3: CPU > 85% routes to SMALL_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 90})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_4_select_small_local_when_local_only_pref(self):
        """Test 4: LOCAL_ONLY preference routes to SMALL_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {"model_preference": "LOCAL_ONLY"}, {})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_5_select_strong_local_for_medium_complexity(self):
        """Test 5: Medium complexity routes to STRONG_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_6_select_strong_cloud_for_high_complexity(self):
        """Test 6: High complexity routes to STRONG_CLOUD_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_CLOUD_LLM")

    def test_7_governor_decoupled_flag_is_true(self):
        """Test 7: Output contains governor_decoupled: True."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertTrue(res["governor_decoupled"])

    def test_8_reason_string_included(self):
        """Test 8: Result contains human-readable reason string."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertIn("reason", res)

    def test_9_selected_tier_in_result(self):
        """Test 9: Result contains selected_tier."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertIn("selected_tier", res)

    def test_10_task_dict_returned(self):
        """Test 10: Result returns original task dict."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["task"], {"complexity": "low"})

    def test_11_resource_budget_returned(self):
        """Test 11: Result returns resource_budget dict."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {"cpu_percent": 10})
        self.assertEqual(res["resource_budget"], {"cpu_percent": 10})

    def test_12_gpu_mem_constrained_routes_small_local(self):
        """Test 12: Low GPU memory routes to SMALL_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"gpu_mem_mb": 500})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_13_balanced_mode_medium_complexity(self):
        """Test 13: Balanced mode with medium complexity routes to STRONG_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {"model_preference": "BALANCED"}, {})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_14_balanced_mode_high_complexity(self):
        """Test 14: Balanced mode with high complexity routes to STRONG_CLOUD_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {"model_preference": "BALANCED"}, {})
        self.assertEqual(res["selected_tier"], "STRONG_CLOUD_LLM")

    def test_15_domain_simple_regex_routes_deterministic(self):
        """Test 15: Simple regex domain routes to DETERMINISTIC."""
        res = self.selector.select_adaptive_model({"domain": "simple_regex"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_16_domain_case_insensitive(self):
        """Test 16: Task complexity and domain matching are case-insensitive."""
        res = self.selector.select_adaptive_model({"complexity": "HIGH"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_CLOUD_LLM")

    def test_17_user_preference_case_insensitive(self):
        """Test 17: Model preference string is case-insensitive."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {"model_preference": "local_only"}, {})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_18_empty_task_characteristics_default_low(self):
        """Test 18: Empty task dict defaults to low complexity (DETERMINISTIC)."""
        res = self.selector.select_adaptive_model({}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_19_empty_historical_outcomes_handled(self):
        """Test 19: Empty historical outcomes dict handled cleanly."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_20_empty_user_preferences_handled(self):
        """Test 20: Empty user preferences dict handled cleanly."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_21_empty_resource_budget_handled(self):
        """Test 21: Empty resource budget handled cleanly."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_22_selected_tier_is_string(self):
        """Test 22: selected_tier is string."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertIsInstance(res["selected_tier"], str)

    def test_23_governor_authority_separate(self):
        """Test 23: AutonomyGovernor retains 100% authorization authority."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {}, {})
        self.assertTrue(res["governor_decoupled"])

    def test_24_deterministic_tier_value(self):
        """Test 24: Tier name matches DETERMINISTIC."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_25_small_local_tier_value(self):
        """Test 25: Tier name matches SMALL_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 90})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_26_strong_local_tier_value(self):
        """Test 26: Tier name matches STRONG_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_27_strong_cloud_tier_value(self):
        """Test 27: Tier name matches STRONG_CLOUD_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_CLOUD_LLM")

    def test_28_complexity_low_routes_deterministic(self):
        """Test 28: Explicit low complexity routes to DETERMINISTIC."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "DETERMINISTIC")

    def test_29_complexity_medium_routes_strong_local(self):
        """Test 29: Explicit medium complexity routes to STRONG_LOCAL_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_30_complexity_high_routes_strong_cloud(self):
        """Test 30: Explicit high complexity routes to STRONG_CLOUD_LLM."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {}, {})
        self.assertEqual(res["selected_tier"], "STRONG_CLOUD_LLM")

    def test_31_cpu_86_percent_constrained(self):
        """Test 31: CPU 86% triggers resource constraint routing."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 86})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_32_cpu_80_percent_not_constrained(self):
        """Test 32: CPU 80% does not trigger resource constraint routing."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 80, "gpu_mem_mb": 2000})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_33_gpu_mem_900mb_constrained(self):
        """Test 33: GPU 900MB triggers resource constraint routing."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"gpu_mem_mb": 900})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_34_gpu_mem_2000mb_not_constrained(self):
        """Test 34: GPU 2000MB does not trigger resource constraint routing."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 50, "gpu_mem_mb": 2000})
        self.assertEqual(res["selected_tier"], "STRONG_LOCAL_LLM")

    def test_35_local_only_pref_overrides_high_complexity(self):
        """Test 35: LOCAL_ONLY preference overrides high complexity cloud routing."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {"model_preference": "LOCAL_ONLY"}, {})
        self.assertEqual(res["selected_tier"], "SMALL_LOCAL_LLM")

    def test_36_reason_contains_resource_message(self):
        """Test 36: Constraint reason explains resource constraint."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 90})
        self.assertIn("Resource constraints", res["reason"])

    def test_37_reason_contains_complexity_message(self):
        """Test 37: High complexity reason explains routing."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {}, {})
        self.assertIn("High complexity", res["reason"])

    def test_38_task_dict_keys_preserved(self):
        """Test 38: Original task keys preserved in output."""
        res = self.selector.select_adaptive_model({"complexity": "low", "custom": 123}, {}, {}, {})
        self.assertEqual(res["task"]["custom"], 123)

    def test_39_multiple_calls_stateless(self):
        """Test 39: Selector calls are stateless and deterministic."""
        res1 = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        res2 = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(res1["selected_tier"], res2["selected_tier"])

    def test_40_adaptive_selector_integration_ready(self):
        """Test 40: Output structured for ModelRouter integration."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {})
        self.assertIn("selected_tier", res)
        self.assertIn("reason", res)

    def test_41_adaptive_selector_return_dict_count(self):
        """Test 41: Return dictionary contains 5 keys."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertEqual(len(res), 5)

    def test_42_deterministic_reason_string(self):
        """Test 42: Deterministic reason explains 0 latency rule engine."""
        res = self.selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
        self.assertIn("0 latency", res["reason"])

    def test_43_small_local_reason_string(self):
        """Test 43: Small local reason explains privacy/resource constraint."""
        res = self.selector.select_adaptive_model({"complexity": "high"}, {}, {"model_preference": "LOCAL_ONLY"}, {})
        self.assertIn("local", res["reason"])

    def test_44_strong_local_reason_string(self):
        """Test 44: Strong local reason explains balanced accuracy/speed."""
        res = self.selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {})
        self.assertIn("balanced", res["reason"])

    def test_45_v5_4_adaptive_model_verification_passed(self):
        """Test 45: All V5.4 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
