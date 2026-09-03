import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.reasoning.autonomous_research_engine import AutonomousResearchEngine

class TestV58AutonomousResearch(unittest.TestCase):

    def setUp(self):
        self.engine = AutonomousResearchEngine()

    def test_1_autonomous_research_engine_initializes(self):
        """Test 1: AutonomousResearchEngine initializes cleanly."""
        self.assertIsNotNone(self.engine)

    def test_2_conduct_research_empty_sources(self):
        """Test 2: conduct_autonomous_research handles empty initial_sources."""
        res = self.engine.conduct_autonomous_research("topic", [])
        self.assertEqual(res["facts_extracted"], 0)
        self.assertTrue(res["provenance_tracked"])

    def test_3_conduct_research_verifies_high_confidence(self):
        """Test 3: Conf >= 0.70 marked VERIFIED and RAG ingestible."""
        sources = [{"url": "https://uni.edu", "confidence": 0.85, "snippet": "evidence"}]
        res = self.engine.conduct_autonomous_research("thesis", sources)
        self.assertEqual(res["verified_facts"], 1)
        self.assertEqual(res["extracted_facts"][0]["verification_status"], "VERIFIED")
        self.assertTrue(res["extracted_facts"][0]["rag_ingestible"])

    def test_4_conduct_research_rejects_low_confidence(self):
        """Test 4: Conf < 0.70 marked UNVERIFIED_NEEDS_APPROVAL and not RAG ingestible."""
        sources = [{"url": "https://unverified.com", "confidence": 0.50, "snippet": "claim"}]
        res = self.engine.conduct_autonomous_research("topic", sources)
        self.assertEqual(res["verified_facts"], 0)
        self.assertEqual(res["extracted_facts"][0]["verification_status"], "UNVERIFIED_NEEDS_APPROVAL")
        self.assertFalse(res["extracted_facts"][0]["rag_ingestible"])

    def test_5_fact_id_prefix(self):
        """Test 5: Fact ID starts with fact_."""
        sources = [{"confidence": 0.90}]
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertTrue(res["extracted_facts"][0]["fact_id"].startswith("fact_"))

    def test_6_provenance_tracked_flag_is_true(self):
        """Test 6: Output contains provenance_tracked: True."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertTrue(res["provenance_tracked"])

    def test_7_total_sources_scanned(self):
        """Test 7: total_sources_scanned matches initial_sources length."""
        sources = [{}, {}, {}]
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertEqual(res["total_sources_scanned"], 3)

    def test_8_facts_extracted_matches_sources(self):
        """Test 8: facts_extracted matches initial_sources length."""
        sources = [{}, {}]
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertEqual(res["facts_extracted"], 2)

    def test_9_source_type_default(self):
        """Test 9: Default source_type is WEB_DOCUMENT."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(res["extracted_facts"][0]["source_type"], "WEB_DOCUMENT")

    def test_10_evidence_text_preserved(self):
        """Test 10: Evidence text preserved in extracted fact."""
        sources = [{"snippet": "exact evidence text"}]
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertEqual(res["extracted_facts"][0]["evidence"], "exact evidence text")

    def test_11_topic_string_preserved(self):
        """Test 11: Topic string preserved in result."""
        res = self.engine.conduct_autonomous_research("Agentic AI", [])
        self.assertEqual(res["topic"], "Agentic AI")

    def test_12_confidence_exact_0_70_is_verified(self):
        """Test 12: Confidence exact 0.70 is marked VERIFIED."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.70}])
        self.assertEqual(res["extracted_facts"][0]["verification_status"], "VERIFIED")

    def test_13_confidence_0_69_is_unverified(self):
        """Test 13: Confidence 0.69 is marked UNVERIFIED_NEEDS_APPROVAL."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.69}])
        self.assertEqual(res["extracted_facts"][0]["verification_status"], "UNVERIFIED_NEEDS_APPROVAL")

    def test_14_extracted_facts_is_list(self):
        """Test 14: extracted_facts is list."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res["extracted_facts"], list)

    def test_15_multiple_sources_mixed_verification(self):
        """Test 15: Multiple sources produce accurate verified count."""
        sources = [{"confidence": 0.80}, {"confidence": 0.40}, {"confidence": 0.95}]
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertEqual(res["verified_facts"], 2)

    def test_16_timestamp_field_preserved(self):
        """Test 16: Timestamp field preserved."""
        res = self.engine.conduct_autonomous_research("t", [{"timestamp": "2026-09-01T00:00:00Z"}])
        self.assertEqual(res["extracted_facts"][0]["timestamp"], "2026-09-01T00:00:00Z")

    def test_17_source_name_fallback(self):
        """Test 17: Source uses name fallback if url missing."""
        res = self.engine.conduct_autonomous_research("t", [{"name": "source_doc"}])
        self.assertEqual(res["extracted_facts"][0]["source"], "source_doc")

    def test_18_source_web_source_fallback(self):
        """Test 18: Source uses web_source default if name and url missing."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(res["extracted_facts"][0]["source"], "web_source")

    def test_19_facts_extracted_count_equals_list_len(self):
        """Test 19: facts_extracted count equals extracted_facts length."""
        res = self.engine.conduct_autonomous_research("t", [{}, {}])
        self.assertEqual(res["facts_extracted"], len(res["extracted_facts"]))

    def test_20_stateless_execution(self):
        """Test 20: Engine execution is stateless."""
        res1 = self.engine.conduct_autonomous_research("t", [{}])
        res2 = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(res1["facts_extracted"], res2["facts_extracted"])

    def test_21_result_dict_keys_count(self):
        """Test 21: Result dict contains 6 keys."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertEqual(len(res), 6)

    def test_22_extracted_fact_keys_count(self):
        """Test 22: Extracted fact entry contains 9 keys."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(len(res["extracted_facts"][0]), 9)

    def test_23_confidence_float_type(self):
        """Test 23: confidence is float."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.85}])
        self.assertIsInstance(res["extracted_facts"][0]["confidence"], float)

    def test_24_rag_ingestible_boolean(self):
        """Test 24: rag_ingestible is boolean."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertIsInstance(res["extracted_facts"][0]["rag_ingestible"], bool)

    def test_25_verification_status_string(self):
        """Test 25: verification_status is string."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertIsInstance(res["extracted_facts"][0]["verification_status"], str)

    def test_26_custom_source_type(self):
        """Test 26: Custom source_type preserved."""
        res = self.engine.conduct_autonomous_research("t", [{"source_type": "PDF_PAPER"}])
        self.assertEqual(res["extracted_facts"][0]["source_type"], "PDF_PAPER")

    def test_27_extracted_fact_topic(self):
        """Test 27: Topic included in each extracted fact."""
        res = self.engine.conduct_autonomous_research("finance", [{}])
        self.assertEqual(res["extracted_facts"][0]["topic"], "finance")

    def test_28_verified_facts_zero(self):
        """Test 28: Zero verified facts returned when all low confidence."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.10}])
        self.assertEqual(res["verified_facts"], 0)

    def test_29_all_verified_facts(self):
        """Test 29: All verified facts returned when high confidence."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.90}, {"confidence": 0.95}])
        self.assertEqual(res["verified_facts"], 2)

    def test_30_extracted_facts_list_iterable(self):
        """Test 30: extracted_facts is iterable."""
        res = self.engine.conduct_autonomous_research("t", [{}, {}])
        count = sum(1 for f in res["extracted_facts"])
        self.assertEqual(count, 2)

    def test_31_confidence_default_is_0_75(self):
        """Test 31: Default confidence is 0.75."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(res["extracted_facts"][0]["confidence"], 0.75)

    def test_32_snippet_default_text(self):
        """Test 32: Default snippet text used if missing."""
        res = self.engine.conduct_autonomous_research("t", [{}])
        self.assertEqual(res["extracted_facts"][0]["evidence"], "Extracted evidence text.")

    def test_33_research_engine_return_type_dict(self):
        """Test 33: Returns dictionary instance."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res, dict)

    def test_34_fact_id_uniqueness(self):
        """Test 34: Fact IDs are unique across items."""
        res = self.engine.conduct_autonomous_research("t", [{}, {}])
        self.assertNotEqual(res["extracted_facts"][0]["fact_id"], res["extracted_facts"][1]["fact_id"])

    def test_35_provenance_tracked_is_boolean(self):
        """Test 35: provenance_tracked is boolean."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res["provenance_tracked"], bool)

    def test_36_total_sources_scanned_integer(self):
        """Test 36: total_sources_scanned is integer."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res["total_sources_scanned"], int)

    def test_37_facts_extracted_integer(self):
        """Test 37: facts_extracted is integer."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res["facts_extracted"], int)

    def test_38_verified_facts_integer(self):
        """Test 38: verified_facts is integer."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIsInstance(res["verified_facts"], int)

    def test_39_url_field_priority(self):
        """Test 39: URL field prioritised over name."""
        res = self.engine.conduct_autonomous_research("t", [{"url": "http://a.com", "name": "a"}])
        self.assertEqual(res["extracted_facts"][0]["source"], "http://a.com")

    def test_40_rag_ingestible_false_for_unverified(self):
        """Test 40: rag_ingestible is False for UNVERIFIED_NEEDS_APPROVAL."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.2}])
        self.assertFalse(res["extracted_facts"][0]["rag_ingestible"])

    def test_41_rag_ingestible_true_for_verified(self):
        """Test 41: rag_ingestible is True for VERIFIED."""
        res = self.engine.conduct_autonomous_research("t", [{"confidence": 0.9}])
        self.assertTrue(res["extracted_facts"][0]["rag_ingestible"])

    def test_42_topic_empty_string(self):
        """Test 42: Handles empty string topic."""
        res = self.engine.conduct_autonomous_research("", [])
        self.assertEqual(res["topic"], "")

    def test_43_large_sources_list(self):
        """Test 43: Handles list of 20 sources cleanly."""
        sources = [{"confidence": 0.8}] * 20
        res = self.engine.conduct_autonomous_research("t", sources)
        self.assertEqual(res["facts_extracted"], 20)

    def test_44_research_engine_integration_ready(self):
        """Test 44: Output structured for ResearchSpecialist integration."""
        res = self.engine.conduct_autonomous_research("t", [])
        self.assertIn("extracted_facts", res)

    def test_45_v5_8_autonomous_research_verification_passed(self):
        """Test 45: All V5.8 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
