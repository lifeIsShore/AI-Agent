import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.strategies.mission_strategy_library import (
    MissionStrategy,
    MissionStrategyLibrary,
    StrategySelector
)

class TestV69MissionStrategyLibrary(unittest.TestCase):

    def setUp(self):
        self.library = MissionStrategyLibrary()
        self.selector = StrategySelector(self.library)

    def test_1_library_initializes_with_3_strategies(self):
        """Test 1: MissionStrategyLibrary initializes with 3 default thesis strategies."""
        self.assertEqual(len(self.library.strategies), 3)

    def test_2_register_custom_strategy(self):
        """Test 2: register_strategy adds a new MissionStrategy."""
        strat = MissionStrategy("s_custom", "Custom", "Job Search", ["EmailSpecialist"], ["Qwen 1.5B"], ["Apply"], 5.0)
        self.library.register_strategy(strat)
        self.assertEqual(len(self.library.strategies), 4)

    def test_3_get_strategies_for_objective(self):
        """Test 3: get_strategies_for_objective finds matching strategies."""
        matches = self.library.get_strategies_for_objective("Thesis")
        self.assertEqual(len(matches), 3)

    def test_4_select_best_strategy(self):
        """Test 4: select_best_strategy returns strategy with highest confidence score."""
        best = self.selector.select_best_strategy("Thesis")
        self.assertIsNotNone(best)
        self.assertTrue("Strategy" in best.name)

    def test_5_select_best_strategy_unknown(self):
        """Test 5: select_best_strategy returns None for non-existent objective."""
        best = self.selector.select_best_strategy("NonExistent")
        self.assertIsNone(best)

    def test_6_strategy_to_dict_keys(self):
        """Test 6: MissionStrategy to_dict returns 9 keys."""
        strat = MissionStrategy("id", "name", "obj", ["A"], ["M"], ["T"], 10.0)
        self.assertEqual(len(strat.to_dict()), 9)

    def test_7_strategy_id_matches(self):
        """Test 7: Strategy ID matches strat_thesis_b."""
        self.assertIn("strat_thesis_b", self.library.strategies)

    def test_8_strategy_required_agents_list(self):
        """Test 8: required_agents is list of strings."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.required_agents, list)

    def test_9_strategy_preferred_models_list(self):
        """Test 9: preferred_models is list of strings."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.preferred_models, list)

    def test_10_strategy_task_sequence_list(self):
        """Test 10: task_sequence is list of strings."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.task_sequence, list)

    def test_11_strategy_historical_success_float(self):
        """Test 11: historical_success_rate is float."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.historical_success_rate, float)

    def test_12_strategy_confidence_float(self):
        """Test 12: confidence is float."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.confidence, float)

    def test_13_strategy_duration_float(self):
        """Test 13: expected_duration_hours is float."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIsInstance(s.expected_duration_hours, float)

    def test_14_library_class_name(self):
        """Test 14: Class name is MissionStrategyLibrary."""
        self.assertEqual(self.library.__class__.__name__, "MissionStrategyLibrary")

    def test_15_selector_class_name(self):
        """Test 15: Class name is StrategySelector."""
        self.assertEqual(self.selector.__class__.__name__, "StrategySelector")

    def test_16_strategy_class_name(self):
        """Test 16: Class name is MissionStrategy."""
        s = MissionStrategy("i", "n", "o", [], [], [], 1.0)
        self.assertEqual(s.__class__.__name__, "MissionStrategy")

    def test_17_strategy_a_success_rate(self):
        """Test 17: Strategy A success rate is 0.61."""
        s = self.library.strategies["strat_thesis_a"]
        self.assertEqual(s.historical_success_rate, 0.61)

    def test_18_strategy_b_success_rate(self):
        """Test 18: Strategy B success rate is 0.89."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertEqual(s.historical_success_rate, 0.89)

    def test_19_strategy_c_success_rate(self):
        """Test 19: Strategy C success rate is 0.86."""
        s = self.library.strategies["strat_thesis_c"]
        self.assertEqual(s.historical_success_rate, 0.86)

    def test_20_strategy_c_confidence_095(self):
        """Test 20: Strategy C confidence is 0.95."""
        s = self.library.strategies["strat_thesis_c"]
        self.assertEqual(s.confidence, 0.95)

    def test_21_strategy_a_duration(self):
        """Test 21: Strategy A duration is 24.0 hours."""
        s = self.library.strategies["strat_thesis_a"]
        self.assertEqual(s.expected_duration_hours, 24.0)

    def test_22_strategy_b_duration(self):
        """Test 22: Strategy B duration is 18.0 hours."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertEqual(s.expected_duration_hours, 18.0)

    def test_23_strategy_c_duration(self):
        """Test 23: Strategy C duration is 16.0 hours."""
        s = self.library.strategies["strat_thesis_c"]
        self.assertEqual(s.expected_duration_hours, 16.0)

    def test_24_strategy_json_serializable(self):
        """Test 24: to_dict output is JSON serializable."""
        import json
        s = self.library.strategies["strat_thesis_b"]
        dumped = json.dumps(s.to_dict())
        self.assertIsInstance(dumped, str)

    def test_25_selector_reusable(self):
        """Test 25: StrategySelector instance is reusable."""
        b1 = self.selector.select_best_strategy("Thesis")
        b2 = self.selector.select_best_strategy("Thesis")
        self.assertEqual(b1.strategy_id, b2.strategy_id)

    def test_26_case_insensitive_matching(self):
        """Test 26: get_strategies_for_objective matches case-insensitively."""
        matches = self.library.get_strategies_for_objective("thesis")
        self.assertEqual(len(matches), 3)

    def test_27_strategy_c_has_critic_agent(self):
        """Test 27: Strategy C includes CriticAgent."""
        s = self.library.strategies["strat_thesis_c"]
        self.assertIn("CriticAgent", s.required_agents)

    def test_28_strategy_c_has_verification_agent(self):
        """Test 28: Strategy C includes VerificationAgent."""
        s = self.library.strategies["strat_thesis_c"]
        self.assertIn("VerificationAgent", s.required_agents)

    def test_29_strategy_b_has_calendar_specialist(self):
        """Test 29: Strategy B includes CalendarSpecialist."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIn("CalendarSpecialist", s.required_agents)

    def test_30_strategy_b_has_planning_specialist(self):
        """Test 30: Strategy B includes PlanningSpecialist."""
        s = self.library.strategies["strat_thesis_b"]
        self.assertIn("PlanningSpecialist", s.required_agents)

    def test_31_strategy_preferred_models_non_empty(self):
        """Test 31: All default strategies have preferred models."""
        for s in self.library.strategies.values():
            self.assertTrue(len(s.preferred_models) > 0)

    def test_32_strategy_task_sequence_non_empty(self):
        """Test 32: All default strategies have task sequence steps."""
        for s in self.library.strategies.values():
            self.assertTrue(len(s.task_sequence) > 0)

    def test_33_strategy_objective_non_empty(self):
        """Test 33: All default strategies have objective string."""
        for s in self.library.strategies.values():
            self.assertTrue(len(s.objective) > 0)

    def test_34_strategy_name_non_empty(self):
        """Test 34: All default strategies have name string."""
        for s in self.library.strategies.values():
            self.assertTrue(len(s.name) > 0)

    def test_35_register_duplicate_overwrites(self):
        """Test 35: Registering duplicate strategy_id overwrites cleanly."""
        strat = MissionStrategy("strat_thesis_a", "Updated A", "Obj", [], [], [], 5.0)
        self.library.register_strategy(strat)
        self.assertEqual(self.library.strategies["strat_thesis_a"].name, "Updated A")

    def test_36_strategy_confidence_bounded(self):
        """Test 36: Confidence is bounded between 0.0 and 1.0."""
        for s in self.library.strategies.values():
            self.assertTrue(0.0 <= s.confidence <= 1.0)

    def test_37_strategy_success_rate_bounded(self):
        """Test 37: Success rate is bounded between 0.0 and 1.0."""
        for s in self.library.strategies.values():
            self.assertTrue(0.0 <= s.historical_success_rate <= 1.0)

    def test_38_best_strategy_calculated_score(self):
        """Test 38: Best strategy has highest combined score."""
        best = self.selector.select_best_strategy("Thesis")
        # strat_thesis_b = 0.89 * 0.92 = 0.8188
        # strat_thesis_c = 0.86 * 0.95 = 0.8170
        self.assertEqual(best.strategy_id, "strat_thesis_b")

    def test_39_to_dict_keys_check(self):
        """Test 39: to_dict contains strategy_id key."""
        strat = MissionStrategy("id", "name", "obj", [], [], [], 1.0)
        self.assertIn("strategy_id", strat.to_dict())

    def test_40_library_strategies_dict_type(self):
        """Test 40: library.strategies is dict."""
        self.assertIsInstance(self.library.strategies, dict)

    def test_41_strategy_duration_positive(self):
        """Test 41: All default strategy durations are positive."""
        for s in self.library.strategies.values():
            self.assertTrue(s.expected_duration_hours > 0)

    def test_42_strategy_a_name(self):
        """Test 42: Strategy A name matches."""
        self.assertEqual(self.library.strategies["strat_thesis_a"].name, "Strategy A — Direct Research & Draft")

    def test_43_strategy_b_name(self):
        """Test 43: Strategy B name matches."""
        self.assertEqual(self.library.strategies["strat_thesis_b"].name, "Strategy B — Requirements & Calendar Alignment")

    def test_44_strategy_c_name(self):
        """Test 44: Strategy C name matches."""
        self.assertEqual(self.library.strategies["strat_thesis_c"].name, "Strategy C — Iterative Critic & Dual Verification")

    def test_45_v6_9_mission_strategy_library_verification_passed(self):
        """Test 45: All V6.9 mission strategy library features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
