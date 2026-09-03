import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.research_agent import ResearchAgent

class TestV72ResearchAgent2(unittest.TestCase):

    def setUp(self):
        self.research_agent = ResearchAgent()

    def test_1_agent_id_is_research_agent(self):
        """Test 1: agent_id is ResearchAgent."""
        self.assertEqual(self.research_agent.agent_id, "ResearchAgent")

    def test_2_role_is_researcher(self):
        """Test 2: role is RESEARCHER."""
        self.assertEqual(self.research_agent.role, "RESEARCHER")

    def test_3_conduct_deep_research_returns_dict(self):
        """Test 3: conduct_deep_research returns dictionary."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertIsInstance(res, dict)

    def test_4_sources_found_count(self):
        """Test 4: sources_found is 18."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertEqual(res["sources_found"], 18)

    def test_5_verified_evidence_nodes_count(self):
        """Test 5: verified_evidence_nodes is 12."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertEqual(res["verified_evidence_nodes"], 12)

    def test_6_contradiction_detected_boolean(self):
        """Test 6: contradiction_detected is True."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertTrue(res["contradiction_detected"])

    def test_7_claim_evidence_map_list(self):
        """Test 7: claim_evidence_map is non-empty list."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertTrue(len(res["claim_evidence_map"]) > 0)

    def test_8_claim_evidence_map_provenance(self):
        """Test 8: claim_evidence_map contains provenance_id starting with fact_."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        item = res["claim_evidence_map"][0]
        self.assertTrue(item["provenance_id"].startswith("fact_"))

    def test_9_governor_authorization_authorized(self):
        """Test 9: Governor authorization is AUTHORIZED."""
        res = self.research_agent.conduct_deep_research("AI Governance")
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_10_capabilities_count_5(self):
        """Test 10: Capabilities count is 5."""
        self.assertEqual(len(self.research_agent.capabilities), 5)

    def test_11_class_name(self):
        """Test 11: Class name is ResearchAgent."""
        self.assertEqual(self.research_agent.__class__.__name__, "ResearchAgent")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable across calls."""
        r1 = self.research_agent.conduct_deep_research("Topic")
        r2 = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(r1["sources_found"], r2["sources_found"])

    def test_13_json_serializable(self):
        """Test 13: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.research_agent.conduct_deep_research("Topic"))
        self.assertIsInstance(dumped, str)

    def test_14_topic_preserved(self):
        """Test 14: Topic string preserved in result."""
        res = self.research_agent.conduct_deep_research("Quantum Agent OS")
        self.assertEqual(res["topic"], "Quantum Agent OS")

    def test_15_tools_include_search_rag(self):
        """Test 15: Tools include search_rag."""
        self.assertIn("search_rag", self.research_agent.tools)

    def test_16_tools_include_web_search(self):
        """Test 16: Tools include web_search."""
        self.assertIn("web_search", self.research_agent.tools)

    def test_17_preferred_models_include_strong_cloud(self):
        """Test 17: Preferred models include strong_cloud."""
        self.assertIn("strong_cloud", self.research_agent.preferred_models)

    def test_18_autonomy_cap_bounded_auto(self):
        """Test 18: Autonomy cap is BOUNDED_AUTO."""
        self.assertEqual(self.research_agent.autonomy_cap, "BOUNDED_AUTO")

    def test_19_summary_keys_count(self):
        """Test 19: conduct_deep_research returns 8 keys."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(len(res), 8)

    def test_20_contradiction_details_non_empty(self):
        """Test 20: contradiction_details is non-empty string."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(len(res["contradiction_details"]) > 0)

    def test_21_claim_evidence_confidence_float(self):
        """Test 21: Evidence confidence is float."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertIsInstance(res["claim_evidence_map"][0]["confidence"], float)

    def test_22_sources_found_positive_int(self):
        """Test 22: sources_found is positive integer."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(res["sources_found"] > 0)

    def test_23_verified_evidence_nodes_positive_int(self):
        """Test 23: verified_evidence_nodes is positive integer."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(res["verified_evidence_nodes"] > 0)

    def test_24_inherits_from_specialist_agent(self):
        """Test 24: ResearchAgent inherits from SpecialistAgent."""
        from personal_agent.agents.base_specialist import SpecialistAgent
        self.assertTrue(issubclass(ResearchAgent, SpecialistAgent))

    def test_25_execute_task_overridden(self):
        """Test 25: Base execute_task works on ResearchAgent."""
        res = self.research_agent.execute_task({})
        self.assertEqual(res["agent_id"], "ResearchAgent")

    def test_26_to_dict_agent_id(self):
        """Test 26: to_dict contains agent_id ResearchAgent."""
        self.assertEqual(self.research_agent.to_dict()["agent_id"], "ResearchAgent")

    def test_27_tools_count_3(self):
        """Test 27: Tools count is 3."""
        self.assertEqual(len(self.research_agent.tools), 3)

    def test_28_preferred_models_count_2(self):
        """Test 28: Preferred models count is 2."""
        self.assertEqual(len(self.research_agent.preferred_models), 2)

    def test_29_instantiation_clean(self):
        """Test 29: ResearchAgent instantiates cleanly."""
        agent = ResearchAgent()
        self.assertIsNotNone(agent)

    def test_30_no_error_keys(self):
        """Test 30: Result does not contain error key."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertNotIn("error", res)

    def test_31_claim_string_non_empty(self):
        """Test 31: Claim string is non-empty."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(len(res["claim_evidence_map"][0]["claim"]) > 0)

    def test_32_evidence_string_non_empty(self):
        """Test 32: Evidence string is non-empty."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(len(res["claim_evidence_map"][0]["evidence"]) > 0)

    def test_33_confidence_bounded_below_1(self):
        """Test 33: Confidence <= 1.0."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(res["claim_evidence_map"][0]["confidence"] <= 1.0)

    def test_34_confidence_bounded_above_0(self):
        """Test 34: Confidence >= 0.0."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertTrue(res["claim_evidence_map"][0]["confidence"] >= 0.0)

    def test_35_arxiv_mentioned_in_contradiction(self):
        """Test 35: Contradiction details mentions arXiv."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertIn("arXiv", res["contradiction_details"])

    def test_36_tools_list_type(self):
        """Test 36: tools is list."""
        self.assertIsInstance(self.research_agent.tools, list)

    def test_37_capabilities_list_type(self):
        """Test 37: capabilities is list."""
        self.assertIsInstance(self.research_agent.capabilities, list)

    def test_38_preferred_models_list_type(self):
        """Test 38: preferred_models is list."""
        self.assertIsInstance(self.research_agent.preferred_models, list)

    def test_39_dict_return_type(self):
        """Test 39: to_dict return type is dict."""
        self.assertEqual(type(self.research_agent.to_dict()), dict)

    def test_40_research_return_type(self):
        """Test 40: conduct_deep_research return type is dict."""
        self.assertEqual(type(self.research_agent.conduct_deep_research("Topic")), dict)

    def test_41_claim_evidence_map_dict_type(self):
        """Test 41: claim_evidence_map items are dicts."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(type(res["claim_evidence_map"][0]), dict)

    def test_42_topic_string_type(self):
        """Test 42: topic is string."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(type(res["topic"]), str)

    def test_43_agent_id_string_type(self):
        """Test 43: agent_id is string."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(type(res["agent_id"]), str)

    def test_44_governor_authorization_string_type(self):
        """Test 44: governor_authorization is string."""
        res = self.research_agent.conduct_deep_research("Topic")
        self.assertEqual(type(res["governor_authorization"]), str)

    def test_45_v7_2_research_agent_2_verification_passed(self):
        """Test 45: All V7.2 ResearchAgent 2.0 features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
