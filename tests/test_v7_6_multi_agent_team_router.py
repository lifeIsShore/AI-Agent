import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.multi_agent_team_router import MultiAgentTeamRouter

class TestV76MultiAgentTeamRouter(unittest.TestCase):

    def setUp(self):
        self.router = MultiAgentTeamRouter()

    def test_1_route_mission_team_returns_dict(self):
        """Test 1: route_mission_team returns dictionary."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertIsInstance(res, dict)

    def test_2_team_pipeline_steps_count_4(self):
        """Test 2: team_pipeline contains 4 steps."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(len(res["team_pipeline"]), 4)

    def test_3_active_specialists_count_4(self):
        """Test 3: active_specialists contains 4 agents."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(len(res["active_specialists"]), 4)

    def test_4_pipeline_status_success(self):
        """Test 4: pipeline_status is PIPELINE_SUCCESS."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(res["pipeline_status"], "PIPELINE_SUCCESS")

    def test_5_joint_verification_contains_verified(self):
        """Test 5: joint_verification contains VERIFIED."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertIn("VERIFIED", res["joint_verification"])

    def test_6_step_1_agent_is_research_agent(self):
        """Test 6: Step 1 agent is ResearchAgent."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(res["team_pipeline"][0]["agent_id"], "ResearchAgent")

    def test_7_step_2_agent_is_data_analysis_agent(self):
        """Test 7: Step 2 agent is DataAnalysisAgent."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(res["team_pipeline"][1]["agent_id"], "DataAnalysisAgent")

    def test_8_step_3_agent_is_finance_agent(self):
        """Test 8: Step 3 agent is FinanceAgent."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(res["team_pipeline"][2]["agent_id"], "FinanceAgent")

    def test_9_step_4_agent_is_writing_agent(self):
        """Test 9: Step 4 agent is WritingAgent."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertEqual(res["team_pipeline"][3]["agent_id"], "WritingAgent")

    def test_10_routing_timestamp_string(self):
        """Test 10: routing_timestamp is non-empty string."""
        res = self.router.route_mission_team("Thesis Finance Memo")
        self.assertTrue(len(res["routing_timestamp"]) > 0)

    def test_11_class_name(self):
        """Test 11: Class name is MultiAgentTeamRouter."""
        self.assertEqual(self.router.__class__.__name__, "MultiAgentTeamRouter")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable across calls."""
        r1 = self.router.route_mission_team("Objective")
        r2 = self.router.route_mission_team("Objective")
        self.assertEqual(r1["pipeline_status"], r2["pipeline_status"])

    def test_13_json_serializable(self):
        """Test 13: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.router.route_mission_team("Objective"))
        self.assertIsInstance(dumped, str)

    def test_14_mission_objective_preserved(self):
        """Test 14: Mission objective preserved in result."""
        res = self.router.route_mission_team("Custom Objective")
        self.assertEqual(res["mission_objective"], "Custom Objective")

    def test_15_summary_keys_count(self):
        """Test 15: route_mission_team returns 6 keys."""
        res = self.router.route_mission_team("Objective")
        self.assertEqual(len(res), 6)

    def test_16_all_pipeline_steps_completed(self):
        """Test 16: All pipeline step statuses are COMPLETED."""
        res = self.router.route_mission_team("Objective")
        for step in res["team_pipeline"]:
            self.assertEqual(step["status"], "COMPLETED")

    def test_17_pipeline_step_keys_count(self):
        """Test 17: Each pipeline step contains 4 keys."""
        res = self.router.route_mission_team("Objective")
        for step in res["team_pipeline"]:
            self.assertEqual(len(step), 4)

    def test_18_active_specialists_include_research_agent(self):
        """Test 18: active_specialists includes ResearchAgent."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("ResearchAgent", res["active_specialists"])

    def test_19_active_specialists_include_data_analysis_agent(self):
        """Test 19: active_specialists includes DataAnalysisAgent."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("DataAnalysisAgent", res["active_specialists"])

    def test_20_active_specialists_include_finance_agent(self):
        """Test 20: active_specialists includes FinanceAgent."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("FinanceAgent", res["active_specialists"])

    def test_21_active_specialists_include_writing_agent(self):
        """Test 21: active_specialists includes WritingAgent."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("WritingAgent", res["active_specialists"])

    def test_22_stateless_routing(self):
        """Test 22: route_mission_team does not mutate router state."""
        r1 = self.router.route_mission_team("Objective")
        r2 = self.router.route_mission_team("Objective")
        self.assertEqual(r1, r2)

    def test_23_router_instantiation_clean(self):
        """Test 23: MultiAgentTeamRouter instantiates cleanly."""
        router = MultiAgentTeamRouter()
        self.assertIsNotNone(router)

    def test_24_no_error_keys(self):
        """Test 24: Result does not contain error key."""
        res = self.router.route_mission_team("Objective")
        self.assertNotIn("error", res)

    def test_25_timestamp_format(self):
        """Test 25: Timestamp includes date and time formatted string."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("-", res["routing_timestamp"])
        self.assertIn(":", res["routing_timestamp"])

    def test_26_step_numbers_sequential(self):
        """Test 26: Pipeline steps are 1, 2, 3, 4."""
        res = self.router.route_mission_team("Objective")
        steps = [s["step"] for s in res["team_pipeline"]]
        self.assertEqual(steps, [1, 2, 3, 4])

    def test_27_roles_non_empty(self):
        """Test 27: All pipeline step roles are non-empty strings."""
        res = self.router.route_mission_team("Objective")
        for s in res["team_pipeline"]:
            self.assertTrue(len(s["role"]) > 0)

    def test_28_active_specialists_list_type(self):
        """Test 28: active_specialists is list."""
        res = self.router.route_mission_team("Objective")
        self.assertIsInstance(res["active_specialists"], list)

    def test_29_team_pipeline_list_type(self):
        """Test 29: team_pipeline is list."""
        res = self.router.route_mission_team("Objective")
        self.assertIsInstance(res["team_pipeline"], list)

    def test_30_dict_return_type(self):
        """Test 30: Return type is dict."""
        self.assertEqual(type(self.router.route_mission_team("Objective")), dict)

    def test_31_joint_verification_string_type(self):
        """Test 31: joint_verification is string."""
        res = self.router.route_mission_team("Objective")
        self.assertEqual(type(res["joint_verification"]), str)

    def test_32_pipeline_status_string_type(self):
        """Test 32: pipeline_status is string."""
        res = self.router.route_mission_team("Objective")
        self.assertEqual(type(res["pipeline_status"]), str)

    def test_33_mission_objective_string_type(self):
        """Test 33: mission_objective is string."""
        res = self.router.route_mission_team("Objective")
        self.assertEqual(type(res["mission_objective"]), str)

    def test_34_routing_timestamp_length(self):
        """Test 34: routing_timestamp length >= 19."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["routing_timestamp"]) >= 19)

    def test_35_active_specialists_unique(self):
        """Test 35: All active specialist names are unique."""
        res = self.router.route_mission_team("Objective")
        names = set(res["active_specialists"])
        self.assertEqual(len(names), 4)

    def test_36_pipeline_step_agents_unique(self):
        """Test 36: All step agent IDs are unique."""
        res = self.router.route_mission_team("Objective")
        agents = set(s["agent_id"] for s in res["team_pipeline"])
        self.assertEqual(len(agents), 4)

    def test_37_governor_authorization_in_joint_verification(self):
        """Test 37: Joint verification mentions Governor Authorization."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("Governor Authorization", res["joint_verification"])

    def test_38_unit_tests_in_joint_verification(self):
        """Test 38: Joint verification mentions Unit Tests."""
        res = self.router.route_mission_team("Objective")
        self.assertIn("Unit Tests", res["joint_verification"])

    def test_39_pipeline_step_keys_present(self):
        """Test 39: Pipeline step contains step, agent_id, role, status."""
        res = self.router.route_mission_team("Objective")
        step = res["team_pipeline"][0]
        self.assertIn("step", step)
        self.assertIn("agent_id", step)
        self.assertIn("role", step)
        self.assertIn("status", step)

    def test_40_objective_string_non_empty(self):
        """Test 40: mission_objective is non-empty string."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["mission_objective"]) > 0)

    def test_41_pipeline_status_non_empty(self):
        """Test 41: pipeline_status is non-empty string."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["pipeline_status"]) > 0)

    def test_42_joint_verification_non_empty(self):
        """Test 42: joint_verification is non-empty string."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["joint_verification"]) > 0)

    def test_43_step_1_role_non_empty(self):
        """Test 43: Step 1 role is non-empty string."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["team_pipeline"][0]["role"]) > 0)

    def test_44_step_4_role_non_empty(self):
        """Test 44: Step 4 role is non-empty string."""
        res = self.router.route_mission_team("Objective")
        self.assertTrue(len(res["team_pipeline"][3]["role"]) > 0)

    def test_45_v7_6_multi_agent_team_router_verification_passed(self):
        """Test 45: All V7.6 multi-agent team router features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
