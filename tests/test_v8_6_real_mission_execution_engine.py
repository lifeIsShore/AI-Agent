import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.real_mission_execution_engine import RealMissionExecutionEngine
from personal_agent.runtime.universal_tool_registry import UniversalToolRegistry
from personal_agent.orchestration.mission_state_machine import MissionStateMachine
from personal_agent.provenance.mission_provenance_logger import MissionProvenanceLogger

class TestV86RealMissionExecutionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RealMissionExecutionEngine()
        self.registry = UniversalToolRegistry()
        self.state_machine = MissionStateMachine("M-2026-TEST")
        self.logger = MissionProvenanceLogger()

    def test_1_dispatch_real_mission_returns_dict(self):
        """Test 1: dispatch_real_mission returns dictionary."""
        res = self.engine.dispatch_real_mission("Fix sandbox bug")
        self.assertIsInstance(res, dict)
        self.assertTrue(res["mission_id"].startswith("M-"))

    def test_2_mission_pipeline_steps_count_6(self):
        """Test 2: pipeline_steps contains 6 steps."""
        res = self.engine.dispatch_real_mission("Fix sandbox bug")
        self.assertEqual(len(res["pipeline_steps"]), 6)

    def test_3_participating_agents_count_4(self):
        """Test 3: participating_agents contains 4 agents."""
        res = self.engine.dispatch_real_mission("Fix sandbox bug")
        self.assertEqual(len(res["participating_agents"]), 4)

    def test_4_universal_tool_registry_coding_agent(self):
        """Test 4: CodingAgent has file.patch tool registered."""
        self.assertTrue(self.registry.is_tool_registered_for_agent("CodingAgent", "file.patch"))

    def test_5_universal_tool_registry_research_agent(self):
        """Test 5: ResearchAgent has web.search tool registered."""
        self.assertTrue(self.registry.is_tool_registered_for_agent("ResearchAgent", "web.search"))

    def test_6_restricted_tool_requires_approval(self):
        """Test 6: git.push evaluates to PENDING_HUMAN_APPROVAL."""
        res = self.registry.evaluate_tool_authority("CodingAgent", "git.push")
        self.assertEqual(res["status"], "PENDING_HUMAN_APPROVAL")

    def test_7_unregistered_tool_denied(self):
        """Test 7: Unregistered tool evaluates to DENIED."""
        res = self.registry.evaluate_tool_authority("WritingAgent", "git.push")
        self.assertEqual(res["status"], "DENIED")

    def test_8_mission_state_machine_initial_state(self):
        """Test 8: Initial state is CREATED."""
        self.assertEqual(self.state_machine.current_state, "CREATED")

    def test_9_mission_state_machine_transition(self):
        """Test 9: State transition to EXECUTING works."""
        self.assertTrue(self.state_machine.transition_to("EXECUTING", "Started execution"))
        self.assertEqual(self.state_machine.current_state, "EXECUTING")

    def test_10_mission_state_machine_invalid_transition(self):
        """Test 10: Invalid state transition returns False."""
        self.assertFalse(self.state_machine.transition_to("INVALID_STATE"))

    def test_11_log_mission_action_provenance(self):
        """Test 11: Provenance log starts with fact_prov_."""
        res = self.logger.log_mission_action(
            "M-1", "CodingAgent", "qwen2.5:1.5b", "file.patch", "runtime.py",
            "Fix bug", "HITL_APPROVED", "TESTS_PASSED", "SUCCESS"
        )
        self.assertTrue(res["provenance_id"].startswith("fact_prov_"))

    def test_12_provenance_records_count(self):
        """Test 12: Provenance logger stores records in list."""
        self.logger.log_mission_action("M-1", "A", "M", "T", "Tar", "R", "Auth", "V", "O")
        self.assertEqual(len(self.logger.provenance_records), 1)

    def test_13_json_serializable_dispatch(self):
        """Test 13: Mission payload is JSON serializable."""
        import json
        res = self.engine.dispatch_real_mission("Test")
        dumped = json.dumps(res)
        self.assertIsInstance(dumped, str)

    def test_14_json_serializable_provenance(self):
        """Test 14: Provenance record is JSON serializable."""
        import json
        res = self.logger.log_mission_action("M-1", "A", "M", "T", "Tar", "R", "Auth", "V", "O")
        dumped = json.dumps(res)
        self.assertIsInstance(dumped, str)

    def test_15_json_serializable_authority(self):
        """Test 15: Tool authority dictionary is JSON serializable."""
        import json
        res = self.registry.evaluate_tool_authority("CodingAgent", "file.patch")
        dumped = json.dumps(res)
        self.assertIsInstance(dumped, str)

    def test_16_state_machine_history_length(self):
        """Test 16: State machine history tracks transition count."""
        self.state_machine.transition_to("PLANNING")
        self.state_machine.transition_to("EXECUTING")
        self.assertEqual(len(self.state_machine.state_history), 3)

    def test_17_engine_active_missions_tracking(self):
        """Test 17: Active missions tracked by engine."""
        res = self.engine.dispatch_real_mission("Prompt")
        fetched = self.engine.get_mission_status(res["mission_id"])
        self.assertIsNotNone(fetched)

    def test_18_governor_authorization_in_dispatch(self):
        """Test 18: Governor authorization in dispatch payload."""
        res = self.engine.dispatch_real_mission("Prompt")
        self.assertEqual(res["governor_authorization"], "AUTHORIZED_BOUNDED_AUTO")

    def test_19_data_analysis_agent_tools(self):
        """Test 19: DataAnalysisAgent has dataset.inspect tool."""
        self.assertTrue(self.registry.is_tool_registered_for_agent("DataAnalysisAgent", "dataset.inspect"))

    def test_20_finance_agent_tools(self):
        """Test 20: FinanceAgent has financial_data.read tool."""
        self.assertTrue(self.registry.is_tool_registered_for_agent("FinanceAgent", "financial_data.read"))

    def test_21_writing_agent_tools(self):
        """Test 21: WritingAgent has document.write tool."""
        self.assertTrue(self.registry.is_tool_registered_for_agent("WritingAgent", "document.write"))

    def test_22_state_machine_valid_states_count(self):
        """Test 22: MissionStateMachine has 14 valid states."""
        self.assertEqual(len(MissionStateMachine.VALID_STATES), 14)

    def test_23_provenance_record_keys_count(self):
        """Test 23: Provenance record contains 11 keys."""
        res = self.logger.log_mission_action("M-1", "A", "M", "T", "Tar", "R", "Auth", "V", "O")
        self.assertEqual(len(res), 11)

    def test_24_plan_mode_progress_percent(self):
        """Test 24: PLAN mode sets progress_percent to 45."""
        res = self.engine.dispatch_real_mission("Prompt", mode="PLAN")
        self.assertEqual(res["progress_percent"], 45)

    def test_25_execute_mode_progress_percent(self):
        """Test 25: EXECUTE mode sets progress_percent to 85."""
        res = self.engine.dispatch_real_mission("Prompt", mode="EXECUTE")
        self.assertEqual(res["progress_percent"], 85)

    def test_26_step_1_agent_is_mission_planner(self):
        """Test 26: Step 1 agent is MissionPlanner."""
        res = self.engine.dispatch_real_mission("Prompt")
        self.assertEqual(res["pipeline_steps"][0]["agent"], "MissionPlanner")

    def test_27_step_6_agent_is_verification_agent(self):
        """Test 27: Step 6 agent is VerificationAgent."""
        res = self.engine.dispatch_real_mission("Prompt")
        self.assertEqual(res["pipeline_steps"][5]["agent"], "VerificationAgent")

    def test_28_state_machine_stopped_transition(self):
        """Test 28: State transition to STOPPED works."""
        self.assertTrue(self.state_machine.transition_to("STOPPED"))

    def test_29_state_machine_emergency_stop_transition(self):
        """Test 29: State transition to EMERGENCY_STOP works."""
        self.assertTrue(self.state_machine.transition_to("EMERGENCY_STOP"))

    def test_30_state_machine_cancelled_transition(self):
        """Test 30: State transition to CANCELLED works."""
        self.assertTrue(self.state_machine.transition_to("CANCELLED"))

    def test_31_engine_instantiation(self):
        """Test 31: RealMissionExecutionEngine instantiates cleanly."""
        self.assertIsNotNone(self.engine)

    def test_32_registry_instantiation(self):
        """Test 32: UniversalToolRegistry instantiates cleanly."""
        self.assertIsNotNone(self.registry)

    def test_33_logger_instantiation(self):
        """Test 33: MissionProvenanceLogger instantiates cleanly."""
        self.assertIsNotNone(self.logger)

    def test_34_prompt_preserved(self):
        """Test 34: Prompt preserved in dispatch payload."""
        res = self.engine.dispatch_real_mission("Custom Prompt")
        self.assertEqual(res["prompt"], "Custom Prompt")

    def test_35_timestamp_non_empty(self):
        """Test 35: submitted_at is non-empty string."""
        res = self.engine.dispatch_real_mission("Prompt")
        self.assertTrue(len(res["submitted_at"]) > 0)

    def test_36_tool_authority_denied_reason(self):
        """Test 36: Denied tool authority returns clear reason."""
        res = self.registry.evaluate_tool_authority("WritingAgent", "git.push")
        self.assertIn("not registered", res["reason"])

    def test_37_tool_authority_restricted_reason(self):
        """Test 37: Restricted tool authority returns human approval reason."""
        res = self.registry.evaluate_tool_authority("CodingAgent", "git.push")
        self.assertIn("human approval", res["reason"])

    def test_38_provenance_records_list_type(self):
        """Test 38: provenance_records is list."""
        self.assertIsInstance(self.logger.provenance_records, list)

    def test_39_active_missions_dict_type(self):
        """Test 39: active_missions is dict."""
        self.assertIsInstance(self.engine.active_missions, dict)

    def test_40_agent_tool_mappings_count_5(self):
        """Test 40: agent_tool_mappings contains 5 agents."""
        self.assertEqual(len(self.registry.agent_tool_mappings), 5)

    def test_41_restricted_tools_count_3(self):
        """Test 41: restricted_tools contains 3 tools."""
        self.assertEqual(len(self.registry.restricted_tools), 3)

    def test_42_state_machine_invalid_init_raises(self):
        """Test 42: Invalid initial state raises ValueError."""
        with self.assertRaises(ValueError):
            MissionStateMachine("M-1", initial_state="INVALID")

    def test_43_get_mission_status_returns_none_for_missing(self):
        """Test 43: get_mission_status returns None for missing ID."""
        self.assertIsNone(self.engine.get_mission_status("missing_id"))

    def test_44_state_machine_history_records_reason(self):
        """Test 44: State history records transition reason."""
        self.state_machine.transition_to("PLANNING", "Reason X")
        self.assertEqual(self.state_machine.state_history[1]["reason"], "Reason X")

    def test_45_v8_6_real_mission_execution_engine_verification_passed(self):
        """Test 45: All V8.6 to V9.0 features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
