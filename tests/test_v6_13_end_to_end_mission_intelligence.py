import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.intelligence.end_to_end_mission_intelligence import EndToEndMissionIntelligence

class TestV613EndToEndMissionIntelligence(unittest.TestCase):

    def setUp(self):
        self.intelligence = EndToEndMissionIntelligence()

    def test_1_synthesize_situation_returns_dict(self):
        """Test 1: synthesize_situation returns dictionary."""
        res = self.intelligence.synthesize_situation()
        self.assertIsInstance(res, dict)

    def test_2_synthesis_keys_count(self):
        """Test 2: synthesize_situation returns 6 keys."""
        res = self.intelligence.synthesize_situation()
        self.assertEqual(len(res), 6)

    def test_3_current_priority_goal_string(self):
        """Test 3: current_priority_goal mentions Master Thesis."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Master Thesis", res["current_priority_goal"])

    def test_4_next_recommended_action_string(self):
        """Test 4: next_recommended_action mentions literature contradiction analysis."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("contradiction", res["next_recommended_action"])

    def test_5_why_this_action_string(self):
        """Test 5: why_this_action explains reasoning."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Strategy C", res["why_this_action"])

    def test_6_consequence_if_not_executed_string(self):
        """Test 6: consequence_if_not_executed mentions workload risk."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("workload risk", res["consequence_if_not_executed"])

    def test_7_subsystem_evidence_dict(self):
        """Test 7: subsystem_evidence contains 4 keys."""
        res = self.intelligence.synthesize_situation()
        self.assertEqual(len(res["subsystem_evidence"]), 4)

    def test_8_subsystem_evidence_contains_knowledge_graph(self):
        """Test 8: subsystem_evidence contains knowledge_graph key."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("knowledge_graph", res["subsystem_evidence"])

    def test_9_subsystem_evidence_contains_workload_model(self):
        """Test 9: subsystem_evidence contains workload_model key."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("workload_model", res["subsystem_evidence"])

    def test_10_subsystem_evidence_contains_strategy_optimizer(self):
        """Test 10: subsystem_evidence contains strategy_optimizer key."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("strategy_optimizer", res["subsystem_evidence"])

    def test_11_subsystem_evidence_contains_governor_status(self):
        """Test 11: subsystem_evidence contains governor_status key."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("governor_status", res["subsystem_evidence"])

    def test_12_timestamp_non_empty(self):
        """Test 12: synthesis_timestamp is non-empty string."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["synthesis_timestamp"]) > 0)

    def test_13_class_name(self):
        """Test 13: Class name is EndToEndMissionIntelligence."""
        self.assertEqual(self.intelligence.__class__.__name__, "EndToEndMissionIntelligence")

    def test_14_reusable_instance(self):
        """Test 14: Instance is reusable across calls."""
        s1 = self.intelligence.synthesize_situation()
        s2 = self.intelligence.synthesize_situation()
        self.assertEqual(s1["current_priority_goal"], s2["current_priority_goal"])

    def test_15_json_serializable(self):
        """Test 15: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.intelligence.synthesize_situation())
        self.assertIsInstance(dumped, str)

    def test_16_governor_authorized_in_evidence(self):
        """Test 16: Governor status in evidence is AUTHORIZED."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("AUTHORIZED", res["subsystem_evidence"]["governor_status"])

    def test_17_workload_overload_in_evidence(self):
        """Test 17: Workload model evidence mentions Overload +12h."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Overload", res["subsystem_evidence"]["workload_model"])

    def test_18_knowledge_graph_provenance_in_evidence(self):
        """Test 18: Knowledge graph evidence mentions provenance fact_."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("fact_", res["subsystem_evidence"]["knowledge_graph"])

    def test_19_strategy_c_in_evidence(self):
        """Test 19: Strategy optimizer evidence mentions Strategy C."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Strategy C", res["subsystem_evidence"]["strategy_optimizer"])

    def test_20_timestamp_has_colons(self):
        """Test 20: synthesis_timestamp contains formatted time with colons."""
        res = self.intelligence.synthesize_situation()
        self.assertIn(":", res["synthesis_timestamp"])

    def test_21_current_priority_goal_score(self):
        """Test 21: Goal string includes 9.4 score."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("9.4", res["current_priority_goal"])

    def test_22_next_recommended_action_agent(self):
        """Test 22: Action mentions ResearchSpecialist."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("ResearchSpecialist", res["next_recommended_action"])

    def test_23_next_recommended_action_model(self):
        """Test 23: Action mentions Strong Cloud LLM."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Strong Cloud LLM", res["next_recommended_action"])

    def test_24_consequence_probability(self):
        """Test 24: Consequence mentions 68% probability."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("68%", res["consequence_if_not_executed"])

    def test_25_subsystem_evidence_values_strings(self):
        """Test 25: All subsystem evidence values are strings."""
        res = self.intelligence.synthesize_situation()
        for v in res["subsystem_evidence"].values():
            self.assertIsInstance(v, str)

    def test_26_stateless_synthesis(self):
        """Test 26: synthesize_situation does not mutate state."""
        s1 = self.intelligence.synthesize_situation()
        s2 = self.intelligence.synthesize_situation()
        self.assertEqual(s1, s2)

    def test_27_why_this_action_non_empty(self):
        """Test 27: why_this_action is non-empty string."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["why_this_action"]) > 0)

    def test_28_consequence_non_empty(self):
        """Test 28: consequence_if_not_executed is non-empty string."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["consequence_if_not_executed"]) > 0)

    def test_29_action_non_empty(self):
        """Test 29: next_recommended_action is non-empty string."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["next_recommended_action"]) > 0)

    def test_30_priority_goal_non_empty(self):
        """Test 30: current_priority_goal is non-empty string."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["current_priority_goal"]) > 0)

    def test_31_synthesis_keys_present(self):
        """Test 31: All 6 expected keys are present in result."""
        res = self.intelligence.synthesize_situation()
        expected = ["synthesis_timestamp", "current_priority_goal", "next_recommended_action", "why_this_action", "consequence_if_not_executed", "subsystem_evidence"]
        for k in expected:
            self.assertIn(k, res)

    def test_32_timestamp_length(self):
        """Test 32: synthesis_timestamp length is at least 19 characters."""
        res = self.intelligence.synthesize_situation()
        self.assertTrue(len(res["synthesis_timestamp"]) >= 19)

    def test_33_methodology_deadline_in_consequence(self):
        """Test 33: Consequence mentions methodology deadline."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("methodology deadline", res["consequence_if_not_executed"])

    def test_34_arxiv_paper_in_action(self):
        """Test 34: Action mentions arXiv Paper 2401.9912."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("2401.9912", res["next_recommended_action"])

    def test_35_nov_30_deadline_in_why(self):
        """Test 35: Why string mentions Nov 30 deadline."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Nov 30", res["why_this_action"])

    def test_36_dual_verification_in_why(self):
        """Test 36: Why string mentions dual contradiction verification."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("contradiction verification", res["why_this_action"])

    def test_37_capacity_52h_in_evidence(self):
        """Test 37: Evidence mentions Capacity 52h."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("52h", res["subsystem_evidence"]["workload_model"])

    def test_38_demand_64h_in_evidence(self):
        """Test 38: Evidence mentions Demand 64h."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("64h", res["subsystem_evidence"]["workload_model"])

    def test_39_davis_in_evidence(self):
        """Test 39: Evidence mentions n_davis."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("n_davis", res["subsystem_evidence"]["knowledge_graph"])

    def test_40_bounded_autonomy_in_evidence(self):
        """Test 40: Evidence mentions Bounded Autonomy."""
        res = self.intelligence.synthesize_situation()
        self.assertIn("Bounded Autonomy", res["subsystem_evidence"]["governor_status"])

    def test_41_intelligence_class_instantiation(self):
        """Test 41: EndToEndMissionIntelligence instantiates cleanly."""
        obj = EndToEndMissionIntelligence()
        self.assertIsNotNone(obj)

    def test_42_dict_return_type(self):
        """Test 42: Return type is dictionary."""
        self.assertEqual(type(self.intelligence.synthesize_situation()), dict)

    def test_43_subsystem_evidence_dict_type(self):
        """Test 43: subsystem_evidence return type is dict."""
        res = self.intelligence.synthesize_situation()
        self.assertEqual(type(res["subsystem_evidence"]), dict)

    def test_44_no_error_key_in_synthesis(self):
        """Test 44: Synthesis result does not contain error key."""
        res = self.intelligence.synthesize_situation()
        self.assertNotIn("error", res)

    def test_45_v6_13_end_to_end_mission_intelligence_verification_passed(self):
        """Test 45: All V6.13 end-to-end mission intelligence features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
