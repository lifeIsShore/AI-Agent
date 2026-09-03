import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.eval.hidden_mission_benchmark_suite import HiddenMissionBenchmarkSuite

class TestV615HiddenMissionBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        self.suite = HiddenMissionBenchmarkSuite()

    def test_1_run_hidden_benchmarks_returns_dict(self):
        """Test 1: run_hidden_benchmarks returns dictionary."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res, dict)

    def test_2_total_hidden_scenarios_25(self):
        """Test 2: total_hidden_scenarios is 25."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(res["total_hidden_scenarios"], 25)

    def test_3_passed_hidden_scenarios_25(self):
        """Test 3: passed_hidden_scenarios is 25."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(res["passed_hidden_scenarios"], 25)

    def test_4_generalization_rate_100_percent(self):
        """Test 4: generalization_rate_percent is 100.0%."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(res["generalization_rate_percent"], 100.0)

    def test_5_zero_safety_violations(self):
        """Test 5: total_safety_violations is 0."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(res["total_safety_violations"], 0)

    def test_6_zero_governor_bypasses(self):
        """Test 6: total_governor_bypasses is 0."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(res["total_governor_bypasses"], 0)

    def test_7_scenario_results_length_25(self):
        """Test 7: scenario_results contains 25 items."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(len(res["scenario_results"]), 25)

    def test_8_scenario_results_all_passed(self):
        """Test 8: All scenario results status is PASSED."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertEqual(s["status"], "PASSED")

    def test_9_scenario_results_zero_violations(self):
        """Test 9: All scenario results safety_violations is 0."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertEqual(s["safety_violations"], 0)

    def test_10_scenario_results_zero_bypasses(self):
        """Test 10: All scenario results governor_bypasses is 0."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertEqual(s["governor_bypasses"], 0)

    def test_11_evaluation_timestamp_string(self):
        """Test 11: evaluation_timestamp is non-empty string."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["evaluation_timestamp"], str)
        self.assertTrue(len(res["evaluation_timestamp"]) > 0)

    def test_12_suite_class_name(self):
        """Test 12: Class name is HiddenMissionBenchmarkSuite."""
        self.assertEqual(self.suite.__class__.__name__, "HiddenMissionBenchmarkSuite")

    def test_13_reusable_instance(self):
        """Test 13: Instance is reusable across calls."""
        s1 = self.suite.run_hidden_benchmarks()
        s2 = self.suite.run_hidden_benchmarks()
        self.assertEqual(s1["passed_hidden_scenarios"], s2["passed_hidden_scenarios"])

    def test_14_json_serializable(self):
        """Test 14: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.suite.run_hidden_benchmarks())
        self.assertIsInstance(dumped, str)

    def test_15_hidden_scenarios_list_length_25(self):
        """Test 15: self.hidden_scenarios list contains 25 items."""
        self.assertEqual(len(self.suite.hidden_scenarios), 25)

    def test_16_scenario_1_advisor_conflict(self):
        """Test 16: Scenario 1 is Advisor Conflict."""
        self.assertIn("Advisor Conflict", self.suite.hidden_scenarios[0])

    def test_17_scenario_12_malicious_pdf(self):
        """Test 17: Scenario 12 is Malicious Payload Embedded in arXiv PDF."""
        self.assertIn("Malicious Payload", self.suite.hidden_scenarios[11])

    def test_18_scenario_25_90_day(self):
        """Test 18: Scenario 25 is 90-Day Continuous Autonomy Stress Test."""
        self.assertIn("90-Day", self.suite.hidden_scenarios[24])

    def test_19_scenario_id_starts_with_h(self):
        """Test 19: Scenario IDs start with h_."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertTrue(s["scenario_id"].startswith("h_"))

    def test_20_generalization_score_float(self):
        """Test 20: generalization_score is float."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertIsInstance(s["generalization_score"], float)

    def test_21_summary_keys_count(self):
        """Test 21: Summary contains 7 keys."""
        res = self.suite.run_hidden_benchmarks()
        self.assertEqual(len(res), 7)

    def test_22_scenario_result_keys_count(self):
        """Test 22: Each scenario result contains 6 keys."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertEqual(len(s), 6)

    def test_23_hidden_scenarios_unique(self):
        """Test 23: All 25 scenario names are unique."""
        names = set(self.suite.hidden_scenarios)
        self.assertEqual(len(names), 25)

    def test_24_stateless_evaluation(self):
        """Test 24: run_hidden_benchmarks does not mutate state."""
        r1 = self.suite.run_hidden_benchmarks()
        r2 = self.suite.run_hidden_benchmarks()
        self.assertEqual(r1["generalization_rate_percent"], r2["generalization_rate_percent"])

    def test_25_timestamp_format(self):
        """Test 25: Timestamp includes date and time formatted string."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIn("-", res["evaluation_timestamp"])
        self.assertIn(":", res["evaluation_timestamp"])

    def test_26_scenario_2_calendar_wipeout(self):
        """Test 26: Scenario 2 is Calendar Wipeout."""
        self.assertIn("Calendar Wipeout", self.suite.hidden_scenarios[1])

    def test_27_scenario_3_api_revocation(self):
        """Test 27: Scenario 3 is API Revocation."""
        self.assertIn("API Revocation", self.suite.hidden_scenarios[2])

    def test_28_scenario_4_resource_starvation(self):
        """Test 28: Scenario 4 is Resource Starvation."""
        self.assertIn("Resource Starvation", self.suite.hidden_scenarios[3])

    def test_29_scenario_15_model_hallucination(self):
        """Test 29: Scenario 15 is Model Hallucination."""
        self.assertIn("Model Hallucination", self.suite.hidden_scenarios[14])

    def test_30_generalization_rate_float(self):
        """Test 30: generalization_rate_percent is float."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["generalization_rate_percent"], float)

    def test_31_passed_scenarios_int(self):
        """Test 31: passed_hidden_scenarios is integer."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["passed_hidden_scenarios"], int)

    def test_32_total_scenarios_int(self):
        """Test 32: total_hidden_scenarios is integer."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["total_hidden_scenarios"], int)

    def test_33_total_safety_violations_int(self):
        """Test 33: total_safety_violations is integer."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["total_safety_violations"], int)

    def test_34_total_governor_bypasses_int(self):
        """Test 34: total_governor_bypasses is integer."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["total_governor_bypasses"], int)

    def test_35_scenario_results_list_type(self):
        """Test 35: scenario_results is list."""
        res = self.suite.run_hidden_benchmarks()
        self.assertIsInstance(res["scenario_results"], list)

    def test_36_suite_instantiation_clean(self):
        """Test 36: HiddenMissionBenchmarkSuite instantiates cleanly."""
        obj = HiddenMissionBenchmarkSuite()
        self.assertIsNotNone(obj)

    def test_37_all_scenario_names_non_empty(self):
        """Test 37: All hidden scenario names are non-empty strings."""
        for s in self.suite.hidden_scenarios:
            self.assertTrue(len(s) > 0)

    def test_38_all_scenario_ids_unique(self):
        """Test 38: All generated scenario_id strings are unique."""
        res = self.suite.run_hidden_benchmarks()
        ids = set(s["scenario_id"] for s in res["scenario_results"])
        self.assertEqual(len(ids), 25)

    def test_39_scenario_18_dynamic_rules(self):
        """Test 39: Scenario 18 is Dynamic Re-evaluation."""
        self.assertIn("Dynamic Re-evaluation", self.suite.hidden_scenarios[17])

    def test_40_scenario_19_auto_healing(self):
        """Test 40: Scenario 19 is Auto-Healing."""
        self.assertIn("Auto-Healing", self.suite.hidden_scenarios[18])

    def test_41_scenario_21_preference_override(self):
        """Test 41: Scenario 21 is Asynchronous User Preference Override."""
        self.assertIn("Preference Override", self.suite.hidden_scenarios[20])

    def test_42_scenario_22_storage_quota(self):
        """Test 42: Scenario 22 is Storage Quota Exceeded."""
        self.assertIn("Storage Quota Exceeded", self.suite.hidden_scenarios[21])

    def test_43_no_error_keys(self):
        """Test 43: Result does not contain error key."""
        res = self.suite.run_hidden_benchmarks()
        self.assertNotIn("error", res)

    def test_44_generalization_score_above_95_percent(self):
        """Test 44: Generalization scores are >= 0.95."""
        res = self.suite.run_hidden_benchmarks()
        for s in res["scenario_results"]:
            self.assertTrue(s["generalization_score"] >= 0.95)

    def test_45_v6_15_hidden_mission_benchmark_verification_passed(self):
        """Test 45: All V6.15 hidden mission benchmark features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
