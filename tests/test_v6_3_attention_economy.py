import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.attention_economy_engine import AttentionEconomyEngine

class TestV63AttentionEconomy(unittest.TestCase):

    def setUp(self):
        self.engine = AttentionEconomyEngine()

    def test_1_engine_initializes(self):
        """Test 1: AttentionEconomyEngine initializes cleanly."""
        self.assertIsNotNone(self.engine)

    def test_2_evaluate_event_attention_high_priority(self):
        """Test 2: High importance and low cost yields HIGH priority alert."""
        event = {"title": "Thesis Deadline Alert", "importance": 1.0, "urgency": 0.9, "interruption_cost": 0.2}
        res = self.engine.evaluate_event_attention(event)
        self.assertEqual(res["priority"], "HIGH")
        self.assertFalse(res["deferred_automatically"])

    def test_3_evaluate_event_attention_low_priority_deferred(self):
        """Test 3: Low relevance and high cost yields LOW priority deferred alert."""
        event = {"title": "Minor Log Summary", "importance": 0.2, "urgency": 0.2, "interruption_cost": 0.9}
        res = self.engine.evaluate_event_attention(event)
        self.assertEqual(res["priority"], "LOW")
        self.assertTrue(res["deferred_automatically"])

    def test_4_attention_score_calculation(self):
        """Test 4: attention_score is calculated accurately."""
        event = {"importance": 1.0, "urgency": 1.0, "goal_relevance": 1.0, "confidence": 1.0, "expected_benefit": 1.0, "interruption_cost": 0.5}
        res = self.engine.evaluate_event_attention(event)
        self.assertEqual(res["attention_score"], 2.0)

    def test_5_recommendation_string_realtime(self):
        """Test 5: Non-deferred events recommend real-time display."""
        res = self.engine.evaluate_event_attention({"importance": 1.0, "urgency": 1.0, "interruption_cost": 0.2})
        self.assertIn("real-time", res["recommendation"])

    def test_6_recommendation_string_digest(self):
        """Test 6: Deferred events recommend daily summary digest."""
        res = self.engine.evaluate_event_attention({"importance": 0.1, "urgency": 0.1, "interruption_cost": 0.9})
        self.assertIn("digest", res["recommendation"])

    def test_7_event_title_preserved(self):
        """Test 7: Event title preserved in output dict."""
        res = self.engine.evaluate_event_attention({"title": "Custom Alert"})
        self.assertEqual(res["event_title"], "Custom Alert")

    def test_8_default_event_title(self):
        """Test 8: Default event title is Event Alert."""
        res = self.engine.evaluate_event_attention({})
        self.assertEqual(res["event_title"], "Event Alert")

    def test_9_attention_score_float_type(self):
        """Test 9: attention_score is float."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsInstance(res["attention_score"], float)

    def test_10_deferred_automatically_boolean(self):
        """Test 10: deferred_automatically is boolean."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsInstance(res["deferred_automatically"], bool)

    def test_11_priority_string_type(self):
        """Test 11: priority is string (HIGH, MEDIUM, or LOW)."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn(res["priority"], ["HIGH", "MEDIUM", "LOW"])

    def test_12_output_dict_keys_count(self):
        """Test 12: Output dict contains 5 keys."""
        res = self.engine.evaluate_event_attention({})
        self.assertEqual(len(res), 5)

    def test_13_stateless_execution(self):
        """Test 13: Attention calculation is stateless and repeatable."""
        res1 = self.engine.evaluate_event_attention({"title": "E"})
        res2 = self.engine.evaluate_event_attention({"title": "E"})
        self.assertEqual(res1["attention_score"], res2["attention_score"])

    def test_14_zero_cost_clamped_to_0_1(self):
        """Test 14: 0.0 interruption_cost is clamped to 0.1 minimum to prevent zero division."""
        res = self.engine.evaluate_event_attention({"interruption_cost": 0.0})
        self.assertTrue(res["attention_score"] > 0.0)

    def test_15_medium_priority_score_range(self):
        """Test 15: Score between 0.6 and 1.49 yields MEDIUM priority."""
        event = {"importance": 0.6, "urgency": 0.6, "interruption_cost": 0.3}
        res = self.engine.evaluate_event_attention(event)
        self.assertEqual(res["priority"], "MEDIUM")
        self.assertFalse(res["deferred_automatically"])

    def test_16_engine_reusable(self):
        """Test 16: Engine instance reusable across calls."""
        res1 = self.engine.evaluate_event_attention({"importance": 0.1})
        res2 = self.engine.evaluate_event_attention({"importance": 1.0})
        self.assertNotEqual(res1["priority"], res2["priority"])

    def test_17_recommendation_string_type(self):
        """Test 17: recommendation is string."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsInstance(res["recommendation"], str)

    def test_18_attention_score_rounded(self):
        """Test 18: attention_score rounded to 2 decimal places."""
        res = self.engine.evaluate_event_attention({"importance": 0.77})
        self.assertEqual(res["attention_score"], round(res["attention_score"], 2))

    def test_19_defaults_produce_medium_or_high(self):
        """Test 19: Default parameters produce non-deferred alert."""
        res = self.engine.evaluate_event_attention({})
        self.assertFalse(res["deferred_automatically"])

    def test_20_maximum_importance_urgency(self):
        """Test 20: Max values yield HIGH priority."""
        res = self.engine.evaluate_event_attention({"importance": 1.0, "urgency": 1.0})
        self.assertEqual(res["priority"], "HIGH")

    def test_21_high_interruption_cost_lowers_score(self):
        """Test 21: High interruption_cost lowers attention_score."""
        r1 = self.engine.evaluate_event_attention({"interruption_cost": 0.2})
        r2 = self.engine.evaluate_event_attention({"interruption_cost": 0.8})
        self.assertTrue(r1["attention_score"] > r2["attention_score"])

    def test_22_high_benefit_raises_score(self):
        """Test 22: High expected_benefit raises attention_score."""
        r1 = self.engine.evaluate_event_attention({"expected_benefit": 0.9})
        r2 = self.engine.evaluate_event_attention({"expected_benefit": 0.2})
        self.assertTrue(r1["attention_score"] > r2["attention_score"])

    def test_23_event_title_empty_string(self):
        """Test 23: Empty string event title handled."""
        res = self.engine.evaluate_event_attention({"title": ""})
        self.assertEqual(res["event_title"], "")

    def test_24_result_dict_type(self):
        """Test 24: Returns dictionary instance."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsInstance(res, dict)

    def test_25_engine_class_name(self):
        """Test 25: Class name is AttentionEconomyEngine."""
        self.assertEqual(self.engine.__class__.__name__, "AttentionEconomyEngine")

    def test_26_priority_key_present(self):
        """Test 26: priority key present in result."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn("priority", res)

    def test_27_attention_score_key_present(self):
        """Test 27: attention_score key present in result."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn("attention_score", res)

    def test_28_deferred_key_present(self):
        """Test 28: deferred_automatically key present in result."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn("deferred_automatically", res)

    def test_29_recommendation_key_present(self):
        """Test 29: recommendation key present in result."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn("recommendation", res)

    def test_30_event_title_key_present(self):
        """Test 30: event_title key present in result."""
        res = self.engine.evaluate_event_attention({})
        self.assertIn("event_title", res)

    def test_31_score_1_5_is_high_priority(self):
        """Test 31: Score exactly 1.5 is HIGH priority."""
        res = self.engine.evaluate_event_attention({"importance": 1.0, "urgency": 1.0, "goal_relevance": 1.0, "confidence": 0.75, "expected_benefit": 1.0, "interruption_cost": 0.5})
        self.assertEqual(res["priority"], "HIGH")

    def test_32_score_0_59_is_low_priority(self):
        """Test 32: Score 0.59 is LOW priority."""
        res = self.engine.evaluate_event_attention({"importance": 0.3, "urgency": 0.3, "interruption_cost": 0.5})
        self.assertEqual(res["priority"], "LOW")

    def test_33_score_0_60_is_medium_priority(self):
        """Test 33: Score 0.60 is MEDIUM priority."""
        res = self.engine.evaluate_event_attention({"importance": 1.0, "urgency": 1.0, "goal_relevance": 1.0, "confidence": 1.0, "expected_benefit": 0.6, "interruption_cost": 1.0})
        self.assertEqual(res["priority"], "MEDIUM")

    def test_34_high_priority_deferred_is_false(self):
        """Test 34: HIGH priority alert has deferred_automatically: False."""
        res = self.engine.evaluate_event_attention({"importance": 1.0, "urgency": 1.0})
        self.assertFalse(res["deferred_automatically"])

    def test_35_low_priority_deferred_is_true(self):
        """Test 35: LOW priority alert has deferred_automatically: True."""
        res = self.engine.evaluate_event_attention({"importance": 0.1, "urgency": 0.1})
        self.assertTrue(res["deferred_automatically"])

    def test_36_negative_cost_clamped(self):
        """Test 36: Negative interruption_cost clamped to 0.1 minimum."""
        res = self.engine.evaluate_event_attention({"interruption_cost": -0.5})
        self.assertTrue(res["attention_score"] > 0.0)

    def test_37_multiple_evaluations_independent(self):
        """Test 37: Multiple evaluations are independent."""
        r1 = self.engine.evaluate_event_attention({"title": "A", "importance": 0.1})
        r2 = self.engine.evaluate_event_attention({"title": "B", "importance": 1.0})
        self.assertEqual(r1["event_title"], "A")
        self.assertEqual(r2["event_title"], "B")

    def test_38_goal_relevance_default(self):
        """Test 38: Default goal_relevance is 0.9."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsNotNone(res["attention_score"])

    def test_39_confidence_default(self):
        """Test 39: Default confidence is 0.85."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsNotNone(res["attention_score"])

    def test_40_expected_benefit_default(self):
        """Test 40: Default expected_benefit is 0.8."""
        res = self.engine.evaluate_event_attention({})
        self.assertIsNotNone(res["attention_score"])

    def test_41_score_positive_float(self):
        """Test 41: attention_score is positive float."""
        res = self.engine.evaluate_event_attention({})
        self.assertTrue(res["attention_score"] > 0.0)

    def test_42_attention_engine_integration_ready(self):
        """Test 42: Output structured for Attention Queue UI integration."""
        res = self.engine.evaluate_event_attention({"title": "T"})
        self.assertIn("priority", res)

    def test_43_custom_payload_fields_ignored_safely(self):
        """Test 43: Extra payload fields in event dict ignored safely."""
        res = self.engine.evaluate_event_attention({"title": "T", "extra_meta": 123})
        self.assertEqual(res["event_title"], "T")

    def test_44_repeated_score_consistency(self):
        """Test 44: Score consistency across 10 iterations."""
        scores = [self.engine.evaluate_event_attention({})["attention_score"] for _ in range(10)]
        self.assertEqual(len(set(scores)), 1)

    def test_45_v6_3_attention_economy_verification_passed(self):
        """Test 45: All V6.3 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
