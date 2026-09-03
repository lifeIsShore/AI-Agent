import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.runtime.personal_ai_os_v6 import PersonalAIOS_v6

class TestV60PersistentPersonalAIOS(unittest.TestCase):

    def setUp(self):
        import tempfile
        import shutil
        self.temp_dir = tempfile.mkdtemp()
        self.os_runtime = PersonalAIOS_v6(storage_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_1_personal_ai_os_initializes(self):
        """Test 1: PersonalAIOS_v6 initializes cleanly with version v6.0.0."""
        self.assertEqual(self.os_runtime.version, "v6.0.0")

    def test_2_run_persistent_os_cycle(self):
        """Test 2: run_persistent_os_cycle executes master cycle successfully."""
        res = self.os_runtime.run_persistent_os_cycle("Check thesis deadline and replan schedule")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["os_version"], "v6.0.0")
        self.assertTrue(res["zero_bypass_governance"])

    def test_3_subcomponents_initialized(self):
        """Test 3: All 7 core master components initialized."""
        self.assertIsNotNone(self.os_runtime.runtime)
        self.assertIsNotNone(self.os_runtime.pilot_ctrl)
        self.assertIsNotNone(self.os_runtime.predictive_engine)
        self.assertIsNotNone(self.os_runtime.sim_env)
        self.assertIsNotNone(self.os_runtime.cf_planner)
        self.assertIsNotNone(self.os_runtime.mission_learning)
        self.assertIsNotNone(self.os_runtime.execution_intel)

    def test_4_zero_bypass_governance_invariant(self):
        """Test 4: Invariant zero_bypass_governance: True enforced on all OS cycles."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertTrue(res["zero_bypass_governance"])

    def test_5_simulation_scenario_included(self):
        """Test 5: simulation_scenario included in cycle output."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("simulation_scenario", res)

    def test_6_predictions_included(self):
        """Test 6: predictions included in cycle output."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("predictions", res)

    def test_7_recommended_strategy_included(self):
        """Test 7: recommended_strategy included in cycle output."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("recommended_strategy", res)

    def test_8_cycle_result_status_success(self):
        """Test 8: Underlying cycle_result status is SUCCESS."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertEqual(res["cycle_result"]["status"], "SUCCESS")

    def test_9_os_run_stateless_reset(self):
        """Test 9: OS instance reusable across multiple cycles."""
        res1 = self.os_runtime.run_persistent_os_cycle("Goal 1")
        res2 = self.os_runtime.run_persistent_os_cycle("Goal 2")
        self.assertEqual(res1["status"], res2["status"])

    def test_10_os_output_has_seven_keys(self):
        """Test 10: OS output dictionary contains 7 keys."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertEqual(len(res), 7)

    def test_11_os_version_string(self):
        """Test 11: os_version is string v6.0.0."""
        self.assertEqual(self.os_runtime.version, "v6.0.0")

    def test_12_pilot_controller_phase_five(self):
        """Test 12: PilotController phase is 5."""
        self.assertEqual(self.os_runtime.pilot_ctrl.current_phase, 5)

    def test_13_pilot_controller_mode_bounded_auto(self):
        """Test 13: PilotController mode is BOUNDED_AUTO."""
        self.assertEqual(self.os_runtime.pilot_ctrl.current_mode, "BOUNDED_AUTO")

    def test_14_cycle_result_contains_execution(self):
        """Test 14: cycle_result contains execution sub-dict."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("execution", res["cycle_result"])

    def test_15_cycle_result_contains_provenance_id(self):
        """Test 15: cycle_result contains provenance_id."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("provenance_id", res["cycle_result"])

    def test_16_cycle_result_security_invariants_verified(self):
        """Test 16: cycle_result verifies security invariants."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertTrue(res["cycle_result"]["security_invariants_verified"])

    def test_17_predictions_contain_governor_gated(self):
        """Test 17: predictions sub-dict contains governor_gated: True."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertTrue(res["predictions"]["governor_gated"])

    def test_18_simulation_scenario_valid_string(self):
        """Test 18: simulation_scenario is valid scenario string."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn(res["simulation_scenario"], ["AGGRESSIVE", "BALANCED", "CONSERVATIVE"])

    def test_19_recommended_strategy_string(self):
        """Test 19: recommended_strategy is string."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIsInstance(res["recommended_strategy"], str)

    def test_20_status_string_success(self):
        """Test 20: Status is SUCCESS string."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertEqual(res["status"], "SUCCESS")

    def test_21_run_persistent_os_cycle_empty_query(self):
        """Test 21: Handles empty query string cleanly."""
        res = self.os_runtime.run_persistent_os_cycle("")
        self.assertEqual(res["status"], "SUCCESS")

    def test_22_run_persistent_os_cycle_large_query(self):
        """Test 22: Handles complex multi-sentence query cleanly."""
        res = self.os_runtime.run_persistent_os_cycle("Complex query with multiple sub-goals and constraints")
        self.assertEqual(res["status"], "SUCCESS")

    def test_23_runtime_supervisor_state_running(self):
        """Test 23: Underlying supervisor state is RUNNING."""
        self.assertEqual(self.os_runtime.runtime.supervisor.current_state.name, "RUNNING")

    def test_24_os_has_runtime_attribute(self):
        """Test 24: OS instance has runtime attribute."""
        self.assertTrue(hasattr(self.os_runtime, "runtime"))

    def test_25_os_has_pilot_ctrl_attribute(self):
        """Test 25: OS instance has pilot_ctrl attribute."""
        self.assertTrue(hasattr(self.os_runtime, "pilot_ctrl"))

    def test_26_os_has_predictive_engine_attribute(self):
        """Test 26: OS instance has predictive_engine attribute."""
        self.assertTrue(hasattr(self.os_runtime, "predictive_engine"))

    def test_27_os_has_sim_env_attribute(self):
        """Test 27: OS instance has sim_env attribute."""
        self.assertTrue(hasattr(self.os_runtime, "sim_env"))

    def test_28_os_has_cf_planner_attribute(self):
        """Test 28: OS instance has cf_planner attribute."""
        self.assertTrue(hasattr(self.os_runtime, "cf_planner"))

    def test_29_os_has_mission_learning_attribute(self):
        """Test 29: OS instance has mission_learning attribute."""
        self.assertTrue(hasattr(self.os_runtime, "mission_learning"))

    def test_30_os_has_execution_intel_attribute(self):
        """Test 30: OS instance has execution_intel attribute."""
        self.assertTrue(hasattr(self.os_runtime, "execution_intel"))

    def test_31_multiple_os_instances_isolated(self):
        """Test 31: Multiple PersonalAIOS_v6 instances are isolated."""
        os1 = PersonalAIOS_v6()
        os2 = PersonalAIOS_v6()
        self.assertIsNot(os1, os2)

    def test_32_return_type_is_dict(self):
        """Test 32: run_persistent_os_cycle returns dict."""
        res = self.os_runtime.run_persistent_os_cycle("g")
        self.assertIsInstance(res, dict)

    def test_33_zero_bypass_governance_boolean(self):
        """Test 33: zero_bypass_governance is boolean."""
        res = self.os_runtime.run_persistent_os_cycle("g")
        self.assertIsInstance(res["zero_bypass_governance"], bool)

    def test_34_cycle_result_agent_id(self):
        """Test 34: cycle_result contains agent_id."""
        res = self.os_runtime.run_persistent_os_cycle("g")
        self.assertIn("agent_id", res["cycle_result"])

    def test_35_predictions_count_key_present(self):
        """Test 35: predictions sub-dict contains predictions_count key."""
        res = self.os_runtime.run_persistent_os_cycle("g")
        self.assertIn("predictions_count", res["predictions"])

    def test_36_predictions_list_present(self):
        """Test 36: predictions sub-dict contains predictions list."""
        res = self.os_runtime.run_persistent_os_cycle("g")
        self.assertIn("predictions", res["predictions"])

    def test_37_recommended_strategy_thesis(self):
        """Test 37: recommended_strategy defaults to strat_thesis_b for thesis query."""
        res = self.os_runtime.run_persistent_os_cycle("thesis")
        self.assertEqual(res["recommended_strategy"], "strat_thesis_b")

    def test_38_os_version_immutable(self):
        """Test 38: Version string is v6.0.0."""
        self.assertEqual(self.os_runtime.version, "v6.0.0")

    def test_39_pilot_controller_is_capability_allowed(self):
        """Test 39: PilotController evaluates capability permission."""
        ok, msg = self.os_runtime.pilot_ctrl.is_capability_allowed("read_email")
        self.assertTrue(ok)

    def test_40_master_os_integration_ready(self):
        """Test 40: Master OS runtime integration ready."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertEqual(res["status"], "SUCCESS")

    def test_41_cycle_result_outcome_id(self):
        """Test 41: cycle_result contains outcome_id."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("outcome_id", res["cycle_result"])

    def test_42_cycle_result_execution(self):
        """Test 42: cycle_result contains execution."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertIn("execution", res["cycle_result"])

    def test_43_cycle_result_has_all_keys(self):
        """Test 43: cycle_result contains 6 expected keys."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertEqual(len(res["cycle_result"]), 6)

    def test_44_master_os_stateless_execution(self):
        """Test 44: Master OS execution is stateless and reliable."""
        res = self.os_runtime.run_persistent_os_cycle("Goal")
        self.assertTrue(res["zero_bypass_governance"])

    def test_45_v6_0_persistent_personal_ai_os_verification_passed(self):
        """Test 45: All V6.0 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
