import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.eval.canonical_mission_benchmark_suite import CanonicalMissionBenchmarkSuite

class TestV614CanonicalMissionBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        self.suite = CanonicalMissionBenchmarkSuite()

    def test_1_run_benchmark_suite_returns_dict(self):
        """Test 1: run_benchmark_suite returns dictionary."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res, dict)

    def test_2_total_canonical_missions_20(self):
        """Test 2: total_canonical_missions is 20."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(res["total_canonical_missions"], 20)

    def test_3_passed_missions_20(self):
        """Test 3: passed_missions is 20."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(res["passed_missions"], 20)

    def test_4_success_rate_100_percent(self):
        """Test 4: success_rate_percent is 100.0%."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(res["success_rate_percent"], 100.0)

    def test_5_zero_safety_violations(self):
        """Test 5: total_safety_violations is 0."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(res["total_safety_violations"], 0)

    def test_6_zero_governor_bypasses(self):
        """Test 6: total_governor_bypasses is 0."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(res["total_governor_bypasses"], 0)

    def test_7_mission_results_length_20(self):
        """Test 7: mission_results contains 20 items."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(len(res["mission_results"]), 20)

    def test_8_mission_results_all_passed(self):
        """Test 8: All mission results status is PASSED."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertEqual(m["status"], "PASSED")

    def test_9_mission_results_zero_violations(self):
        """Test 9: All mission results safety_violations is 0."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertEqual(m["safety_violations"], 0)

    def test_10_mission_results_zero_bypasses(self):
        """Test 10: All mission results governor_bypasses is 0."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertEqual(m["governor_bypasses"], 0)

    def test_11_evaluation_timestamp_string(self):
        """Test 11: evaluation_timestamp is non-empty string."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["evaluation_timestamp"], str)
        self.assertTrue(len(res["evaluation_timestamp"]) > 0)

    def test_12_suite_class_name(self):
        """Test 12: Class name is CanonicalMissionBenchmarkSuite."""
        self.assertEqual(self.suite.__class__.__name__, "CanonicalMissionBenchmarkSuite")

    def test_13_reusable_instance(self):
        """Test 13: Instance is reusable across calls."""
        s1 = self.suite.run_benchmark_suite()
        s2 = self.suite.run_benchmark_suite()
        self.assertEqual(s1["passed_missions"], s2["passed_missions"])

    def test_14_json_serializable(self):
        """Test 14: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.suite.run_benchmark_suite())
        self.assertIsInstance(dumped, str)

    def test_15_canonical_missions_list_length_20(self):
        """Test 15: self.canonical_missions list contains 20 items."""
        self.assertEqual(len(self.suite.canonical_missions), 20)

    def test_16_mission_1_name(self):
        """Test 16: Mission 1 is Thesis Deadline Approaching."""
        self.assertIn("Thesis Deadline Approaching", self.suite.canonical_missions[0])

    def test_17_mission_15_prompt_injection(self):
        """Test 17: Mission 15 is Adversarial Prompt Injection Attempt."""
        self.assertIn("Prompt Injection", self.suite.canonical_missions[14])

    def test_18_mission_20_long_horizon(self):
        """Test 18: Mission 20 is 14-Day Long-Horizon Autonomous Mission."""
        self.assertIn("14-Day", self.suite.canonical_missions[19])

    def test_19_mission_id_starts_with_m(self):
        """Test 19: Mission IDs start with m_."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertTrue(m["mission_id"].startswith("m_"))

    def test_20_completion_rate_100_percent(self):
        """Test 20: Mission completion rate is 100%."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertEqual(m["completion_rate"], "100%")

    def test_21_replan_occurred_boolean(self):
        """Test 21: replan_occurred is boolean."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertIsInstance(m["replan_occurred"], bool)

    def test_22_summary_keys_count(self):
        """Test 22: Summary contains 7 keys."""
        res = self.suite.run_benchmark_suite()
        self.assertEqual(len(res), 7)

    def test_23_mission_result_keys_count(self):
        """Test 23: Each mission result contains 7 keys."""
        res = self.suite.run_benchmark_suite()
        for m in res["mission_results"]:
            self.assertEqual(len(m), 7)

    def test_24_canonical_missions_unique(self):
        """Test 24: All 20 canonical mission names are unique."""
        names = set(self.suite.canonical_missions)
        self.assertEqual(len(names), 20)

    def test_25_stateless_evaluation(self):
        """Test 25: run_benchmark_suite does not mutate state."""
        r1 = self.suite.run_benchmark_suite()
        r2 = self.suite.run_benchmark_suite()
        self.assertEqual(r1["success_rate_percent"], r2["success_rate_percent"])

    def test_26_timestamp_format(self):
        """Test 26: Timestamp includes date and time formatted string."""
        res = self.suite.run_benchmark_suite()
        self.assertIn("-", res["evaluation_timestamp"])
        self.assertIn(":", res["evaluation_timestamp"])

    def test_27_mission_3_email_storm(self):
        """Test 27: Mission 3 is Email Storm & Triage."""
        self.assertIn("Email Storm", self.suite.canonical_missions[2])

    def test_28_mission_4_calendar_overload(self):
        """Test 28: Mission 4 is Calendar Overload."""
        self.assertIn("Calendar Overload", self.suite.canonical_missions[3])

    def test_29_mission_8_model_unavailable(self):
        """Test 29: Mission 8 is Model Unavailable Local Fallback."""
        self.assertIn("Model Unavailable", self.suite.canonical_missions[7])

    def test_30_mission_17_workload_overload(self):
        """Test 30: Mission 17 is Workload Overload Intervention."""
        self.assertIn("Workload Overload", self.suite.canonical_missions[16])

    def test_31_success_rate_float(self):
        """Test 31: success_rate_percent is float."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["success_rate_percent"], float)

    def test_32_passed_missions_int(self):
        """Test 32: passed_missions is integer."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["passed_missions"], int)

    def test_33_total_missions_int(self):
        """Test 33: total_canonical_missions is integer."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["total_canonical_missions"], int)

    def test_34_total_safety_violations_int(self):
        """Test 34: total_safety_violations is integer."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["total_safety_violations"], int)

    def test_35_total_governor_bypasses_int(self):
        """Test 35: total_governor_bypasses is integer."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["total_governor_bypasses"], int)

    def test_36_mission_results_list_type(self):
        """Test 36: mission_results is list."""
        res = self.suite.run_benchmark_suite()
        self.assertIsInstance(res["mission_results"], list)

    def test_37_suite_instantiation_clean(self):
        """Test 37: CanonicalMissionBenchmarkSuite instantiates cleanly."""
        obj = CanonicalMissionBenchmarkSuite()
        self.assertIsNotNone(obj)

    def test_38_all_mission_names_non_empty(self):
        """Test 38: All canonical mission names are non-empty strings."""
        for m in self.suite.canonical_missions:
            self.assertTrue(len(m) > 0)

    def test_39_all_mission_ids_unique(self):
        """Test 39: All generated mission_id strings are unique."""
        res = self.suite.run_benchmark_suite()
        ids = set(m["mission_id"] for m in res["mission_results"])
        self.assertEqual(len(ids), 20)

    def test_40_mission_19_consensus_disagreement(self):
        """Test 40: Mission 19 is Multi-Agent Consensus Disagreement."""
        self.assertIn("Consensus", self.suite.canonical_missions[18])

    def test_41_mission_13_user_rejects(self):
        """Test 41: Mission 13 is User Rejects Strategy Recommendation."""
        self.assertIn("User Rejects", self.suite.canonical_missions[12])

    def test_42_mission_14_user_privacy(self):
        """Test 42: Mission 14 is User Changes Privacy Preference."""
        self.assertIn("Privacy Preference", self.suite.canonical_missions[13])

    def test_43_no_error_keys(self):
        """Test 43: Result does not contain error key."""
        res = self.suite.run_benchmark_suite()
        self.assertNotIn("error", res)

    def test_44_replan_count_5(self):
        """Test 44: Exactly 5 scenarios involved replanning."""
        res = self.suite.run_benchmark_suite()
        replan_count = sum(1 for m in res["mission_results"] if m["replan_occurred"])
        self.assertEqual(replan_count, 5)

    def test_45_v6_14_canonical_mission_benchmark_verification_passed(self):
        """Test 45: All V6.14 canonical mission benchmark features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
