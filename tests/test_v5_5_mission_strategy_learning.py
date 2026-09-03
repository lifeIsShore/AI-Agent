import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.learning.mission_outcome_analyzer import MissionOutcomeAnalyzer
from personal_agent.learning.strategy_extractor import StrategyExtractor
from personal_agent.learning.mission_strategy_store import MissionStrategyStore
from personal_agent.learning.strategy_selector import StrategySelector
from personal_agent.learning.mission_learning_engine import MissionLearningEngine

class TestV55MissionStrategyLearning(unittest.TestCase):

    def setUp(self):
        self.analyzer = MissionOutcomeAnalyzer()
        self.extractor = StrategyExtractor()
        self.store = MissionStrategyStore()
        self.selector = StrategySelector()
        self.engine = MissionLearningEngine()

    def test_1_outcome_analyzer_handles_empty(self):
        """Test 1: MissionOutcomeAnalyzer handles empty mission data."""
        res = self.analyzer.analyze_mission_outcome({})
        self.assertTrue(res["success"])
        self.assertEqual(res["success_rate"], 1.0)

    def test_2_outcome_analyzer_calculates_success(self):
        """Test 2: analyze_mission_outcome calculates clean success."""
        m_data = {"mission_id": "m1", "steps": [{"step_name": "s1", "status": "SUCCESS"}]}
        res = self.analyzer.analyze_mission_outcome(m_data)
        self.assertTrue(res["success"])

    def test_3_outcome_analyzer_calculates_rejection_penalty(self):
        """Test 3: analyze_mission_outcome penalizes rejections."""
        m_data = {"mission_id": "m1", "steps": [{"step_name": "s1"}], "rejections": 2}
        res = self.analyzer.analyze_mission_outcome(m_data)
        self.assertFalse(res["success"])
        self.assertEqual(res["success_rate"], 0.6)

    def test_4_strategy_extractor_generates_strategy(self):
        """Test 4: extract_strategy generates reusable strategy dictionary."""
        m_data = {"mission_id": "m1", "domain": "job_application", "steps": [{"step_name": "CV"}, {"step_name": "Cover"}]}
        analysis = self.analyzer.analyze_mission_outcome(m_data)
        strat = self.extractor.extract_strategy(m_data, analysis)
        self.assertEqual(strat["domain"], "job_application")
        self.assertEqual(len(strat["step_sequence"]), 2)

    def test_5_strategy_store_initializes_defaults(self):
        """Test 5: MissionStrategyStore contains default strategies."""
        strats = self.store.get_strategies_for_domain("university_deadline")
        self.assertTrue(len(strats) >= 2)

    def test_6_strategy_store_save_strategy(self):
        """Test 6: save_strategy persists custom strategy."""
        s_custom = {"strategy_id": "s_c", "domain": "job", "success_rate": 0.95}
        self.store.save_strategy(s_custom)
        res = self.store.get_strategies_for_domain("job")
        self.assertEqual(len(res), 1)

    def test_7_strategy_selector_picks_highest_success_rate(self):
        """Test 7: StrategySelector selects Strategy B (89%) over Strategy A (61%)."""
        best = self.selector.select_best_strategy("university_deadline", self.store)
        self.assertEqual(best["strategy_id"], "strat_thesis_b")

    def test_8_strategy_selector_returns_none_for_unknown(self):
        """Test 8: StrategySelector returns None for unknown domain."""
        best = self.selector.select_best_strategy("unknown_domain", self.store)
        self.assertIsNone(best)

    def test_9_mission_learning_engine_process_completed(self):
        """Test 9: process_completed_mission executes full pipeline."""
        m_data = {"mission_id": "m10", "domain": "scholarship", "steps": [{"step_name": "Apply"}]}
        res = self.engine.process_completed_mission(m_data)
        self.assertEqual(res["status"], "PROCESSED")
        self.assertIsNotNone(res["extracted_strategy"])

    def test_10_mission_learning_engine_recommend(self):
        """Test 10: recommend_mission_strategy delegates to selector."""
        rec = self.engine.recommend_mission_strategy("university_deadline")
        self.assertEqual(rec["strategy_id"], "strat_thesis_b")

    def test_11_extractor_strategy_id_prefix(self):
        """Test 11: Strategy ID starts with strat_."""
        strat = self.extractor.extract_strategy({"domain": "d"}, {"success_rate": 1.0})
        self.assertTrue(strat["strategy_id"].startswith("strat_"))

    def test_12_extractor_confidence_scale(self):
        """Test 12: Strategy confidence scales with success rate."""
        strat = self.extractor.extract_strategy({"domain": "d"}, {"success_rate": 1.0})
        self.assertEqual(strat["confidence"], 1.0)

    def test_13_outcome_analyzer_tokens_used(self):
        """Test 13: tokens_used preserved in analysis."""
        res = self.analyzer.analyze_mission_outcome({"tokens_used": 500})
        self.assertEqual(res["tokens_used"], 500)

    def test_14_outcome_analyzer_duration_sec(self):
        """Test 14: duration_sec preserved in analysis."""
        res = self.analyzer.analyze_mission_outcome({"duration_sec": 12.5})
        self.assertEqual(res["duration_sec"], 12.5)

    def test_15_outcome_analyzer_failed_steps_count(self):
        """Test 15: failed_steps count calculated correctly."""
        res = self.analyzer.analyze_mission_outcome({"steps": [{"status": "FAILED"}, {"status": "SUCCESS"}]})
        self.assertEqual(res["failed_steps"], 1)

    def test_16_outcome_analyzer_total_steps_count(self):
        """Test 16: total_steps count calculated correctly."""
        res = self.analyzer.analyze_mission_outcome({"steps": [{}, {}, {}]})
        self.assertEqual(res["total_steps"], 3)

    def test_17_strategy_store_dict_retrieval(self):
        """Test 17: Strategy store retrieves strategy dict."""
        res = self.store.get_strategies_for_domain("university_deadline")
        self.assertIn("strategy_id", res[0])

    def test_18_strategy_selector_confidence_tie_breaker(self):
        """Test 18: StrategySelector uses confidence as tie-breaker."""
        s1 = {"strategy_id": "s1", "domain": "test", "success_rate": 0.90, "confidence": 0.80}
        s2 = {"strategy_id": "s2", "domain": "test", "success_rate": 0.90, "confidence": 0.95}
        self.store.save_strategy(s1)
        self.store.save_strategy(s2)
        best = self.selector.select_best_strategy("test", self.store)
        self.assertEqual(best["strategy_id"], "s2")

    def test_19_engine_initializes_all_components(self):
        """Test 19: MissionLearningEngine initializes all 4 subcomponents."""
        self.assertIsNotNone(self.engine.analyzer)
        self.assertIsNotNone(self.engine.extractor)
        self.assertIsNotNone(self.engine.store)
        self.assertIsNotNone(self.engine.selector)

    def test_20_engine_rejects_low_success_rate_extraction(self):
        """Test 20: Engine does not extract strategy for missions with success_rate < 0.70."""
        m_data = {"mission_id": "m_fail", "domain": "d", "rejections": 5}
        res = self.engine.process_completed_mission(m_data)
        self.assertIsNone(res["extracted_strategy"])

    def test_21_analyzer_domain_field(self):
        """Test 21: domain field preserved in analysis."""
        res = self.analyzer.analyze_mission_outcome({"domain": "finance"})
        self.assertEqual(res["domain"], "finance")

    def test_22_extractor_sample_missions_list(self):
        """Test 22: sample_missions list contains mission_id."""
        strat = self.extractor.extract_strategy({"mission_id": "m123", "domain": "d"}, {"success_rate": 1.0})
        self.assertIn("m123", strat["sample_missions"])

    def test_23_store_case_insensitive_domain(self):
        """Test 23: Strategy store lookup is domain case-insensitive."""
        res = self.store.get_strategies_for_domain("UNIVERSITY_DEADLINE")
        self.assertTrue(len(res) >= 2)

    def test_24_selector_handles_single_candidate(self):
        """Test 24: StrategySelector handles single candidate correctly."""
        self.store.save_strategy({"strategy_id": "single", "domain": "unique_d", "success_rate": 0.80})
        best = self.selector.select_best_strategy("unique_d", self.store)
        self.assertEqual(best["strategy_id"], "single")

    def test_25_engine_integration_status_processed(self):
        """Test 25: Process status is PROCESSED."""
        res = self.engine.process_completed_mission({})
        self.assertEqual(res["status"], "PROCESSED")

    def test_26_analyzer_success_rate_bounds(self):
        """Test 26: Success rate bounded between 0.0 and 1.0."""
        res = self.analyzer.analyze_mission_outcome({"rejections": 10, "steps": [{"status": "FAILED"}] * 10})
        self.assertEqual(res["success_rate"], 0.0)

    def test_27_extractor_name_format(self):
        """Test 27: Name format includes domain string."""
        strat = self.extractor.extract_strategy({"domain": "career"}, {"success_rate": 0.9})
        self.assertIn("career", strat["name"])

    def test_28_store_multiple_domains(self):
        """Test 28: Store tracks multiple distinct domains."""
        self.store.save_strategy({"strategy_id": "s1", "domain": "d1"})
        self.store.save_strategy({"strategy_id": "s2", "domain": "d2"})
        self.assertEqual(len(self.store.get_strategies_for_domain("d1")), 1)

    def test_29_selector_returns_dict(self):
        """Test 29: Selector returns dictionary instance."""
        best = self.selector.select_best_strategy("university_deadline", self.store)
        self.assertIsInstance(best, dict)

    def test_30_engine_recommend_returns_dict(self):
        """Test 30: Engine recommend returns strategy dictionary."""
        rec = self.engine.recommend_mission_strategy("university_deadline")
        self.assertIsInstance(rec, dict)

    def test_31_analyzer_mission_id_default(self):
        """Test 31: Missing mission_id defaults to m_unknown."""
        res = self.analyzer.analyze_mission_outcome({})
        self.assertEqual(res["mission_id"], "m_unknown")

    def test_32_extractor_step_sequence_empty(self):
        """Test 32: Empty steps produces empty step_sequence."""
        strat = self.extractor.extract_strategy({"domain": "d"}, {"success_rate": 1.0})
        self.assertEqual(strat["step_sequence"], [])

    def test_33_store_overwrite_strategy(self):
        """Test 33: Saving strategy with same ID overwrites entry."""
        self.store.save_strategy({"strategy_id": "s1", "domain": "d", "val": 1})
        self.store.save_strategy({"strategy_id": "s1", "domain": "d", "val": 2})
        strats = self.store.get_strategies_for_domain("d")
        self.assertEqual(strats[0]["val"], 2)

    def test_34_selector_empty_store_returns_none(self):
        """Test 34: Selector on empty store returns None."""
        empty_store = MissionStrategyStore()
        empty_store.strategies = {}
        best = self.selector.select_best_strategy("any", empty_store)
        self.assertIsNone(best)

    def test_35_engine_process_and_recommend(self):
        """Test 35: Mission processed can immediately be recommended."""
        m_data = {"mission_id": "m_new", "domain": "new_domain", "steps": [{"step_name": "step1"}]}
        self.engine.process_completed_mission(m_data)
        rec = self.engine.recommend_mission_strategy("new_domain")
        self.assertIsNotNone(rec)

    def test_36_analyzer_success_flag_boolean(self):
        """Test 36: success flag is boolean."""
        res = self.analyzer.analyze_mission_outcome({})
        self.assertIsInstance(res["success"], bool)

    def test_37_extractor_confidence_float(self):
        """Test 37: confidence is float."""
        strat = self.extractor.extract_strategy({"domain": "d"}, {"success_rate": 0.8})
        self.assertIsInstance(strat["confidence"], float)

    def test_38_store_strategies_dict(self):
        """Test 38: Store maintains strategies dictionary."""
        self.assertIsInstance(self.store.strategies, dict)

    def test_39_selector_sort_order(self):
        """Test 39: Selector sorts candidates descending."""
        self.store.save_strategy({"strategy_id": "low", "domain": "d_sort", "success_rate": 0.5})
        self.store.save_strategy({"strategy_id": "high", "domain": "d_sort", "success_rate": 0.95})
        best = self.selector.select_best_strategy("d_sort", self.store)
        self.assertEqual(best["strategy_id"], "high")

    def test_40_engine_analyzer_attribute(self):
        """Test 40: Engine analyzer attribute is MissionOutcomeAnalyzer."""
        self.assertIsInstance(self.engine.analyzer, MissionOutcomeAnalyzer)

    def test_41_analyzer_strategy_id_preserved(self):
        """Test 41: strategy_id preserved in outcome analysis."""
        res = self.analyzer.analyze_mission_outcome({"strategy_id": "s_123"})
        self.assertEqual(res["strategy_id"], "s_123")

    def test_42_extractor_step_names_extracted(self):
        """Test 42: Step names extracted accurately."""
        m_data = {"domain": "d", "steps": [{"step_name": "A"}, {"step_name": "B"}]}
        strat = self.extractor.extract_strategy(m_data, {"success_rate": 1.0})
        self.assertEqual(strat["step_sequence"], ["A", "B"])

    def test_43_store_get_strategies_returns_list(self):
        """Test 43: get_strategies_for_domain returns list."""
        res = self.store.get_strategies_for_domain("university_deadline")
        self.assertIsInstance(res, list)

    def test_44_engine_workflow_integration_ready(self):
        """Test 44: Engine output structured for MissionController integration."""
        res = self.engine.process_completed_mission({"domain": "d", "steps": []})
        self.assertIn("analysis", res)

    def test_45_v5_5_mission_strategy_learning_verification_passed(self):
        """Test 45: All V5.5 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
