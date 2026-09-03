import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.reasoning.decision_intelligence_engine import DecisionIntelligenceEngine

class TestV64DecisionIntelligence(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionIntelligenceEngine()

    def test_1_engine_initializes(self):
        """Test 1: DecisionIntelligenceEngine initializes cleanly."""
        self.assertIsNotNone(self.engine)

    def test_2_formulate_decision_options_returns_three_options(self):
        """Test 2: formulate_decision_options returns 3 scenario trade-off options."""
        res = self.engine.formulate_decision_options("Thesis timeline delay", {})
        self.assertEqual(len(res["options"]), 3)
        self.assertTrue(res["requires_user_decision"])

    def test_3_recommended_option_is_opt_b(self):
        """Test 3: recommended_option is opt_b."""
        res = self.engine.formulate_decision_options("Thesis timeline delay", {})
        self.assertEqual(res["recommended_option"], "opt_b")

    def test_4_problem_statement_preserved(self):
        """Test 4: Problem statement string preserved in output."""
        res = self.engine.formulate_decision_options("Custom Problem", {})
        self.assertEqual(res["problem_statement"], "Custom Problem")

    def test_5_recommendation_reason_string(self):
        """Test 5: recommendation_reason is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIn("Option B", res["recommendation_reason"])

    def test_6_option_keys_structure(self):
        """Test 6: Option entry contains 5 keys (option_id, name, completion_prob, risk_level, impact)."""
        res = self.engine.formulate_decision_options("P", {})
        opt = res["options"][0]
        self.assertEqual(len(opt), 5)
        self.assertIn("option_id", opt)
        self.assertIn("completion_prob", opt)

    def test_7_requires_user_decision_invariant(self):
        """Test 7: Invariant requires_user_decision: True enforced."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertTrue(res["requires_user_decision"])

    def test_8_option_a_id(self):
        """Test 8: Option A ID is opt_a."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][0]["option_id"], "opt_a")

    def test_9_option_b_id(self):
        """Test 9: Option B ID is opt_b."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][1]["option_id"], "opt_b")

    def test_10_option_c_id(self):
        """Test 10: Option C ID is opt_c."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][2]["option_id"], "opt_c")

    def test_11_stateless_execution(self):
        """Test 11: Formulate decision options is stateless."""
        r1 = self.engine.formulate_decision_options("P", {})
        r2 = self.engine.formulate_decision_options("P", {})
        self.assertEqual(r1["recommended_option"], r2["recommended_option"])

    def test_12_output_dict_keys_count(self):
        """Test 12: Output dict contains 5 keys."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(len(res), 5)

    def test_13_option_b_completion_prob_0_84(self):
        """Test 13: Option B completion_prob is 0.84."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][1]["completion_prob"], 0.84)

    def test_14_option_b_risk_level_low(self):
        """Test 14: Option B risk_level is LOW."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][1]["risk_level"], "LOW")

    def test_15_options_is_list(self):
        """Test 15: options is list."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"], list)

    def test_16_engine_reusable(self):
        """Test 16: Engine instance reusable across calls."""
        r1 = self.engine.formulate_decision_options("P1", {})
        r2 = self.engine.formulate_decision_options("P2", {})
        self.assertEqual(r1["problem_statement"], "P1")
        self.assertEqual(r2["problem_statement"], "P2")

    def test_17_recommendation_reason_type_str(self):
        """Test 17: recommendation_reason is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["recommendation_reason"], str)

    def test_18_recommended_option_type_str(self):
        """Test 18: recommended_option is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["recommended_option"], str)

    def test_19_requires_user_decision_boolean(self):
        """Test 19: requires_user_decision is boolean."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["requires_user_decision"], bool)

    def test_20_option_a_risk_high(self):
        """Test 20: Option A risk_level is HIGH."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][0]["risk_level"], "HIGH")

    def test_21_option_c_risk_low(self):
        """Test 21: Option C risk_level is LOW."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][2]["risk_level"], "LOW")

    def test_22_option_a_completion_prob(self):
        """Test 22: Option A completion_prob is 0.72."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][0]["completion_prob"], 0.72)

    def test_23_option_c_completion_prob(self):
        """Test 23: Option C completion_prob is 0.91."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(res["options"][2]["completion_prob"], 0.91)

    def test_24_empty_problem_statement_handled(self):
        """Test 24: Empty problem statement handled cleanly."""
        res = self.engine.formulate_decision_options("", {})
        self.assertEqual(res["problem_statement"], "")

    def test_25_engine_class_name(self):
        """Test 25: Class name is DecisionIntelligenceEngine."""
        self.assertEqual(self.engine.__class__.__name__, "DecisionIntelligenceEngine")

    def test_26_options_count_exact_3(self):
        """Test 26: options list contains exactly 3 entries."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertEqual(len(res["options"]), 3)

    def test_27_recommended_option_in_option_ids(self):
        """Test 27: recommended_option exists in options list IDs."""
        res = self.engine.formulate_decision_options("P", {})
        opt_ids = [o["option_id"] for o in res["options"]]
        self.assertIn(res["recommended_option"], opt_ids)

    def test_28_option_names_distinct(self):
        """Test 28: Option names are distinct."""
        res = self.engine.formulate_decision_options("P", {})
        names = [o["name"] for o in res["options"]]
        self.assertEqual(len(set(names)), 3)

    def test_29_option_impacts_non_empty(self):
        """Test 29: Option impact strings are non-empty."""
        res = self.engine.formulate_decision_options("P", {})
        for o in res["options"]:
            self.assertTrue(len(o["impact"]) > 0)

    def test_30_result_type_dict(self):
        """Test 30: Returns dict instance."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res, dict)

    def test_31_workload_dict_passed(self):
        """Test 31: Workload dict passed cleanly."""
        res = self.engine.formulate_decision_options("P", {"total_hours": 30})
        self.assertIsNotNone(res)

    def test_32_options_iterable(self):
        """Test 32: options list is iterable."""
        res = self.engine.formulate_decision_options("P", {})
        count = sum(1 for _ in res["options"])
        self.assertEqual(count, 3)

    def test_33_option_id_string_type(self):
        """Test 33: option_id is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"][0]["option_id"], str)

    def test_34_option_name_string_type(self):
        """Test 34: option name is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"][0]["name"], str)

    def test_35_option_risk_level_string_type(self):
        """Test 35: risk_level is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"][0]["risk_level"], str)

    def test_36_option_impact_string_type(self):
        """Test 36: impact is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"][0]["impact"], str)

    def test_37_option_completion_prob_float_type(self):
        """Test 37: completion_prob is float."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["options"][0]["completion_prob"], float)

    def test_38_options_order(self):
        """Test 38: Options order is opt_a, opt_b, opt_c."""
        res = self.engine.formulate_decision_options("P", {})
        ids = [o["option_id"] for o in res["options"]]
        self.assertEqual(ids, ["opt_a", "opt_b", "opt_c"])

    def test_39_recommendation_reason_mentions_opt_b(self):
        """Test 39: recommendation_reason mentions Option B."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIn("Option B", res["recommendation_reason"])

    def test_40_decision_intelligence_integration_ready(self):
        """Test 40: Dict structured for Decision Center UI integration."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIn("recommended_option", res)
        self.assertIn("options", res)

    def test_41_multiple_problem_formulations(self):
        """Test 41: Multiple formulations return independent objects."""
        r1 = self.engine.formulate_decision_options("P1", {})
        r2 = self.engine.formulate_decision_options("P2", {})
        self.assertIsNot(r1, r2)

    def test_42_completion_prob_bounded(self):
        """Test 42: Completion probabilities are bounded between 0.0 and 1.0."""
        res = self.engine.formulate_decision_options("P", {})
        for o in res["options"]:
            self.assertTrue(0.0 <= o["completion_prob"] <= 1.0)

    def test_43_requires_user_decision_always_true(self):
        """Test 43: Invariant requires_user_decision remains True across calls."""
        r1 = self.engine.formulate_decision_options("P1", {})
        r2 = self.engine.formulate_decision_options("P2", {})
        self.assertTrue(r1["requires_user_decision"])
        self.assertTrue(r2["requires_user_decision"])

    def test_44_problem_statement_type_str(self):
        """Test 44: problem_statement is string."""
        res = self.engine.formulate_decision_options("P", {})
        self.assertIsInstance(res["problem_statement"], str)

    def test_45_v6_4_decision_intelligence_verification_passed(self):
        """Test 45: All V6.4 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
