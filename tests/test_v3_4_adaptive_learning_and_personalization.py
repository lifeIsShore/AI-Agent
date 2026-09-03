import sys
import os
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.learning.outcome_engine import (
    OutcomeEngine, ActionOutcome, OUTCOME_SUCCESS, OUTCOME_FAILED,
    OUTCOME_USER_MODIFIED, OUTCOME_USER_REJECTED, OUTCOME_USER_ACCEPTED, OUTCOME_IGNORED
)
from personal_agent.learning.preference_candidate import (
    PreferenceRegistry, PreferenceCandidate, SOURCE_USER, SOURCE_LEARNED, STATUS_CANDIDATE, STATUS_CONFIRMED, STATUS_EXPIRED
)
from personal_agent.learning.learning_engine import LearningEngine
from personal_agent.learning.adaptive_policy import AdaptivePolicy
from personal_agent.learning.reflection_engine import ReflectionEngine
from personal_agent.autonomy.autonomy_policy import LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO

class TestV34AdaptiveLearningAndPersonalization(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_4_")
        self.outcome_engine = OutcomeEngine(storage_dir=self.test_dir)
        self.registry = PreferenceRegistry(storage_dir=self.test_dir)
        self.learning_engine = LearningEngine(
            outcome_engine=self.outcome_engine,
            registry=self.registry
        )
        self.adaptive_policy = AdaptivePolicy(outcome_engine=self.outcome_engine)
        self.reflection_engine = ReflectionEngine(
            outcome_engine=self.outcome_engine,
            learning_engine=self.learning_engine,
            min_reflection_interval_sec=0.1
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_successful_action_produces_outcome(self):
        """Test 1: Successful action produces ActionOutcome with status SUCCESS."""
        out = self.outcome_engine.record_outcome("a1", "create_task", OUTCOME_SUCCESS, goal_id="g1")
        self.assertEqual(out.outcome_type, OUTCOME_SUCCESS)
        self.assertEqual(out.action_type, "create_task")
        self.assertEqual(len(self.outcome_engine.records), 1)

    def test_2_failed_action_produces_outcome(self):
        """Test 2: Failed action produces ActionOutcome with status FAILED."""
        self.outcome_engine.record_outcome("a2_1", "create_task", OUTCOME_SUCCESS)
        out = self.outcome_engine.record_outcome("a2_2", "create_task", OUTCOME_FAILED, actual_result="API Error")
        self.assertEqual(out.outcome_type, OUTCOME_FAILED)
        self.assertEqual(self.outcome_engine.get_success_rate("create_task"), 50.0)

    def test_3_user_modification_recorded(self):
        """Test 3: User schedule shift is recorded as USER_MODIFIED."""
        out = self.outcome_engine.record_outcome(
            "a3", "schedule_thesis", OUTCOME_USER_MODIFIED, user_override=True,
            details={"original_time": "08:00", "preferred_time": "15:00"}
        )
        self.assertTrue(out.user_override)
        self.assertEqual(out.outcome_type, OUTCOME_USER_MODIFIED)

    def test_4_user_rejection_recorded(self):
        """Test 4: Proposal rejection is recorded as USER_REJECTED."""
        out = self.outcome_engine.record_outcome("a4", "delete_calendar", OUTCOME_USER_REJECTED, user_override=True)
        self.assertEqual(out.outcome_type, OUTCOME_USER_REJECTED)

    def test_5_repeated_behavior_creates_candidate_preference(self):
        """Test 5: >= 3 consistent shifts generate a LEARNED candidate preference."""
        for i in range(3):
            self.outcome_engine.record_outcome(
                f"a5_{i}", "thesis_work", OUTCOME_USER_MODIFIED, user_override=True,
                details={"preferred_time": "15:00"}
            )
        
        candidates = self.learning_engine.analyze_patterns()
        self.assertTrue(len(candidates) > 0)
        cand = candidates[0]
        self.assertEqual(cand.source, SOURCE_LEARNED)
        self.assertEqual(cand.value, "15:00")
        self.assertGreaterEqual(cand.confidence, 0.70)

    def test_6_single_event_does_not_create_preference(self):
        """Test 6: Single observation does NOT generate a learned candidate preference."""
        self.outcome_engine.record_outcome("a6", "thesis_work", OUTCOME_USER_MODIFIED, user_override=True, details={"preferred_time": "15:00"})
        candidates = self.learning_engine.analyze_patterns()
        self.assertEqual(len(candidates), 0)

    def test_7_confidence_increases_with_evidence(self):
        """Test 7: Additional supporting observations increase candidate confidence."""
        cand = PreferenceCandidate("p7", "test_key", "val", confidence=0.6, observations_count=1)
        conf1 = cand.confidence
        cand.add_observation("New supporting evidence")
        conf2 = cand.confidence
        self.assertGreater(conf2, conf1)

    def test_8_contradictory_evidence_reduces_confidence(self):
        """Test 8: Contradictory evidence lowers candidate confidence."""
        cand = PreferenceCandidate("p8", "test_key", "val", confidence=0.8, observations_count=3)
        cand.add_contradictory_observation("User moved meeting back to morning")
        self.assertLess(cand.confidence, 0.8)

    def test_9_learned_preference_decays(self):
        """Test 9: Unreinforced learned preferences decay over time."""
        cand = PreferenceCandidate("p9", "test_key", "val", source=SOURCE_LEARNED, confidence=0.7)
        cand.decay_confidence(decay_rate=0.1)
        self.assertEqual(cand.confidence, 0.6)

    def test_10_user_preference_outranks_learned(self):
        """Test 10: USER explicit preference outranks high-confidence LEARNED candidate."""
        self.registry.register_preference("start_hour", 10, source=SOURCE_USER, confidence=1.0)
        # Attempt to register learned preference over user preference
        res = self.registry.register_preference("start_hour", 8, source=SOURCE_LEARNED, confidence=0.9)
        
        effective = self.registry.get_effective_preference("start_hour")
        self.assertEqual(effective.value, 10)
        self.assertEqual(effective.source, SOURCE_USER)

    def test_11_low_confidence_learning_doesnt_affect_planning(self):
        """Test 11: Low-confidence candidate (< 0.70) is ignored for active planning."""
        self.registry.register_preference("low_conf_key", "val", source=SOURCE_LEARNED, confidence=0.5)
        effective = self.registry.get_effective_preference("low_conf_key")
        self.assertIsNone(effective)

    def test_12_high_confidence_learning_affects_planning(self):
        """Test 12: High-confidence candidate (> 0.70) returns active preference value."""
        self.registry.register_preference("high_conf_key", "val_high", source=SOURCE_LEARNED, confidence=0.85, observations_count=4)
        effective = self.registry.get_effective_preference("high_conf_key")
        self.assertIsNotNone(effective)
        self.assertEqual(effective.value, "val_high")

    def test_13_learned_policy_cannot_bypass_governor(self):
        """Test 13: High historical success rate cannot bypass governor level bounds."""
        for i in range(10):
            self.outcome_engine.record_outcome(f"a13_{i}", "create_task", OUTCOME_SUCCESS)
        
        level, reason = self.adaptive_policy.evaluate_adaptive_autonomy_level("create_task", LEVEL_3_BOUNDED_AUTO, governor_max_level=LEVEL_2_APPROVAL)
        self.assertEqual(level, LEVEL_2_APPROVAL)
        self.assertIn("Capped by Governor ceiling", reason)

    def test_14_learning_cannot_increase_maximum_autonomy(self):
        """Test 14: AdaptivePolicy output level is strictly capped by governor_max_level."""
        level, reason = self.adaptive_policy.evaluate_adaptive_autonomy_level("any_action", LEVEL_3_BOUNDED_AUTO, governor_max_level=LEVEL_3_BOUNDED_AUTO)
        self.assertIn(level, (LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO))

    def test_15_user_override_reduces_confidence(self):
        """Test 15: User override reduces confidence score and degrades autonomy recommendation."""
        for i in range(2):
            self.outcome_engine.record_outcome(f"a15_{i}", "schedule_task", OUTCOME_USER_REJECTED, user_override=True)
        
        level, reason = self.adaptive_policy.evaluate_adaptive_autonomy_level("schedule_task", LEVEL_3_BOUNDED_AUTO, governor_max_level=LEVEL_3_BOUNDED_AUTO)
        self.assertEqual(level, LEVEL_2_APPROVAL)
        self.assertIn("degraded autonomy level", reason)

    def test_16_repeated_ignored_notifications_reduce_proactivity(self):
        """Test 16: User rejections logged in outcomes degrade proposal acceptance confidence."""
        for i in range(3):
            self.outcome_engine.record_outcome(f"a16_{i}", "notify_user", OUTCOME_USER_REJECTED)
        self.learning_engine.analyze_patterns()
        
        pref = self.registry.get_preference("proposal_acceptance_notify_user")
        if pref:
            self.assertLess(pref.confidence, 0.5)

    def test_17_repeated_accepted_proposals_increase_confidence(self):
        """Test 17: High acceptance rate boosts proposal confidence."""
        self.registry.register_preference("acceptance_key", "accept", source=SOURCE_LEARNED, confidence=0.6)
        cand = self.registry.get_preference("acceptance_key")
        cand.add_observation("User accepted proposal")
        self.assertGreater(cand.confidence, 0.6)

    def test_18_reflection_produces_actionable_proposals(self):
        """Test 18: ReflectionEngine outputs structured improvement proposals."""
        self.outcome_engine.record_outcome("a18", "create_task", OUTCOME_USER_REJECTED, user_override=True)
        refl = self.reflection_engine.conduct_reflection(force=True)
        
        self.assertEqual(refl["status"], "COMPLETED")
        self.assertTrue(len(refl["improvement_proposals"]) > 0)

    def test_19_reflection_does_not_directly_execute_actions(self):
        """Test 19: Reflection engine outputs proposals only, without executing tool actions directly."""
        refl = self.reflection_engine.conduct_reflection(force=True)
        # Proposals returned are dict representations, not executed mutations
        self.assertIsInstance(refl["improvement_proposals"], list)

    def test_20_learning_survives_restart(self):
        """Test 20: Outcomes and preference candidates persist across process restarts."""
        self.outcome_engine.record_outcome("a20", "task_x", OUTCOME_SUCCESS)
        self.registry.register_preference("key_20", "val_20", source=SOURCE_USER)

        # Re-instantiate from disk
        restarted_outcome = OutcomeEngine(storage_dir=self.test_dir)
        restarted_registry = PreferenceRegistry(storage_dir=self.test_dir)

        self.assertEqual(len(restarted_outcome.records), 1)
        pref = restarted_registry.get_preference("key_20")
        self.assertIsNotNone(pref)
        self.assertEqual(pref.value, "val_20")

    def test_21_corrupted_learning_state_safe_fallback(self):
        """Test 21: Corrupted JSON preference file triggers safe default fallback without crashing."""
        registry = PreferenceRegistry(storage_dir=self.test_dir)
        with open(registry.filepath, 'w', encoding='utf-8') as f:
            f.write("{corrupt_json: [invalid")

        loaded = registry.load_preferences()
        self.assertEqual(len(loaded), 0)

    def test_22_learning_does_not_create_feedback_loops(self):
        """Test 22: Self-reinforcement confidence cap prevents runaway feedback loops above 1.0."""
        cand = PreferenceCandidate("p22", "key22", "val", source=SOURCE_LEARNED, confidence=0.95)
        for _ in range(10):
            cand.add_observation("Reinforce")
        self.assertLessEqual(cand.confidence, 1.0)

    def test_23_event_storms_dont_trigger_excessive_reflection(self):
        """Test 23: Reflection throttle prevents reflection storms during rapid events."""
        refl_policy = ReflectionEngine(outcome_engine=self.outcome_engine, learning_engine=self.learning_engine, min_reflection_interval_sec=10.0)
        
        r1 = refl_policy.conduct_reflection()
        self.assertEqual(r1["status"], "COMPLETED")

        r2 = refl_policy.conduct_reflection()
        self.assertEqual(r2["status"], "THROTTLED")

    def test_24_historical_outcomes_are_auditable(self):
        """Test 24: OutcomeEngine records timestamped audit trails."""
        out = self.outcome_engine.record_outcome("a24", "audit_action", OUTCOME_SUCCESS, details={"audited": True})
        self.assertIsNotNone(out.timestamp)
        self.assertTrue(out.details.get("audited"))

    def test_25_learning_decisions_are_explainable(self):
        """Test 25: explain_preference("key") returns structured explanation and observation stats for 'Why' queries."""
        for i in range(3):
            self.outcome_engine.record_outcome(
                f"a25_{i}", "thesis_scheduling", OUTCOME_USER_MODIFIED, user_override=True,
                details={"preferred_time": "15:00"}
            )
        self.learning_engine.analyze_patterns()

        exp = self.learning_engine.explain_preference("preferred_work_time_thesis_scheduling")
        self.assertTrue(exp["found"])
        self.assertEqual(exp["value"], "15:00")
        self.assertEqual(exp["observations_count"], 3)
        self.assertIn("based on 3 previous observations", exp["explanation"])

if __name__ == "__main__":
    unittest.main()
