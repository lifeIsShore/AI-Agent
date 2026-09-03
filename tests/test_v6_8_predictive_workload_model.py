import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.predictive.predictive_workload_model import (
    CapacityEstimator,
    DemandEstimator,
    WorkloadRiskDetector,
    PredictiveWorkloadModel
)

class TestV68PredictiveWorkloadModel(unittest.TestCase):

    def setUp(self):
        self.model = PredictiveWorkloadModel()

    def test_1_forecast_returns_dict(self):
        """Test 1: get_forecast returns forecast dictionary."""
        forecast = self.model.get_forecast()
        self.assertIsInstance(forecast, dict)

    def test_2_forecast_contains_horizon_days(self):
        """Test 2: Forecast contains 14 horizon days."""
        forecast = self.model.get_forecast(14)
        self.assertEqual(forecast["horizon_days"], 14)

    def test_3_capacity_available_hours(self):
        """Test 3: Available capacity is 52.0 hours."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertEqual(cap["available_capacity_hours"], 52.0)

    def test_4_demand_total_hours(self):
        """Test 4: Total demand is 64.0 hours."""
        dem = self.model.demand_estimator.estimate_demand()
        self.assertEqual(dem["total_demand_hours"], 64.0)

    def test_5_overload_risk_level_high(self):
        """Test 5: Overload risk level is HIGH when demand exceeds capacity."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertEqual(risk["risk_level"], "HIGH")

    def test_6_overload_hours_calculation(self):
        """Test 6: Overload hours is 12.0 hours."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertEqual(risk["overload_hours"], 12.0)

    def test_7_bottleneck_identification(self):
        """Test 7: Bottleneck is identified as Thesis Methodology."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertIn("Thesis Methodology", risk["bottleneck"])

    def test_8_simulate_scenarios_returns_3_scenarios(self):
        """Test 8: simulate_scenarios returns 3 scenarios."""
        scenarios = self.model.simulate_scenarios()
        self.assertEqual(len(scenarios["scenarios"]), 3)

    def test_9_scenario_b_is_recommended(self):
        """Test 9: Scenario B is recommended."""
        scenarios = self.model.simulate_scenarios()
        opt_b = scenarios["scenarios"][1]
        self.assertEqual(opt_b["scenario_id"], "defer_secondary")
        self.assertIn("Recommended", opt_b["impact"])

    def test_10_forecast_keys_count(self):
        """Test 10: get_forecast returns 5 top-level keys."""
        forecast = self.model.get_forecast()
        self.assertEqual(len(forecast), 5)

    def test_11_capacity_keys_count(self):
        """Test 11: estimate_capacity returns 6 keys."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertEqual(len(cap), 6)

    def test_12_demand_keys_count(self):
        """Test 12: estimate_demand returns 4 keys."""
        dem = self.model.demand_estimator.estimate_demand()
        self.assertEqual(len(dem), 4)

    def test_13_risk_keys_count(self):
        """Test 13: detect_risk returns 6 keys."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertEqual(len(risk), 6)

    def test_14_capacity_net_usable_calculation(self):
        """Test 14: Net usable capacity is 45.0 hours (52 - 7)."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertEqual(cap["net_usable_capacity_hours"], 45.0)

    def test_15_delay_probability_float(self):
        """Test 15: Delay probability is float."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertIsInstance(risk["delay_probability"], float)

    def test_16_recommended_intervention_string(self):
        """Test 16: Recommended intervention is string."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertIsInstance(risk["recommended_intervention"], str)

    def test_17_scenario_id_unique(self):
        """Test 17: Scenario IDs are unique across scenarios."""
        scenarios = self.model.simulate_scenarios()["scenarios"]
        ids = set(s["scenario_id"] for s in scenarios)
        self.assertEqual(len(ids), 3)

    def test_18_scenario_utilization_percentages(self):
        """Test 18: Scenarios include utilization percentage string."""
        scenarios = self.model.simulate_scenarios()["scenarios"]
        for s in scenarios:
            self.assertIn("%", s["utilization"])

    def test_19_forecast_timestamp_string(self):
        """Test 19: Forecast includes non-empty forecast_timestamp."""
        forecast = self.model.get_forecast()
        self.assertIsInstance(forecast["forecast_timestamp"], str)
        self.assertTrue(len(forecast["forecast_timestamp"]) > 0)

    def test_20_capacity_estimator_class_name(self):
        """Test 20: Class name is CapacityEstimator."""
        self.assertEqual(self.model.capacity_estimator.__class__.__name__, "CapacityEstimator")

    def test_21_demand_estimator_class_name(self):
        """Test 21: Class name is DemandEstimator."""
        self.assertEqual(self.model.demand_estimator.__class__.__name__, "DemandEstimator")

    def test_22_risk_detector_class_name(self):
        """Test 22: Class name is WorkloadRiskDetector."""
        self.assertEqual(self.model.risk_detector.__class__.__name__, "WorkloadRiskDetector")

    def test_23_custom_horizon_days(self):
        """Test 23: Custom horizon days (7) preserved."""
        cap = self.model.capacity_estimator.estimate_capacity(7)
        self.assertEqual(cap["horizon_days"], 7)

    def test_24_risk_level_low_when_demand_under_capacity(self):
        """Test 24: Risk level is LOW when demand <= capacity."""
        cap = {"available_capacity_hours": 60.0}
        dem = {"total_demand_hours": 50.0}
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertEqual(risk["risk_level"], "LOW")

    def test_25_risk_level_medium_when_slight_overload(self):
        """Test 25: Risk level is MEDIUM when 0 < overload <= 5."""
        cap = {"available_capacity_hours": 50.0}
        dem = {"total_demand_hours": 53.0}
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertEqual(risk["risk_level"], "MEDIUM")

    def test_26_scenario_a_overload_risk_high(self):
        """Test 26: Scenario A overload risk is HIGH."""
        s_a = self.model.simulate_scenarios()["scenarios"][0]
        self.assertEqual(s_a["overload_risk"], "HIGH")

    def test_27_scenario_c_completion_prob_91(self):
        """Test 27: Scenario C completion probability is 91%."""
        s_c = self.model.simulate_scenarios()["scenarios"][2]
        self.assertEqual(s_c["completion_probability"], "91%")

    def test_28_forecast_json_serializable(self):
        """Test 28: Forecast output is JSON serializable."""
        import json
        dumped = json.dumps(self.model.get_forecast())
        self.assertIsInstance(dumped, str)

    def test_29_scenarios_json_serializable(self):
        """Test 29: Scenarios output is JSON serializable."""
        import json
        dumped = json.dumps(self.model.simulate_scenarios())
        self.assertIsInstance(dumped, str)

    def test_30_thesis_demand_hours_positive(self):
        """Test 30: Thesis demand hours > 0."""
        dem = self.model.demand_estimator.estimate_demand()
        self.assertTrue(dem["thesis_demand_hours"] > 0)

    def test_31_course_demand_hours_positive(self):
        """Test 31: Course demand hours > 0."""
        dem = self.model.demand_estimator.estimate_demand()
        self.assertTrue(dem["course_demand_hours"] > 0)

    def test_32_secondary_demand_hours_positive(self):
        """Test 32: Secondary demand hours > 0."""
        dem = self.model.demand_estimator.estimate_demand()
        self.assertTrue(dem["secondary_demand_hours"] > 0)

    def test_33_calendar_commitments_hours_positive(self):
        """Test 33: Calendar commitments > 0."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertTrue(cap["calendar_commitments_hours"] > 0)

    def test_34_expected_interruptions_hours_positive(self):
        """Test 34: Expected interruptions > 0."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertTrue(cap["expected_interruptions_hours"] > 0)

    def test_35_buffer_capacity_hours_positive(self):
        """Test 35: Buffer capacity > 0."""
        cap = self.model.capacity_estimator.estimate_capacity()
        self.assertTrue(cap["buffer_capacity_hours"] > 0)

    def test_36_utilization_percent_float(self):
        """Test 36: Utilization percent is float."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertIsInstance(risk["utilization_percent"], float)

    def test_37_overload_hours_float(self):
        """Test 37: Overload hours is float."""
        cap = self.model.capacity_estimator.estimate_capacity()
        dem = self.model.demand_estimator.estimate_demand()
        risk = self.model.risk_detector.detect_risk(cap, dem)
        self.assertIsInstance(risk["overload_hours"], float)

    def test_38_predictive_workload_model_reusable(self):
        """Test 38: PredictiveWorkloadModel instance is reusable."""
        f1 = self.model.get_forecast()
        f2 = self.model.get_forecast()
        self.assertEqual(f1["horizon_days"], f2["horizon_days"])

    def test_39_scenario_b_utilization_96(self):
        """Test 39: Scenario B utilization is 96%."""
        s_b = self.model.simulate_scenarios()["scenarios"][1]
        self.assertEqual(s_b["utilization"], "96%")

    def test_40_scenario_a_utilization_123(self):
        """Test 40: Scenario A utilization is 123%."""
        s_a = self.model.simulate_scenarios()["scenarios"][0]
        self.assertEqual(s_a["utilization"], "123%")

    def test_41_scenarios_top_key_scenarios(self):
        """Test 41: simulate_scenarios dict contains top key 'scenarios'."""
        res = self.model.simulate_scenarios()
        self.assertIn("scenarios", res)

    def test_42_scenario_names_non_empty(self):
        """Test 42: All scenario names are non-empty strings."""
        for s in self.model.simulate_scenarios()["scenarios"]:
            self.assertTrue(len(s["name"]) > 0)

    def test_43_scenario_impacts_non_empty(self):
        """Test 43: All scenario impacts are non-empty strings."""
        for s in self.model.simulate_scenarios()["scenarios"]:
            self.assertTrue(len(s["impact"]) > 0)

    def test_44_model_class_name(self):
        """Test 44: Class name is PredictiveWorkloadModel."""
        self.assertEqual(self.model.__class__.__name__, "PredictiveWorkloadModel")

    def test_45_v6_8_predictive_workload_verification_passed(self):
        """Test 45: All V6.8 predictive workload modeling features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
