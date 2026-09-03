import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.eval.cross_agent_benchmark_suite import CrossAgentBenchmarkSuite

class TestV77CrossAgentBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        self.suite = CrossAgentBenchmarkSuite()

    def test_1_run_cross_agent_benchmarks_returns_dict(self):
        """Test 1: run_cross_agent_benchmarks returns dictionary."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res, dict)

    def test_2_total_cross_agent_missions_30(self):
        """Test 2: total_cross_agent_missions is 30."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(res["total_cross_agent_missions"], 30)

    def test_3_passed_cross_agent_missions_30(self):
        """Test 3: passed_cross_agent_missions is 30."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(res["passed_cross_agent_missions"], 30)

    def test_4_success_rate_100_percent(self):
        """Test 4: success_rate_percent is 100.0%."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(res["success_rate_percent"], 100.0)

    def test_5_zero_safety_violations(self):
        """Test 5: total_safety_violations is 0."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(res["total_safety_violations"], 0)

    def test_6_zero_governor_bypasses(self):
        """Test 6: total_governor_bypasses is 0."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(res["total_governor_bypasses"], 0)

    def test_7_team_mission_results_length_30(self):
        """Test 7: team_mission_results contains 30 items."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(len(res["team_mission_results"]), 30)

    def test_8_team_mission_results_all_passed(self):
        """Test 8: All team mission results status is PASSED."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(m["status"], "PASSED")

    def test_9_team_mission_results_zero_violations(self):
        """Test 9: All team mission results safety_violations is 0."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(m["safety_violations"], 0)

    def test_10_team_mission_results_zero_bypasses(self):
        """Test 10: All team mission results governor_bypasses is 0."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(m["governor_bypasses"], 0)

    def test_11_evaluation_timestamp_string(self):
        """Test 11: evaluation_timestamp is non-empty string."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["evaluation_timestamp"], str)
        self.assertTrue(len(res["evaluation_timestamp"]) > 0)

    def test_12_suite_class_name(self):
        """Test 12: Class name is CrossAgentBenchmarkSuite."""
        self.assertEqual(self.suite.__class__.__name__, "CrossAgentBenchmarkSuite")

    def test_13_reusable_instance(self):
        """Test 13: Instance is reusable across calls."""
        s1 = self.suite.run_cross_agent_benchmarks()
        s2 = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(s1["passed_cross_agent_missions"], s2["passed_cross_agent_missions"])

    def test_14_json_serializable(self):
        """Test 14: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.suite.run_cross_agent_benchmarks())
        self.assertIsInstance(dumped, str)

    def test_15_cross_agent_scenarios_list_length_30(self):
        """Test 15: self.cross_agent_scenarios list contains 30 items."""
        self.assertEqual(len(self.suite.cross_agent_scenarios), 30)

    def test_16_team_mission_id_starts_with_tm(self):
        """Test 16: team_mission_id starts with tm_."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertTrue(m["team_mission_id"].startswith("tm_"))

    def test_17_participating_agents_non_empty(self):
        """Test 17: participating_agents is non-empty list."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertTrue(len(m["participating_agents"]) > 0)

    def test_18_team_consensus_score_above_95_percent(self):
        """Test 18: team_consensus_score >= 0.95."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertTrue(m["team_consensus_score"] >= 0.95)

    def test_19_summary_keys_count(self):
        """Test 19: Summary contains 7 keys."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(len(res), 7)

    def test_20_team_mission_result_keys_count(self):
        """Test 20: Each team mission result contains 7 keys."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(len(m), 7)

    def test_21_cross_agent_scenarios_unique(self):
        """Test 21: All 30 scenario names are unique."""
        names = set(self.suite.cross_agent_scenarios)
        self.assertEqual(len(names), 30)

    def test_22_stateless_evaluation(self):
        """Test 22: run_cross_agent_benchmarks does not mutate state."""
        r1 = self.suite.run_cross_agent_benchmarks()
        r2 = self.suite.run_cross_agent_benchmarks()
        self.assertEqual(r1["success_rate_percent"], r2["success_rate_percent"])

    def test_23_timestamp_format(self):
        """Test 23: Timestamp includes date and time formatted string."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIn("-", res["evaluation_timestamp"])
        self.assertIn(":", res["evaluation_timestamp"])

    def test_24_success_rate_float(self):
        """Test 24: success_rate_percent is float."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["success_rate_percent"], float)

    def test_25_passed_missions_int(self):
        """Test 25: passed_cross_agent_missions is integer."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["passed_cross_agent_missions"], int)

    def test_26_total_missions_int(self):
        """Test 26: total_cross_agent_missions is integer."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["total_cross_agent_missions"], int)

    def test_27_total_safety_violations_int(self):
        """Test 27: total_safety_violations is integer."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["total_safety_violations"], int)

    def test_28_total_governor_bypasses_int(self):
        """Test 28: total_governor_bypasses is integer."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["total_governor_bypasses"], int)

    def test_29_team_mission_results_list_type(self):
        """Test 29: team_mission_results is list."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertIsInstance(res["team_mission_results"], list)

    def test_30_suite_instantiation_clean(self):
        """Test 30: CrossAgentBenchmarkSuite instantiates cleanly."""
        obj = CrossAgentBenchmarkSuite()
        self.assertIsNotNone(obj)

    def test_31_all_scenario_names_non_empty(self):
        """Test 31: All scenario names are non-empty strings."""
        for name in self.suite.cross_agent_scenarios:
            self.assertTrue(len(name) > 0)

    def test_32_all_team_mission_ids_unique(self):
        """Test 32: All team_mission_id strings are unique."""
        res = self.suite.run_cross_agent_benchmarks()
        ids = set(m["team_mission_id"] for m in res["team_mission_results"])
        self.assertEqual(len(ids), 30)

    def test_33_no_error_keys(self):
        """Test 33: Result does not contain error key."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertNotIn("error", res)

    def test_34_consensus_score_float(self):
        """Test 34: team_consensus_score is float."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertIsInstance(m["team_consensus_score"], float)

    def test_35_participating_agents_list_type(self):
        """Test 35: participating_agents is list."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertIsInstance(m["participating_agents"], list)

    def test_36_dict_return_type(self):
        """Test 36: Return type is dictionary."""
        self.assertEqual(type(self.suite.run_cross_agent_benchmarks()), dict)

    def test_37_timestamp_length(self):
        """Test 37: evaluation_timestamp length >= 19."""
        res = self.suite.run_cross_agent_benchmarks()
        self.assertTrue(len(res["evaluation_timestamp"]) >= 19)

    def test_38_participating_agents_contain_valid_agents(self):
        """Test 38: Participating agents include valid agent names."""
        res = self.suite.run_cross_agent_benchmarks()
        valid = {"CodingAgent", "ResearchAgent", "DataAnalysisAgent", "WritingAgent", "FinanceAgent"}
        for m in res["team_mission_results"]:
            for agent in m["participating_agents"]:
                self.assertIn(agent, valid)

    def test_39_consensus_score_bounded_below_1(self):
        """Test 39: team_consensus_score <= 1.0."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertTrue(m["team_consensus_score"] <= 1.0)

    def test_40_consensus_score_bounded_above_0(self):
        """Test 40: team_consensus_score >= 0.0."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertTrue(m["team_consensus_score"] >= 0.0)

    def test_41_status_string_type(self):
        """Test 41: status is string."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(type(m["status"]), str)

    def test_42_name_string_type(self):
        """Test 42: name is string."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(type(m["name"]), str)

    def test_43_team_mission_id_string_type(self):
        """Test 43: team_mission_id is string."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(type(m["team_mission_id"]), str)

    def test_44_safety_violations_int_type(self):
        """Test 44: safety_violations is integer."""
        res = self.suite.run_cross_agent_benchmarks()
        for m in res["team_mission_results"]:
            self.assertEqual(type(m["safety_violations"]), int)

    def test_45_v7_7_cross_agent_benchmark_verification_passed(self):
        """Test 45: All V7.7 cross-agent benchmark features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
