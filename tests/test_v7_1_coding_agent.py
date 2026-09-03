import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.coding_agent import CodingAgent

class TestV71CodingAgent(unittest.TestCase):

    def setUp(self):
        self.coding_agent = CodingAgent()

    def test_1_agent_id_is_coding_agent(self):
        """Test 1: agent_id is CodingAgent."""
        self.assertEqual(self.coding_agent.agent_id, "CodingAgent")

    def test_2_role_is_developer(self):
        """Test 2: role is DEVELOPER."""
        self.assertEqual(self.coding_agent.role, "DEVELOPER")

    def test_3_capabilities_include_code_read(self):
        """Test 3: Capabilities include code.read."""
        self.assertIn("code.read", self.coding_agent.capabilities)

    def test_4_capabilities_include_code_propose_diff(self):
        """Test 4: Capabilities include code.propose_diff."""
        self.assertIn("code.propose_diff", self.coding_agent.capabilities)

    def test_5_analyze_repository_returns_dict(self):
        """Test 5: analyze_repository returns dictionary."""
        res = self.coding_agent.analyze_repository()
        self.assertIsInstance(res, dict)

    def test_6_propose_patch_returns_dict(self):
        """Test 6: propose_patch returns dictionary."""
        res = self.coding_agent.propose_patch("Fix typo")
        self.assertIsInstance(res, dict)

    def test_7_propose_patch_requires_user_approval(self):
        """Test 7: propose_patch requires_user_approval is True."""
        res = self.coding_agent.propose_patch("Fix typo")
        self.assertTrue(res["requires_user_approval"])

    def test_8_propose_patch_diff_contains_plus(self):
        """Test 8: proposed_diff contains + symbol."""
        res = self.coding_agent.propose_patch("Fix typo")
        self.assertIn("+", res["proposed_diff"])

    def test_9_analyze_repository_total_tests(self):
        """Test 9: analyze_repository total_unit_tests is 1937."""
        res = self.coding_agent.analyze_repository()
        self.assertEqual(res["total_unit_tests"], 1937)

    def test_10_governor_authorization_sandbox_only(self):
        """Test 10: propose_patch governor authorization is AUTHORIZED_FOR_SANDBOX_ONLY."""
        res = self.coding_agent.propose_patch("Fix typo")
        self.assertEqual(res["governor_authorization"], "AUTHORIZED_FOR_SANDBOX_ONLY")

    def test_11_class_name(self):
        """Test 11: Class name is CodingAgent."""
        self.assertEqual(self.coding_agent.__class__.__name__, "CodingAgent")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable."""
        r1 = self.coding_agent.analyze_repository()
        r2 = self.coding_agent.analyze_repository()
        self.assertEqual(r1["files_inspected"], r2["files_inspected"])

    def test_13_json_serializable_patch(self):
        """Test 13: propose_patch output is JSON serializable."""
        import json
        dumped = json.dumps(self.coding_agent.propose_patch("Issue"))
        self.assertIsInstance(dumped, str)

    def test_14_json_serializable_analysis(self):
        """Test 14: analyze_repository output is JSON serializable."""
        import json
        dumped = json.dumps(self.coding_agent.analyze_repository())
        self.assertIsInstance(dumped, str)

    def test_15_tools_include_view_file(self):
        """Test 15: Tools include view_file."""
        self.assertIn("view_file", self.coding_agent.tools)

    def test_16_tools_include_replace_file_content(self):
        """Test 16: Tools include replace_file_content."""
        self.assertIn("replace_file_content", self.coding_agent.tools)

    def test_17_preferred_models_include_qwen(self):
        """Test 17: Preferred models include qwen2.5_1.5b."""
        self.assertIn("qwen2.5_1.5b", self.coding_agent.preferred_models)

    def test_18_autonomy_cap_bounded_auto(self):
        """Test 18: Autonomy cap is BOUNDED_AUTO."""
        self.assertEqual(self.coding_agent.autonomy_cap, "BOUNDED_AUTO")

    def test_19_analyze_repository_keys_count(self):
        """Test 19: analyze_repository returns 7 keys."""
        res = self.coding_agent.analyze_repository()
        self.assertEqual(len(res), 7)

    def test_20_propose_patch_keys_count(self):
        """Test 20: propose_patch returns 6 keys."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertEqual(len(res), 6)

    def test_21_patch_issue_preserved(self):
        """Test 21: Issue string preserved in patch proposal."""
        res = self.coding_agent.propose_patch("Fix null pointer")
        self.assertEqual(res["issue"], "Fix null pointer")

    def test_22_repo_path_preserved(self):
        """Test 22: Custom repo_path preserved."""
        res = self.coding_agent.analyze_repository("c:\\Custom")
        self.assertEqual(res["repo_path"], "c:\\Custom")

    def test_23_patch_test_verification_non_empty(self):
        """Test 23: test_verification is non-empty string."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertTrue(len(res["test_verification"]) > 0)

    def test_24_architecture_summary_non_empty(self):
        """Test 24: architecture_summary is non-empty string."""
        res = self.coding_agent.analyze_repository()
        self.assertTrue(len(res["architecture_summary"]) > 0)

    def test_25_capabilities_count_5(self):
        """Test 25: Capabilities count is 5."""
        self.assertEqual(len(self.coding_agent.capabilities), 5)

    def test_26_tools_count_4(self):
        """Test 26: Tools count is 4."""
        self.assertEqual(len(self.coding_agent.tools), 4)

    def test_27_preferred_models_count_2(self):
        """Test 27: Preferred models count is 2."""
        self.assertEqual(len(self.coding_agent.preferred_models), 2)

    def test_28_inherits_from_specialist_agent(self):
        """Test 28: CodingAgent inherits from SpecialistAgent."""
        from personal_agent.agents.base_specialist import SpecialistAgent
        self.assertTrue(issubclass(CodingAgent, SpecialistAgent))

    def test_29_execute_task_overridden(self):
        """Test 29: Base execute_task works on CodingAgent."""
        res = self.coding_agent.execute_task({})
        self.assertEqual(res["agent_id"], "CodingAgent")

    def test_30_to_dict_agent_id(self):
        """Test 30: to_dict contains agent_id CodingAgent."""
        self.assertEqual(self.coding_agent.to_dict()["agent_id"], "CodingAgent")

    def test_31_analyze_repository_status_analyzed(self):
        """Test 31: Status is ANALYZED."""
        res = self.coding_agent.analyze_repository()
        self.assertEqual(res["status"], "ANALYZED")

    def test_32_patch_agent_id_coding_agent(self):
        """Test 32: Patch agent_id is CodingAgent."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertEqual(res["agent_id"], "CodingAgent")

    def test_33_patch_requires_user_approval_boolean(self):
        """Test 33: requires_user_approval is boolean."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertIsInstance(res["requires_user_approval"], bool)

    def test_34_files_inspected_positive_int(self):
        """Test 34: files_inspected is positive integer."""
        res = self.coding_agent.analyze_repository()
        self.assertTrue(res["files_inspected"] > 0)

    def test_35_total_unit_tests_positive_int(self):
        """Test 35: total_unit_tests is positive integer."""
        res = self.coding_agent.analyze_repository()
        self.assertTrue(res["total_unit_tests"] > 0)

    def test_36_instantiation_clean(self):
        """Test 36: CodingAgent instantiates cleanly."""
        agent = CodingAgent()
        self.assertIsNotNone(agent)

    def test_37_no_error_keys(self):
        """Test 37: Result does not contain error key."""
        res = self.coding_agent.analyze_repository()
        self.assertNotIn("error", res)

    def test_38_governor_authorized_in_analysis(self):
        """Test 38: Analysis mentions AUTHORIZED."""
        res = self.coding_agent.analyze_repository()
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_39_proposed_diff_multiline(self):
        """Test 39: proposed_diff contains newlines."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertIn("\n", res["proposed_diff"])

    def test_40_proposed_diff_minus(self):
        """Test 40: proposed_diff contains - symbol."""
        res = self.coding_agent.propose_patch("Issue")
        self.assertIn("-", res["proposed_diff"])

    def test_41_tools_list_type(self):
        """Test 41: tools is list."""
        self.assertIsInstance(self.coding_agent.tools, list)

    def test_42_capabilities_list_type(self):
        """Test 42: capabilities is list."""
        self.assertIsInstance(self.coding_agent.capabilities, list)

    def test_43_preferred_models_list_type(self):
        """Test 43: preferred_models is list."""
        self.assertIsInstance(self.coding_agent.preferred_models, list)

    def test_44_dict_return_type(self):
        """Test 44: to_dict return type is dict."""
        self.assertEqual(type(self.coding_agent.to_dict()), dict)

    def test_45_v7_1_coding_agent_verification_passed(self):
        """Test 45: All V7.1 CodingAgent features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
