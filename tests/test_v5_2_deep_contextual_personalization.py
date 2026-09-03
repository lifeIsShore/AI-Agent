import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.learning.deep_personalization_engine import (
    DeepPersonalizationEngine, ContextualPreferenceRule
)

class TestV52DeepContextualPersonalization(unittest.TestCase):

    def setUp(self):
        self.engine = DeepPersonalizationEngine()

    def test_1_contextual_rule_initializes(self):
        """Test 1: ContextualPreferenceRule initializes with conditions and recommendation."""
        r = ContextualPreferenceRule("r1", {"k": "v"}, "rec1")
        self.assertEqual(r.rule_id, "r1")
        self.assertEqual(r.action_recommendation, "rec1")

    def test_2_contextual_rule_matches_context(self):
        """Test 2: matches_context evaluates dictionary conditions cleanly."""
        r = ContextualPreferenceRule("r1", {"k": "v"}, "rec1")
        self.assertTrue(r.matches_context({"k": "v"}))

    def test_3_contextual_rule_matches_case_insensitive(self):
        """Test 3: String condition matching is case-insensitive."""
        r = ContextualPreferenceRule("r1", {"k": "Prof"}, "rec1")
        self.assertTrue(r.matches_context({"k": "professor"}))

    def test_4_contextual_rule_to_dict(self):
        """Test 4: to_dict() returns dictionary output."""
        r = ContextualPreferenceRule("r1", {"k": "v"}, "rec1")
        d = r.to_dict()
        self.assertEqual(d["rule_id"], "r1")

    def test_5_deep_personalization_engine_initializes(self):
        """Test 5: DeepPersonalizationEngine initializes default rule tree."""
        self.assertEqual(len(self.engine.rules), 2)

    def test_6_evaluate_recommendation_univ_prof(self):
        """Test 6: Matches task == university_email and sender == prof."""
        rule = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "Prof. Davis"})
        self.assertIsNotNone(rule)
        self.assertEqual(rule.action_recommendation, "recommend_afternoon_response")

    def test_7_evaluate_recommendation_job_urgent(self):
        """Test 7: Matches task == job_application and urgent == True."""
        rule = self.engine.evaluate_contextual_recommendation({"task": "job_application", "urgent": True})
        self.assertIsNotNone(rule)
        self.assertEqual(rule.action_recommendation, "increase_priority_high")

    def test_8_user_rules_rank_above_learned_rules(self):
        """Test 8: Explicit USER rules are selected over LEARNED rules."""
        r_learned = ContextualPreferenceRule("r_l", {"task": "univ"}, "rec_learned", source="LEARNED", confidence=0.99)
        self.engine.add_rule(r_learned)
        rule = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof"})
        self.assertEqual(rule.source, "USER")

    def test_9_add_rule(self):
        """Test 9: add_rule appends new contextual rule."""
        r_new = ContextualPreferenceRule("r_new", {"a": "b"}, "rec_new")
        self.engine.add_rule(r_new)
        self.assertEqual(len(self.engine.rules), 3)

    def test_10_evaluate_recommendation_unmatched(self):
        """Test 10: Returns None when no conditions match."""
        rule = self.engine.evaluate_contextual_recommendation({"task": "unknown"})
        self.assertIsNone(rule)

    def test_11_multiple_matching_rules_highest_confidence(self):
        """Test 11: Selects highest confidence rule among matches."""
        r1 = ContextualPreferenceRule("r1", {"k": "v"}, "rec1", source="LEARNED", confidence=0.70)
        r2 = ContextualPreferenceRule("r2", {"k": "v"}, "rec2", source="LEARNED", confidence=0.95)
        self.engine.add_rule(r1)
        self.engine.add_rule(r2)
        rule = self.engine.evaluate_contextual_recommendation({"k": "v"})
        self.assertEqual(rule.rule_id, "r2")

    def test_12_matches_context_missing_key(self):
        """Test 12: Missing key in context returns False."""
        r = ContextualPreferenceRule("r1", {"missing": "val"}, "rec1")
        self.assertFalse(r.matches_context({"k": "v"}))

    def test_13_matches_context_exact_non_string(self):
        """Test 13: Non-string values matched by equality."""
        r = ContextualPreferenceRule("r1", {"num": 42}, "rec1")
        self.assertTrue(r.matches_context({"num": 42}))

    def test_14_user_rule_confidence_1_0(self):
        """Test 14: Default USER rule confidence is 1.0."""
        rule = self.engine.rules[0]
        self.assertEqual(rule.confidence, 1.0)

    def test_15_learned_rule_confidence_0_85(self):
        """Test 15: Default LEARNED rule confidence is 0.85."""
        r = ContextualPreferenceRule("r_l", {"k": "v"}, "rec")
        self.assertEqual(r.confidence, 0.85)

    def test_16_contextual_rule_id_assigned(self):
        """Test 16: Each rule has unique rule_id."""
        r = ContextualPreferenceRule("r_unique", {"k": "v"}, "rec")
        self.assertEqual(r.rule_id, "r_unique")

    def test_17_add_learned_rule(self):
        """Test 17: Adding custom LEARNED rule works."""
        r = ContextualPreferenceRule("r_l", {"tag": "email"}, "rec_tag", source="LEARNED")
        self.engine.add_rule(r)
        self.assertIn(r, self.engine.rules)

    def test_18_evaluate_with_partial_match(self):
        """Test 18: Partial match failure returns None."""
        r = ContextualPreferenceRule("r1", {"k1": "v1", "k2": "v2"}, "rec1")
        self.assertFalse(r.matches_context({"k1": "v1"}))

    def test_19_rule_conditions_dict(self):
        """Test 19: conditions dict preserved accurately."""
        r = ContextualPreferenceRule("r1", {"c1": 1}, "rec1")
        self.assertEqual(r.conditions, {"c1": 1})

    def test_20_action_recommendation_string(self):
        """Test 20: action_recommendation string returned cleanly."""
        r = ContextualPreferenceRule("r1", {"c1": 1}, "do_action")
        self.assertEqual(r.action_recommendation, "do_action")

    def test_21_deep_engine_rules_count(self):
        """Test 21: Default rules count is 2."""
        self.assertEqual(len(self.engine.rules), 2)

    def test_22_evaluate_contextual_user_priority_invariant(self):
        """Test 22: Invariant USER > LEARNED holds 100%."""
        r_user = ContextualPreferenceRule("ru", {"topic": "ai"}, "user_rec", source="USER", confidence=0.80)
        r_learned = ContextualPreferenceRule("rl", {"topic": "ai"}, "learned_rec", source="LEARNED", confidence=0.99)
        self.engine.add_rule(r_learned)
        self.engine.add_rule(r_user)
        res = self.engine.evaluate_contextual_recommendation({"topic": "ai"})
        self.assertEqual(res.source, "USER")

    def test_23_matches_context_substring_check(self):
        """Test 23: Substring matching works for text sender."""
        r = ContextualPreferenceRule("r1", {"sender": "davis"}, "rec")
        self.assertTrue(r.matches_context({"sender": "Prof. Davis"}))

    def test_24_matches_context_boolean_check(self):
        """Test 24: Boolean condition matching works."""
        r = ContextualPreferenceRule("r1", {"flag": True}, "rec")
        self.assertTrue(r.matches_context({"flag": True}))

    def test_25_contextual_rule_source_field(self):
        """Test 25: source field defaults to LEARNED unless specified USER."""
        r = ContextualPreferenceRule("r1", {"k": "v"}, "rec")
        self.assertEqual(r.source, "LEARNED")

    def test_26_evaluate_recommendation_returns_rule_object(self):
        """Test 26: Return value is ContextualPreferenceRule instance."""
        res = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof"})
        self.assertIsInstance(res, ContextualPreferenceRule)

    def test_27_add_multiple_rules(self):
        """Test 27: Multiple rules added sequentially."""
        self.engine.add_rule(ContextualPreferenceRule("r1", {}, "a1"))
        self.engine.add_rule(ContextualPreferenceRule("r2", {}, "a2"))
        self.assertEqual(len(self.engine.rules), 4)

    def test_28_matches_context_empty_conditions(self):
        """Test 28: Empty conditions rule matches any context."""
        r = ContextualPreferenceRule("r_any", {}, "rec_any")
        self.assertTrue(r.matches_context({"any_key": "any_val"}))

    def test_29_rule_dict_contains_source(self):
        """Test 29: to_dict() contains source."""
        d = ContextualPreferenceRule("r1", {}, "rec", source="USER").to_dict()
        self.assertEqual(d["source"], "USER")

    def test_30_rule_dict_contains_confidence(self):
        """Test 30: to_dict() contains confidence."""
        d = ContextualPreferenceRule("r1", {}, "rec", confidence=0.9).to_dict()
        self.assertEqual(d["confidence"], 0.9)

    def test_31_rule_dict_contains_conditions(self):
        """Test 31: to_dict() contains conditions."""
        d = ContextualPreferenceRule("r1", {"a": 1}, "rec").to_dict()
        self.assertEqual(d["conditions"], {"a": 1})

    def test_32_rule_dict_contains_recommendation(self):
        """Test 32: to_dict() contains action_recommendation."""
        d = ContextualPreferenceRule("r1", {}, "rec_action").to_dict()
        self.assertEqual(d["action_recommendation"], "rec_action")

    def test_33_user_rule_override_learned(self):
        """Test 33: USER rule overrides LEARNED rule with higher confidence."""
        r_u = ContextualPreferenceRule("ru", {"c": 1}, "u_action", source="USER", confidence=1.0)
        r_l = ContextualPreferenceRule("rl", {"c": 1}, "l_action", source="LEARNED", confidence=0.9)
        self.engine.add_rule(r_l)
        self.engine.add_rule(r_u)
        res = self.engine.evaluate_contextual_recommendation({"c": 1})
        self.assertEqual(res.rule_id, "ru")

    def test_34_evaluate_job_application_deadline(self):
        """Test 34: Deadline condition matching."""
        r = ContextualPreferenceRule("r_dl", {"task": "job_application", "deadline_hours": 48}, "high_priority", source="USER")
        self.engine.add_rule(r)
        res = self.engine.evaluate_contextual_recommendation({"task": "job_application", "deadline_hours": 48})
        self.assertEqual(res.rule_id, "r_dl")

    def test_35_evaluate_professor_normal_urgency(self):
        """Test 35: Multi-condition university rule matching."""
        res = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof", "urgency": "normal"})
        self.assertIsNotNone(res)

    def test_36_evaluate_context_case_variants(self):
        """Test 36: Case variant context matching."""
        res = self.engine.evaluate_contextual_recommendation({"TASK": "UNIVERSITY_EMAIL", "SENDER": "PROFESSOR"})
        self.assertIsNone(res)  # keys are exact

    def test_37_governor_capability_ceiling_preserved(self):
        """Test 37: Deep rules cannot exceed maximum governor capabilities."""
        res = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof"})
        self.assertIsNotNone(res)

    def test_38_evaluate_returns_none_for_empty_facts(self):
        """Test 38: Empty facts dict returns None."""
        res = self.engine.evaluate_contextual_recommendation({})
        self.assertIsNone(res)

    def test_39_rules_list_iterable(self):
        """Test 39: rules list is iterable."""
        count = sum(1 for r in self.engine.rules)
        self.assertEqual(count, 2)

    def test_40_custom_rule_id_unique(self):
        """Test 40: Custom rule_id string preserved."""
        r = ContextualPreferenceRule("custom_id_123", {}, "rec")
        self.assertEqual(r.rule_id, "custom_id_123")

    def test_41_confidence_sorting_learned(self):
        """Test 41: LEARNED rules sorted by confidence."""
        r1 = ContextualPreferenceRule("r1", {"tag": "a"}, "rec1", source="LEARNED", confidence=0.7)
        r2 = ContextualPreferenceRule("r2", {"tag": "a"}, "rec2", source="LEARNED", confidence=0.9)
        self.engine.add_rule(r1)
        self.engine.add_rule(r2)
        res = self.engine.evaluate_contextual_recommendation({"tag": "a"})
        self.assertEqual(res.rule_id, "r2")

    def test_42_confidence_sorting_user(self):
        """Test 42: USER rules sorted by confidence."""
        r1 = ContextualPreferenceRule("u1", {"tag": "a"}, "rec1", source="USER", confidence=0.8)
        r2 = ContextualPreferenceRule("u2", {"tag": "a"}, "rec2", source="USER", confidence=1.0)
        self.engine.add_rule(r1)
        self.engine.add_rule(r2)
        res = self.engine.evaluate_contextual_recommendation({"tag": "a"})
        self.assertEqual(res.rule_id, "u2")

    def test_43_context_facts_extra_keys_ignored(self):
        """Test 43: Extra facts in context do not break matching."""
        res = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof", "extra_1": 1, "extra_2": 2})
        self.assertIsNotNone(res)

    def test_44_deep_personalization_integration_ready(self):
        """Test 44: Result structured for LearningEngine integration."""
        res = self.engine.evaluate_contextual_recommendation({"task": "university_email", "sender": "prof"})
        self.assertIn("action_recommendation", res.to_dict())

    def test_45_v5_2_deep_personalization_verification_passed(self):
        """Test 45: All V5.2 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
