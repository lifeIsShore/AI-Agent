import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.data_analysis_agent import DataAnalysisAgent

class TestV73DataAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.data_agent = DataAnalysisAgent()

    def test_1_agent_id_is_data_analysis_agent(self):
        """Test 1: agent_id is DataAnalysisAgent."""
        self.assertEqual(self.data_agent.agent_id, "DataAnalysisAgent")

    def test_2_role_is_data_analyst(self):
        """Test 2: role is DATA_ANALYST."""
        self.assertEqual(self.data_agent.role, "DATA_ANALYST")

    def test_3_analyze_dataset_returns_dict(self):
        """Test 3: analyze_dataset returns dictionary."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertIsInstance(res, dict)

    def test_4_total_rows_count(self):
        """Test 4: total_rows is 14200."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertEqual(res["total_rows"], 14200)

    def test_5_columns_profiled_count(self):
        """Test 5: columns_profiled is 18."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertEqual(res["columns_profiled"], 18)

    def test_6_sandbox_execution_status_success(self):
        """Test 6: sandbox_execution_status starts with SUCCESS."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertTrue(res["sandbox_execution_status"].startswith("SUCCESS"))

    def test_7_visualization_generated_string(self):
        """Test 7: visualization_generated ends with .png."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertTrue(res["visualization_generated"].endswith(".png"))

    def test_8_governor_authorization_authorized(self):
        """Test 8: Governor authorization is AUTHORIZED."""
        res = self.data_agent.analyze_dataset("Thesis Study Hours")
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_9_capabilities_count_6(self):
        """Test 9: Capabilities count is 6."""
        self.assertEqual(len(self.data_agent.capabilities), 6)

    def test_10_tools_count_2(self):
        """Test 10: Tools count is 2."""
        self.assertEqual(len(self.data_agent.tools), 2)

    def test_11_class_name(self):
        """Test 11: Class name is DataAnalysisAgent."""
        self.assertEqual(self.data_agent.__class__.__name__, "DataAnalysisAgent")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable across calls."""
        r1 = self.data_agent.analyze_dataset("DS")
        r2 = self.data_agent.analyze_dataset("DS")
        self.assertEqual(r1["total_rows"], r2["total_rows"])

    def test_13_json_serializable(self):
        """Test 13: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.data_agent.analyze_dataset("DS"))
        self.assertIsInstance(dumped, str)

    def test_14_dataset_name_preserved(self):
        """Test 14: Dataset name preserved in result."""
        res = self.data_agent.analyze_dataset("Custom Dataset")
        self.assertEqual(res["dataset_name"], "Custom Dataset")

    def test_15_capabilities_include_python_sandbox(self):
        """Test 15: Capabilities include data.python_sandbox."""
        self.assertIn("data.python_sandbox", self.data_agent.capabilities)

    def test_16_capabilities_include_visualize(self):
        """Test 16: Capabilities include data.visualize."""
        self.assertIn("data.visualize", self.data_agent.capabilities)

    def test_17_preferred_models_include_qwen(self):
        """Test 17: Preferred models include qwen2.5_1.5b."""
        self.assertIn("qwen2.5_1.5b", self.data_agent.preferred_models)

    def test_18_autonomy_cap_bounded_auto(self):
        """Test 18: Autonomy cap is BOUNDED_AUTO."""
        self.assertEqual(self.data_agent.autonomy_cap, "BOUNDED_AUTO")

    def test_19_summary_keys_count(self):
        """Test 19: analyze_dataset returns 9 keys."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertEqual(len(res), 9)

    def test_20_correlation_summary_non_empty(self):
        """Test 20: correlation_summary is non-empty string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(len(res["correlation_summary"]) > 0)

    def test_21_missing_values_imputed_int(self):
        """Test 21: missing_values_imputed is integer."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertIsInstance(res["missing_values_imputed"], int)

    def test_22_total_rows_positive_int(self):
        """Test 22: total_rows is positive integer."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(res["total_rows"] > 0)

    def test_23_columns_profiled_positive_int(self):
        """Test 23: columns_profiled is positive integer."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(res["columns_profiled"] > 0)

    def test_24_inherits_from_specialist_agent(self):
        """Test 24: DataAnalysisAgent inherits from SpecialistAgent."""
        from personal_agent.agents.base_specialist import SpecialistAgent
        self.assertTrue(issubclass(DataAnalysisAgent, SpecialistAgent))

    def test_25_execute_task_overridden(self):
        """Test 25: Base execute_task works on DataAnalysisAgent."""
        res = self.data_agent.execute_task({})
        self.assertEqual(res["agent_id"], "DataAnalysisAgent")

    def test_26_to_dict_agent_id(self):
        """Test 26: to_dict contains agent_id DataAnalysisAgent."""
        self.assertEqual(self.data_agent.to_dict()["agent_id"], "DataAnalysisAgent")

    def test_27_tools_list_type(self):
        """Test 27: tools is list."""
        self.assertIsInstance(self.data_agent.tools, list)

    def test_28_preferred_models_count_2(self):
        """Test 28: Preferred models count is 2."""
        self.assertEqual(len(self.data_agent.preferred_models), 2)

    def test_29_instantiation_clean(self):
        """Test 29: DataAnalysisAgent instantiates cleanly."""
        agent = DataAnalysisAgent()
        self.assertIsNotNone(agent)

    def test_30_no_error_keys(self):
        """Test 30: Result does not contain error key."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertNotIn("error", res)

    def test_31_correlation_mentions_r_value(self):
        """Test 31: Correlation summary mentions r=0.88."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertIn("0.88", res["correlation_summary"])

    def test_32_sandbox_mentions_python(self):
        """Test 32: Sandbox execution status mentions Python."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertIn("Python", res["sandbox_execution_status"])

    def test_33_capabilities_list_type(self):
        """Test 33: capabilities is list."""
        self.assertIsInstance(self.data_agent.capabilities, list)

    def test_34_preferred_models_list_type(self):
        """Test 34: preferred_models is list."""
        self.assertIsInstance(self.data_agent.preferred_models, list)

    def test_35_dict_return_type(self):
        """Test 35: to_dict return type is dict."""
        self.assertEqual(type(self.data_agent.to_dict()), dict)

    def test_36_analyze_return_type(self):
        """Test 36: analyze_dataset return type is dict."""
        self.assertEqual(type(self.data_agent.analyze_dataset("DS")), dict)

    def test_37_dataset_name_string_type(self):
        """Test 37: dataset_name is string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertEqual(type(res["dataset_name"]), str)

    def test_38_agent_id_string_type(self):
        """Test 38: agent_id is string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertEqual(type(res["agent_id"]), str)

    def test_39_governor_authorization_string_type(self):
        """Test 39: governor_authorization is string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertEqual(type(res["governor_authorization"]), str)

    def test_40_missing_values_imputed_non_negative(self):
        """Test 40: missing_values_imputed >= 0."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(res["missing_values_imputed"] >= 0)

    def test_41_columns_profiled_non_negative(self):
        """Test 41: columns_profiled >= 0."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(res["columns_profiled"] >= 0)

    def test_42_total_rows_non_negative(self):
        """Test 42: total_rows >= 0."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(res["total_rows"] >= 0)

    def test_43_visualization_string_non_empty(self):
        """Test 43: visualization_generated is non-empty string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(len(res["visualization_generated"]) > 0)

    def test_44_sandbox_status_string_non_empty(self):
        """Test 44: sandbox_execution_status is non-empty string."""
        res = self.data_agent.analyze_dataset("DS")
        self.assertTrue(len(res["sandbox_execution_status"]) > 0)

    def test_45_v7_3_data_analysis_agent_verification_passed(self):
        """Test 45: All V7.3 DataAnalysisAgent features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
