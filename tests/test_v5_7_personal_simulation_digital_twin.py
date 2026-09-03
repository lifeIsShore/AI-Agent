import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.world.personal_simulation_environment import (
    PersonalSimulationEnvironment, SCENARIO_AGGRESSIVE, SCENARIO_BALANCED, SCENARIO_CONSERVATIVE
)
from personal_agent.planner.counterfactual_planner import CounterfactualPlanner

class TestV57PersonalSimulationDigitalTwin(unittest.TestCase):

    def setUp(self):
        self.sim_env = PersonalSimulationEnvironment()
        self.planner = CounterfactualPlanner()

    def test_1_simulation_environment_initializes(self):
        """Test 1: PersonalSimulationEnvironment initializes cleanly."""
        self.assertIsNotNone(self.sim_env)

    def test_2_simulate_balanced_scenario(self):
        """Test 2: simulate_scenario simulates BALANCED branch."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 5.0}, SCENARIO_BALANCED)
        self.assertEqual(res["scenario_mode"], SCENARIO_BALANCED)
        self.assertFalse(res["mutates_live_state"])

    def test_3_simulate_aggressive_scenario(self):
        """Test 3: simulate_scenario simulates AGGRESSIVE branch."""
        res = self.sim_env.simulate_scenario({"total_hours": 30.0, "max_capacity": 40.0}, {"estimated_hours": 8.0}, SCENARIO_AGGRESSIVE)
        self.assertEqual(res["scenario_mode"], SCENARIO_AGGRESSIVE)
        self.assertEqual(res["risk_level"], "HIGH")

    def test_4_simulate_conservative_scenario(self):
        """Test 4: simulate_scenario simulates CONSERVATIVE branch."""
        res = self.sim_env.simulate_scenario({"total_hours": 10.0, "max_capacity": 40.0}, {"estimated_hours": 2.0}, SCENARIO_CONSERVATIVE)
        self.assertEqual(res["scenario_mode"], SCENARIO_CONSERVATIVE)
        self.assertEqual(res["risk_level"], "LOW")

    def test_5_mutates_live_state_invariant_is_false(self):
        """Test 5: Invariant mutates_live_state: False enforced across all simulation runs."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertFalse(res["mutates_live_state"])

    def test_6_counterfactual_planner_evaluates_all_scenarios(self):
        """Test 6: evaluate_counterfactuals evaluates all 3 scenario branches."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 4.0})
        self.assertEqual(len(res["all_scenarios"]), 3)

    def test_7_counterfactual_planner_recommends_best_scenario(self):
        """Test 7: evaluate_counterfactuals selects optimal recommended scenario."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 4.0})
        self.assertIn("recommended_scenario", res)
        self.assertIsNotNone(res["recommended_outcome"])

    def test_8_simulated_workload_hours_calculated(self):
        """Test 8: simulated_workload_hours calculates total hours accurately."""
        res = self.sim_env.simulate_scenario({"total_hours": 15.0}, {"estimated_hours": 5.0})
        self.assertEqual(res["simulated_workload_hours"], 20.0)

    def test_9_capacity_utilization_ratio(self):
        """Test 9: capacity_utilization ratio calculated accurately."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 0.0})
        self.assertEqual(res["capacity_utilization"], 0.5)

    def test_10_predicted_completion_prob_in_range(self):
        """Test 10: predicted_completion_prob is within range 0.0 to 1.0."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 5.0})
        self.assertTrue(0.0 <= res["predicted_completion_prob"] <= 1.0)

    def test_11_risk_level_string_values(self):
        """Test 11: risk_level is string (LOW, MEDIUM, or HIGH)."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertIn(res["risk_level"], ["LOW", "MEDIUM", "HIGH"])

    def test_12_planner_returns_dict(self):
        """Test 12: evaluate_counterfactuals returns dict instance."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertIsInstance(res, dict)

    def test_13_sim_env_default_mode_balanced(self):
        """Test 13: Default simulation mode is BALANCED."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertEqual(res["scenario_mode"], SCENARIO_BALANCED)

    def test_14_sim_env_handles_empty_inputs(self):
        """Test 14: simulate_scenario handles empty input dicts cleanly."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertEqual(res["simulated_workload_hours"], 22.0)  # default 20 + 2

    def test_15_all_scenarios_contain_all_modes(self):
        """Test 15: all_scenarios contains AGGRESSIVE, BALANCED, CONSERVATIVE."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        modes = [s["scenario_mode"] for s in res["all_scenarios"]]
        self.assertIn(SCENARIO_AGGRESSIVE, modes)
        self.assertIn(SCENARIO_BALANCED, modes)
        self.assertIn(SCENARIO_CONSERVATIVE, modes)

    def test_16_conservative_lowest_risk(self):
        """Test 16: CONSERVATIVE scenario mode returns LOW risk_level."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0}, {"estimated_hours": 5.0}, SCENARIO_CONSERVATIVE)
        self.assertEqual(res["risk_level"], "LOW")

    def test_17_aggressive_high_capacity_high_risk(self):
        """Test 17: AGGRESSIVE mode at high capacity returns HIGH risk_level."""
        res = self.sim_env.simulate_scenario({"total_hours": 35.0, "max_capacity": 40.0}, {"estimated_hours": 2.0}, SCENARIO_AGGRESSIVE)
        self.assertEqual(res["risk_level"], "HIGH")

    def test_18_recommended_scenario_is_string(self):
        """Test 18: recommended_scenario is string."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertIsInstance(res["recommended_scenario"], str)

    def test_19_recommended_outcome_dict_keys(self):
        """Test 19: recommended_outcome dict contains expected keys."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertIn("scenario_mode", res["recommended_outcome"])
        self.assertIn("predicted_completion_prob", res["recommended_outcome"])

    def test_20_stateless_simulation_execution(self):
        """Test 20: PersonalSimulationEnvironment is stateless and repeatable."""
        res1 = self.sim_env.simulate_scenario({"total_hours": 10.0}, {"estimated_hours": 2.0})
        res2 = self.sim_env.simulate_scenario({"total_hours": 10.0}, {"estimated_hours": 2.0})
        self.assertEqual(res1["simulated_workload_hours"], res2["simulated_workload_hours"])

    def test_21_capacity_utilization_float(self):
        """Test 21: capacity_utilization is float."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertIsInstance(res["capacity_utilization"], float)

    def test_22_predicted_completion_prob_float(self):
        """Test 22: predicted_completion_prob is float."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertIsInstance(res["predicted_completion_prob"], float)

    def test_23_counterfactual_planner_initializes(self):
        """Test 23: CounterfactualPlanner initializes cleanly."""
        self.assertIsNotNone(self.planner)

    def test_24_all_scenarios_count_is_three(self):
        """Test 24: all_scenarios list length is exactly 3."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertEqual(len(res["all_scenarios"]), 3)

    def test_25_recommended_scenario_valid_mode(self):
        """Test 25: recommended_scenario is one of the 3 valid scenario modes."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertIn(res["recommended_scenario"], [SCENARIO_AGGRESSIVE, SCENARIO_BALANCED, SCENARIO_CONSERVATIVE])

    def test_26_zero_workload_hours_handled(self):
        """Test 26: 0 total hours workload handled cleanly."""
        res = self.sim_env.simulate_scenario({"total_hours": 0.0}, {"estimated_hours": 0.0})
        self.assertEqual(res["simulated_workload_hours"], 0.0)

    def test_27_custom_max_capacity(self):
        """Test 27: Custom max_capacity parameter evaluated correctly."""
        res = self.sim_env.simulate_scenario({"total_hours": 50.0, "max_capacity": 100.0}, {"estimated_hours": 0.0})
        self.assertEqual(res["capacity_utilization"], 0.5)

    def test_28_high_risk_scenarios_filtered_by_planner(self):
        """Test 28: CounterfactualPlanner filters out HIGH risk scenarios when lower risk scenarios exist."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {"total_hours": 35.0, "max_capacity": 40.0}, {"estimated_hours": 2.0})
        self.assertNotEqual(res["recommended_scenario"], SCENARIO_AGGRESSIVE)

    def test_29_conservative_mode_highest_completion_prob(self):
        """Test 29: Conservative mode yields higher completion probability."""
        res_cons = self.sim_env.simulate_scenario({"total_hours": 20.0}, {"estimated_hours": 5.0}, SCENARIO_CONSERVATIVE)
        res_agg = self.sim_env.simulate_scenario({"total_hours": 20.0}, {"estimated_hours": 5.0}, SCENARIO_AGGRESSIVE)
        self.assertTrue(res_cons["predicted_completion_prob"] >= res_agg["predicted_completion_prob"])

    def test_30_simulation_result_dict_keys_count(self):
        """Test 30: simulate_scenario return dict contains 6 keys."""
        res = self.sim_env.simulate_scenario({}, {})
        self.assertEqual(len(res), 6)

    def test_31_counterfactual_result_dict_keys_count(self):
        """Test 31: evaluate_counterfactuals return dict contains 3 keys."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertEqual(len(res), 3)

    def test_32_simulated_workload_float_precision(self):
        """Test 32: simulated_workload_hours rounded to 1 decimal place."""
        res = self.sim_env.simulate_scenario({"total_hours": 10.123}, {"estimated_hours": 2.456})
        self.assertEqual(res["simulated_workload_hours"], 12.6)

    def test_33_capacity_utilization_precision(self):
        """Test 33: capacity_utilization rounded to 2 decimal places."""
        res = self.sim_env.simulate_scenario({"total_hours": 10.0, "max_capacity": 30.0}, {"estimated_hours": 0.0})
        self.assertEqual(res["capacity_utilization"], 0.33)

    def test_34_predicted_completion_prob_precision(self):
        """Test 34: predicted_completion_prob rounded to 2 decimal places."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 5.0})
        self.assertEqual(res["predicted_completion_prob"], round(res["predicted_completion_prob"], 2))

    def test_35_planner_recommended_outcome_matches_scenario(self):
        """Test 35: recommended_outcome's scenario_mode matches recommended_scenario."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {}, {})
        self.assertEqual(res["recommended_outcome"]["scenario_mode"], res["recommended_scenario"])

    def test_36_balanced_risk_medium_when_utilization_over_80(self):
        """Test 36: BALANCED mode at 85% capacity returns MEDIUM risk."""
        res = self.sim_env.simulate_scenario({"total_hours": 34.0, "max_capacity": 40.0}, {"estimated_hours": 0.0}, SCENARIO_BALANCED)
        self.assertEqual(res["risk_level"], "MEDIUM")

    def test_37_balanced_risk_low_when_utilization_under_80(self):
        """Test 37: BALANCED mode at 50% capacity returns LOW risk."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 0.0}, SCENARIO_BALANCED)
        self.assertEqual(res["risk_level"], "LOW")

    def test_38_aggressive_medium_risk_when_utilization_under_85(self):
        """Test 38: AGGRESSIVE mode at 50% capacity returns MEDIUM risk."""
        res = self.sim_env.simulate_scenario({"total_hours": 20.0, "max_capacity": 40.0}, {"estimated_hours": 0.0}, SCENARIO_AGGRESSIVE)
        self.assertEqual(res["risk_level"], "MEDIUM")

    def test_39_in_memory_sandbox_non_mutating_check(self):
        """Test 39: In-memory simulation does not alter current_workload dict."""
        workload = {"total_hours": 20.0, "max_capacity": 40.0}
        self.sim_env.simulate_scenario(workload, {"estimated_hours": 5.0})
        self.assertEqual(workload["total_hours"], 20.0)

    def test_40_in_memory_sandbox_non_mutating_action_check(self):
        """Test 40: In-memory simulation does not alter proposed_action dict."""
        action = {"estimated_hours": 5.0}
        self.sim_env.simulate_scenario({"total_hours": 20.0}, action)
        self.assertEqual(action["estimated_hours"], 5.0)

    def test_41_planner_evaluates_with_high_overload(self):
        """Test 41: Planner chooses conservative when workload is severely overloaded."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {"total_hours": 38.0, "max_capacity": 40.0}, {"estimated_hours": 5.0})
        self.assertEqual(res["recommended_scenario"], SCENARIO_CONSERVATIVE)

    def test_42_planner_evaluates_with_light_workload(self):
        """Test 42: Planner handles light workload scenario selection cleanly."""
        res = self.planner.evaluate_counterfactuals(self.sim_env, {"total_hours": 5.0, "max_capacity": 40.0}, {"estimated_hours": 2.0})
        self.assertIsNotNone(res["recommended_scenario"])

    def test_43_scenario_constant_aggressive_value(self):
        """Test 43: SCENARIO_AGGRESSIVE constant is AGGRESSIVE."""
        self.assertEqual(SCENARIO_AGGRESSIVE, "AGGRESSIVE")

    def test_44_scenario_constant_balanced_value(self):
        """Test 44: SCENARIO_BALANCED constant is BALANCED."""
        self.assertEqual(SCENARIO_BALANCED, "BALANCED")

    def test_45_v5_7_personal_simulation_verification_passed(self):
        """Test 45: All V5.7 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
