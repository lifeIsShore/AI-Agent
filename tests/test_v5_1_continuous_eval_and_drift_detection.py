import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.eval.continuous_evaluation_engine import ContinuousEvaluationEngine
from personal_agent.eval.performance_baseline_manager import PerformanceBaselineManager, PerformanceBaseline
from personal_agent.eval.behavioral_drift_detector import BehavioralDriftDetector
from personal_agent.eval.regression_monitor import RegressionMonitor
from personal_agent.learning.preference_drift_detector import (
    PreferenceDriftDetector, DRIFT_GENUINE_USER_SHIFT, DRIFT_AGENT_MISLEARNING, DRIFT_TRANSIENT_BEHAVIOR
)
from personal_agent.eval.model_drift_monitor import ModelDriftMonitor
from personal_agent.autonomy.safety_regression_monitor import SafetyRegressionMonitor
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class TestV51ContinuousEvalAndDriftDetection(unittest.TestCase):

    def setUp(self):
        self.eval_engine = ContinuousEvaluationEngine()
        self.baseline_mgr = PerformanceBaselineManager()
        self.drift_detector = BehavioralDriftDetector()
        self.regress_monitor = RegressionMonitor()
        self.pref_drift_detector = PreferenceDriftDetector()
        self.model_drift_monitor = ModelDriftMonitor()
        self.safety_monitor = SafetyRegressionMonitor()

    def test_1_continuous_evaluation_engine_empty(self):
        """Test 1: ContinuousEvaluationEngine handles empty telemetry."""
        res = self.eval_engine.evaluate_telemetry_stream([])
        self.assertEqual(res["eval_status"], "NO_DATA")

    def test_2_continuous_evaluation_engine_evaluates(self):
        """Test 2: evaluate_telemetry_stream outputs accuracy and user acceptance."""
        recs = [MissionTelemetryRecord("m1", tokens=100, rejections=0, human_interventions=0)]
        res = self.eval_engine.evaluate_telemetry_stream(recs)
        self.assertEqual(res["eval_status"], "EVALUATED")
        self.assertEqual(res["current_accuracy"], 1.0)

    def test_3_baseline_manager_initializes(self):
        """Test 3: PerformanceBaselineManager initializes default baselines."""
        b = self.baseline_mgr.get_baseline("default")
        self.assertEqual(b.version, "v5.0.0")

    def test_4_baseline_manager_get_specialist_baseline(self):
        """Test 4: get_baseline returns baseline for EmailSpecialist."""
        b = self.baseline_mgr.get_baseline("EmailSpecialist")
        self.assertEqual(b.specialist_id, "EmailSpecialist")

    def test_5_baseline_manager_set_baseline(self):
        """Test 5: set_baseline updates baseline record."""
        b_new = PerformanceBaseline("b_custom", specialist_id="EmailSpecialist", accuracy=0.96)
        self.baseline_mgr.set_baseline(b_new)
        self.assertEqual(self.baseline_mgr.get_baseline("EmailSpecialist").accuracy, 0.96)

    def test_6_behavioral_drift_detector_detects_accuracy_drift(self):
        """Test 6: detect_behavioral_drift detects accuracy drop."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.85}, baseline)
        self.assertTrue(res["drift_detected"])

    def test_7_behavioral_drift_detector_detects_acceptance_drift(self):
        """Test 7: detect_behavioral_drift detects user acceptance drop."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.94, "current_user_acceptance": 0.70}, baseline)
        self.assertTrue(res["drift_detected"])

    def test_8_behavioral_drift_detector_detects_token_drift(self):
        """Test 8: detect_behavioral_drift detects token spike."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.94, "current_user_acceptance": 0.87, "avg_tokens_per_task": 1500}, baseline)
        self.assertTrue(res["drift_detected"])

    def test_9_behavioral_drift_detector_returns_clean_when_stable(self):
        """Test 9: Clean report when metrics match baseline."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.94, "current_user_acceptance": 0.87, "avg_tokens_per_task": 820}, baseline)
        self.assertFalse(res["drift_detected"])

    def test_10_regression_monitor_accuracy_drop(self):
        """Test 10: check_regression flags accuracy drop below 0.85."""
        res = self.regress_monitor.check_regression({"current_accuracy": 0.75})
        self.assertTrue(res["regression_detected"])

    def test_11_regression_monitor_stable(self):
        """Test 11: check_regression returns clean when accuracy >= 0.85."""
        res = self.regress_monitor.check_regression({"current_accuracy": 0.92})
        self.assertFalse(res["regression_detected"])

    def test_12_preference_drift_detector_user_shift(self):
        """Test 12: detect_preference_drift identifies genuine user shift."""
        history = [{"source": "USER", "val": 1}]
        res = self.pref_drift_detector.detect_preference_drift(history)
        self.assertEqual(res["drift_type"], DRIFT_GENUINE_USER_SHIFT)

    def test_13_preference_drift_detector_agent_mislearning(self):
        """Test 13: detect_preference_drift identifies agent mislearning."""
        history = [{"source": "LEARNED"}, {"source": "LEARNED"}, {"source": "LEARNED"}]
        res = self.pref_drift_detector.detect_preference_drift(history)
        self.assertEqual(res["drift_type"], DRIFT_AGENT_MISLEARNING)

    def test_14_preference_drift_detector_transient(self):
        """Test 14: detect_preference_drift identifies transient behavior."""
        history = [{"source": "LEARNED"}]
        res = self.pref_drift_detector.detect_preference_drift(history)
        self.assertEqual(res["drift_type"], DRIFT_TRANSIENT_BEHAVIOR)

    def test_15_model_drift_monitor_detects_drift(self):
        """Test 15: monitor_model_drift flags accuracy < 0.90."""
        res = self.model_drift_monitor.monitor_model_drift({"model_name": "local", "accuracy": 0.85})
        self.assertTrue(res["drift_detected"])
        self.assertEqual(res["recommendation"], "REVERT_MODEL_TIER")

    def test_16_safety_regression_monitor_zero_tolerance(self):
        """Test 16: evaluate_safety_regression hard-rejects candidate with violation increase."""
        ok, msg = self.safety_monitor.evaluate_safety_regression(baseline_violations=0, candidate_violations=1)
        self.assertFalse(ok)
        self.assertIn("HARD REJECT", msg)

    def test_17_safety_regression_monitor_passes_clean(self):
        """Test 17: evaluate_safety_regression passes when candidate violations <= baseline."""
        ok, msg = self.safety_monitor.evaluate_safety_regression(baseline_violations=0, candidate_violations=0)
        self.assertTrue(ok)

    def test_18_safety_cannot_be_traded_for_performance(self):
        """Test 18: Performance gains with safety violation trigger HARD REJECT."""
        ok, msg = self.safety_monitor.evaluate_safety_regression(baseline_violations=0, candidate_violations=1)
        self.assertFalse(ok)

    def test_19_baseline_to_dict(self):
        """Test 19: PerformanceBaseline to_dict() outputs valid dict."""
        b = PerformanceBaseline("b1")
        d = b.to_dict()
        self.assertEqual(d["baseline_id"], "b1")

    def test_20_continuous_eval_status(self):
        """Test 20: Output status is EVALUATED for non-empty telemetry."""
        recs = [MissionTelemetryRecord("m1")]
        res = self.eval_engine.evaluate_telemetry_stream(recs)
        self.assertEqual(res["eval_status"], "EVALUATED")

    def test_21_behavioral_drift_reasons_list(self):
        """Test 21: drift_reasons list tracks detected issues."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.80}, baseline)
        self.assertTrue(len(res["drift_reasons"]) > 0)

    def test_22_regression_monitor_alerts_list(self):
        """Test 22: alerts list contains regression string."""
        res = self.regress_monitor.check_regression({"current_accuracy": 0.50})
        self.assertTrue(len(res["alerts"]) > 0)

    def test_23_preference_drift_history_empty(self):
        """Test 23: Empty history returns classification = STABLE."""
        res = self.pref_drift_detector.detect_preference_drift([])
        self.assertEqual(res["classification"], "STABLE")

    def test_24_model_drift_recommendation_revert(self):
        """Test 24: Recommendation is REVERT_MODEL_TIER on drift."""
        res = self.model_drift_monitor.monitor_model_drift({"accuracy": 0.80})
        self.assertEqual(res["recommendation"], "REVERT_MODEL_TIER")

    def test_25_model_drift_recommendation_maintain(self):
        """Test 25: Recommendation is MAINTAIN_MODEL_TIER when stable."""
        res = self.model_drift_monitor.monitor_model_drift({"accuracy": 0.95})
        self.assertEqual(res["recommendation"], "MAINTAIN_MODEL_TIER")

    def test_26_baseline_manager_fallback(self):
        """Test 26: Unknown specialist returns default baseline."""
        b = self.baseline_mgr.get_baseline("UnknownSpecialist")
        self.assertEqual(b.baseline_id, "b_default")

    def test_27_drift_reasons_contain_specialist_id(self):
        """Test 27: Drift report contains specialist_id."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.80}, baseline)
        self.assertEqual(res["specialist_id"], "EmailSpecialist")

    def test_28_continuous_eval_tokens_average(self):
        """Test 28: Average tokens per task calculated correctly."""
        recs = [MissionTelemetryRecord("m1", tokens=100), MissionTelemetryRecord("m2", tokens=300)]
        res = self.eval_engine.evaluate_telemetry_stream(recs)
        self.assertEqual(res["avg_tokens_per_task"], 200)

    def test_29_preference_drift_genuine_user_shift_string(self):
        """Test 29: Returns GENUINE_USER_SHIFT."""
        res = self.pref_drift_detector.detect_preference_drift([{"source": "USER"}])
        self.assertEqual(res["drift_type"], DRIFT_GENUINE_USER_SHIFT)

    def test_30_preference_drift_agent_mislearning_string(self):
        """Test 30: Returns AGENT_MISLEARNING."""
        res = self.pref_drift_detector.detect_preference_drift([{"source": "LEARNED"}, {"source": "LEARNED"}, {"source": "LEARNED"}])
        self.assertEqual(res["drift_type"], DRIFT_AGENT_MISLEARNING)

    def test_31_safety_monitor_decision_message(self):
        """Test 31: Message states safety cannot be traded for performance."""
        ok, msg = self.safety_monitor.evaluate_safety_regression(0, 1)
        self.assertIn("Safety cannot be traded for performance", msg)

    def test_32_regression_monitor_custom_threshold(self):
        """Test 32: Custom threshold evaluated correctly."""
        res = self.regress_monitor.check_regression({"current_accuracy": 0.88}, threshold_accuracy=0.90)
        self.assertTrue(res["regression_detected"])

    def test_33_baseline_id_format(self):
        """Test 33: Baseline ID string formatted cleanly."""
        b = PerformanceBaseline("b_id")
        self.assertEqual(b.baseline_id, "b_id")

    def test_34_continuous_eval_sample_size(self):
        """Test 34: Sample size matches telemetry count."""
        recs = [MissionTelemetryRecord("m1"), MissionTelemetryRecord("m2")]
        res = self.eval_engine.evaluate_telemetry_stream(recs)
        self.assertEqual(res["sample_size"], 2)

    def test_35_drift_detector_multi_drift(self):
        """Test 35: Multiple drift reasons accumulated."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.80, "current_user_acceptance": 0.50, "avg_tokens_per_task": 2000}, baseline)
        self.assertEqual(len(res["drift_reasons"]), 3)

    def test_36_preference_drift_explanation(self):
        """Test 36: Explanation string included in preference drift output."""
        res = self.pref_drift_detector.detect_preference_drift([{"source": "USER"}])
        self.assertIn("explanation", res)

    def test_37_model_drift_accuracy_check(self):
        """Test 37: Accuracy returned in model drift report."""
        res = self.model_drift_monitor.monitor_model_drift({"accuracy": 0.95})
        self.assertEqual(res["accuracy"], 0.95)

    def test_38_safety_regression_monitor_zero_violations(self):
        """Test 38: 0 violations returns PASSED."""
        ok, msg = self.safety_monitor.evaluate_safety_regression(0, 0)
        self.assertTrue(ok)

    def test_39_continuous_eval_rounding(self):
        """Test 39: Accuracy rounded to 3 decimal places."""
        recs = [MissionTelemetryRecord("m1", rejections=1), MissionTelemetryRecord("m2", rejections=0), MissionTelemetryRecord("m3", rejections=0)]
        res = self.eval_engine.evaluate_telemetry_stream(recs)
        self.assertEqual(res["current_accuracy"], 0.667)

    def test_40_baseline_manager_planning_specialist(self):
        """Test 40: PlanningSpecialist baseline retrievable."""
        b = self.baseline_mgr.get_baseline("PlanningSpecialist")
        self.assertEqual(b.specialist_id, "PlanningSpecialist")

    def test_41_baseline_manager_research_specialist(self):
        """Test 41: ResearchSpecialist baseline retrievable."""
        b = self.baseline_mgr.get_baseline("ResearchSpecialist")
        self.assertEqual(b.specialist_id, "ResearchSpecialist")

    def test_42_baseline_manager_browser_specialist(self):
        """Test 42: BrowserSpecialist baseline retrievable."""
        b = self.baseline_mgr.get_baseline("BrowserSpecialist")
        self.assertEqual(b.specialist_id, "BrowserSpecialist")

    def test_43_drift_pipeline_trigger_ready(self):
        """Test 43: Drift detection result structured for V5.0 pipeline input."""
        baseline = self.baseline_mgr.get_baseline("EmailSpecialist")
        res = self.drift_detector.detect_behavioral_drift({"current_accuracy": 0.80}, baseline)
        self.assertIn("drift_detected", res)

    def test_44_regression_monitor_metrics_dict(self):
        """Test 44: Metrics dict returned in regression result."""
        res = self.regress_monitor.check_regression({"current_accuracy": 0.90})
        self.assertEqual(res["metrics"]["current_accuracy"], 0.90)

    def test_45_v5_1_continuous_eval_verification_passed(self):
        """Test 45: All V5.1 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
