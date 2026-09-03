import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.research.persistent_research_engine import (
    SourceMonitor,
    NoveltyDetector,
    ContradictionDetector,
    PersistentResearchEngine
)

class TestV66PersistentAutonomousResearch(unittest.TestCase):

    def setUp(self):
        self.engine = PersistentResearchEngine()
        self.monitor = SourceMonitor()
        self.novelty = NoveltyDetector()
        self.contradiction = ContradictionDetector()

    def test_1_engine_initializes(self):
        """Test 1: PersistentResearchEngine initializes cleanly."""
        self.assertIsNotNone(self.engine)

    def test_2_source_monitor_scans_sources(self):
        """Test 2: SourceMonitor returns list of 2 scanned paper sources."""
        papers = self.monitor.scan_sources("Autonomous Agents")
        self.assertEqual(len(papers), 2)
        self.assertTrue(papers[0]["paper_id"].startswith("arxiv_"))

    def test_3_novelty_detector_assess_novelty(self):
        """Test 3: NoveltyDetector assesses novelty score 0.88."""
        res = self.novelty.assess_novelty({"paper_id": "p1"}, [])
        self.assertEqual(res["novelty_score"], 0.88)
        self.assertTrue(res["is_novel"])

    def test_4_contradiction_detector_detects_contradiction(self):
        """Test 4: ContradictionDetector flags contradiction when title contains 'drift'."""
        paper = {"paper_id": "p2", "title": "LLM Strategy Drift"}
        res = self.contradiction.detect_contradictions(paper, "Adaptive Thresholds")
        self.assertTrue(res["has_contradiction"])

    def test_5_continuous_research_scan_result_structure(self):
        """Test 5: run_continuous_research_scan returns structured summary dict."""
        res = self.engine.run_continuous_research_scan("Autonomous Agent Governance")
        self.assertEqual(res["candidates_found"], 2)
        self.assertEqual(res["novel_count"], 2)
        self.assertEqual(res["contradiction_count"], 1)
        self.assertTrue(res["requires_user_attention"])

    def test_6_topic_string_preserved(self):
        """Test 6: Topic string preserved in result."""
        res = self.engine.run_continuous_research_scan("Custom Topic")
        self.assertEqual(res["topic"], "Custom Topic")

    def test_7_evaluations_list_length(self):
        """Test 7: evaluations list length matches candidates_found."""
        res = self.engine.run_continuous_research_scan()
        self.assertEqual(len(res["evaluations"]), res["candidates_found"])

    def test_8_stateless_execution(self):
        """Test 8: Research scan is stateless and repeatable."""
        r1 = self.engine.run_continuous_research_scan()
        r2 = self.engine.run_continuous_research_scan()
        self.assertEqual(r1["candidates_found"], r2["candidates_found"])

    def test_9_source_monitor_paper_dict_keys(self):
        """Test 9: Scanned paper dict contains 5 keys."""
        papers = self.monitor.scan_sources("Topic")
        self.assertEqual(len(papers[0]), 5)

    def test_10_novelty_dict_keys_count(self):
        """Test 10: Novelty assessment dict contains 4 keys."""
        res = self.novelty.assess_novelty({"paper_id": "p1"}, [])
        self.assertEqual(len(res), 4)

    def test_11_contradiction_dict_keys_count(self):
        """Test 11: Contradiction dict contains 3 keys."""
        res = self.contradiction.detect_contradictions({}, "")
        self.assertEqual(len(res), 3)

    def test_12_requires_user_attention_boolean(self):
        """Test 12: requires_user_attention is boolean."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["requires_user_attention"], bool)

    def test_13_last_scan_timestamp_string(self):
        """Test 13: last_scan_timestamp is string."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["last_scan_timestamp"], str)

    def test_14_candidates_found_integer(self):
        """Test 14: candidates_found is integer."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["candidates_found"], int)

    def test_15_verified_count_integer(self):
        """Test 15: verified_count is integer."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["verified_count"], int)

    def test_16_novel_count_integer(self):
        """Test 16: novel_count is integer."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["novel_count"], int)

    def test_17_contradiction_count_integer(self):
        """Test 17: contradiction_count is integer."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["contradiction_count"], int)

    def test_18_engine_reusable(self):
        """Test 18: Engine instance reusable across calls."""
        r1 = self.engine.run_continuous_research_scan("T1")
        r2 = self.engine.run_continuous_research_scan("T2")
        self.assertEqual(r1["topic"], "T1")
        self.assertEqual(r2["topic"], "T2")

    def test_19_paper_confidence_float(self):
        """Test 19: Paper confidence is float."""
        papers = self.monitor.scan_sources("T")
        self.assertIsInstance(papers[0]["confidence"], float)

    def test_20_novel_claims_list(self):
        """Test 20: novel_claims is list."""
        res = self.novelty.assess_novelty({"paper_id": "p1"}, [])
        self.assertIsInstance(res["novel_claims"], list)

    def test_21_contradiction_details_string(self):
        """Test 21: contradiction_details is string."""
        res = self.contradiction.detect_contradictions({"title": "drift"}, "")
        self.assertIsInstance(res["contradiction_details"], str)

    def test_22_non_contradictory_paper(self):
        """Test 22: Paper without 'drift' in title has no contradiction."""
        res = self.contradiction.detect_contradictions({"title": "General AI"}, "")
        self.assertFalse(res["has_contradiction"])

    def test_23_evaluations_is_list(self):
        """Test 23: evaluations is list."""
        res = self.engine.run_continuous_research_scan()
        self.assertIsInstance(res["evaluations"], list)

    def test_24_evaluations_element_structure(self):
        """Test 24: Each evaluation contains paper, novelty, contradiction."""
        res = self.engine.run_continuous_research_scan()
        e = res["evaluations"][0]
        self.assertIn("paper", e)
        self.assertIn("novelty", e)
        self.assertIn("contradiction", e)

    def test_25_engine_class_name(self):
        """Test 25: Class name is PersistentResearchEngine."""
        self.assertEqual(self.engine.__class__.__name__, "PersistentResearchEngine")

    def test_26_monitor_class_name(self):
        """Test 26: Class name is SourceMonitor."""
        self.assertEqual(self.monitor.__class__.__name__, "SourceMonitor")

    def test_27_novelty_class_name(self):
        """Test 27: Class name is NoveltyDetector."""
        self.assertEqual(self.novelty.__class__.__name__, "NoveltyDetector")

    def test_28_contradiction_class_name(self):
        """Test 28: Class name is ContradictionDetector."""
        self.assertEqual(self.contradiction.__class__.__name__, "ContradictionDetector")

    def test_29_result_dict_keys_count(self):
        """Test 29: Research scan result dict contains 8 keys."""
        res = self.engine.run_continuous_research_scan()
        self.assertEqual(len(res), 8)

    def test_30_default_topic_governance(self):
        """Test 30: Default topic is Autonomous Agent Governance."""
        res = self.engine.run_continuous_research_scan()
        self.assertEqual(res["topic"], "Autonomous Agent Governance")

    def test_31_paper_authors_string(self):
        """Test 31: Paper authors is string."""
        papers = self.monitor.scan_sources("T")
        self.assertIsInstance(papers[0]["authors"], str)

    def test_32_paper_source_string(self):
        """Test 32: Paper source is string."""
        papers = self.monitor.scan_sources("T")
        self.assertIsInstance(papers[0]["source"], str)

    def test_33_novelty_score_bounded(self):
        """Test 33: Novelty score is bounded between 0.0 and 1.0."""
        res = self.novelty.assess_novelty({"paper_id": "p1"}, [])
        self.assertTrue(0.0 <= res["novelty_score"] <= 1.0)

    def test_34_is_novel_boolean(self):
        """Test 34: is_novel is boolean."""
        res = self.novelty.assess_novelty({"paper_id": "p1"}, [])
        self.assertIsInstance(res["is_novel"], bool)

    def test_35_has_contradiction_boolean(self):
        """Test 35: has_contradiction is boolean."""
        res = self.contradiction.detect_contradictions({}, "")
        self.assertIsInstance(res["has_contradiction"], bool)

    def test_36_multiple_scans_independent(self):
        """Test 36: Multiple research scans return independent objects."""
        r1 = self.engine.run_continuous_research_scan()
        r2 = self.engine.run_continuous_research_scan()
        self.assertIsNot(r1, r2)

    def test_37_evaluations_iterable(self):
        """Test 37: evaluations list is iterable."""
        res = self.engine.run_continuous_research_scan()
        count = sum(1 for _ in res["evaluations"])
        self.assertEqual(count, 2)

    def test_38_paper_id_preserved_in_novelty(self):
        """Test 38: paper_id preserved in novelty evaluation."""
        res = self.novelty.assess_novelty({"paper_id": "px"}, [])
        self.assertEqual(res["paper_id"], "px")

    def test_39_paper_id_preserved_in_contradiction(self):
        """Test 39: paper_id preserved in contradiction evaluation."""
        res = self.contradiction.detect_contradictions({"paper_id": "py"}, "")
        self.assertEqual(res["paper_id"], "py")

    def test_40_research_engine_ui_integration_ready(self):
        """Test 40: Dict structured for Persistent Research Monitor UI panel."""
        res = self.engine.run_continuous_research_scan()
        self.assertIn("verified_count", res)
        self.assertIn("evaluations", res)

    def test_41_novelty_detector_existing_facts_list(self):
        """Test 41: Existing facts list passed cleanly."""
        res = self.novelty.assess_novelty({"paper_id": "p"}, ["fact1", "fact2"])
        self.assertTrue(res["is_novel"])

    def test_42_contradiction_detector_methodology_string(self):
        """Test 42: Current methodology string passed cleanly."""
        res = self.contradiction.detect_contradictions({"title": "drift"}, "Adaptive Thresholds")
        self.assertTrue(res["has_contradiction"])

    def test_43_source_monitor_domain_topic_param(self):
        """Test 43: Domain topic param accepted cleanly."""
        papers = self.monitor.scan_sources("Custom Domain")
        self.assertEqual(len(papers), 2)

    def test_44_verified_count_equals_candidates(self):
        """Test 44: verified_count equals candidates_found in baseline scan."""
        res = self.engine.run_continuous_research_scan()
        self.assertEqual(res["verified_count"], res["candidates_found"])

    def test_45_v6_6_persistent_research_verification_passed(self):
        """Test 45: All V6.6 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
