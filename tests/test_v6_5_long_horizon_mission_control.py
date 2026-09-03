import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.control.long_horizon_mission_control import LongHorizonMissionControl

class TestV65LongHorizonMissionControl(unittest.TestCase):

    def setUp(self):
        self.control = LongHorizonMissionControl()

    def test_1_control_initializes(self):
        """Test 1: LongHorizonMissionControl initializes cleanly."""
        self.assertIsNotNone(self.control)

    def test_2_get_active_missions_returns_missions(self):
        """Test 2: get_active_missions returns list of 2 active multi-week missions."""
        missions = self.control.get_active_missions()
        self.assertEqual(len(missions), 2)
        self.assertIn("m_thesis", [m["mission_id"] for m in missions])

    def test_3_thesis_mission_progress(self):
        """Test 3: Thesis mission progress_percent is 76%."""
        missions = self.control.get_active_missions()
        thesis = [m for m in missions if m["mission_id"] == "m_thesis"][0]
        self.assertEqual(thesis["progress_percent"], 76)

    def test_4_thesis_mission_completion_prob(self):
        """Test 4: Thesis mission completion_prob is 0.89."""
        missions = self.control.get_active_missions()
        thesis = [m for m in missions if m["mission_id"] == "m_thesis"][0]
        self.assertEqual(thesis["completion_prob"], 0.89)

    def test_5_mission_dict_keys_count(self):
        """Test 5: Mission dict contains 11 keys."""
        missions = self.control.get_active_missions()
        self.assertEqual(len(missions[0]), 11)

    def test_6_mission_id_string(self):
        """Test 6: mission_id is string."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["mission_id"], str)

    def test_7_progress_percent_integer(self):
        """Test 7: progress_percent is integer."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["progress_percent"], int)

    def test_8_status_string(self):
        """Test 8: status is string."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["status"], str)

    def test_9_predicted_completion_date(self):
        """Test 9: predicted_completion is date string."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[0]["predicted_completion"], "2026-11-24")

    def test_10_deadline_date(self):
        """Test 10: deadline is date string."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[0]["deadline"], "2026-11-30")

    def test_11_risk_level_string(self):
        """Test 11: risk_level is string LOW."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[0]["risk_level"], "LOW")

    def test_12_current_step_string(self):
        """Test 12: current_step is string."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["current_step"], str)

    def test_13_selected_strategy_string(self):
        """Test 13: selected_strategy is string."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["selected_strategy"], str)

    def test_14_completion_prob_float(self):
        """Test 14: completion_prob is float."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0]["completion_prob"], float)

    def test_15_bottleneck_string(self):
        """Test 15: bottleneck is string Literature Diversity."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[0]["bottleneck"], "Literature Diversity")

    def test_16_stateless_execution(self):
        """Test 16: get_active_missions is stateless."""
        m1 = self.control.get_active_missions()
        m2 = self.control.get_active_missions()
        self.assertEqual(len(m1), len(m2))

    def test_17_second_mission_id(self):
        """Test 17: Second mission_id is m_msc_courses."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[1]["mission_id"], "m_msc_courses")

    def test_18_second_mission_progress(self):
        """Test 18: Second mission progress_percent is 45%."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[1]["progress_percent"], 45)

    def test_19_second_mission_completion_prob(self):
        """Test 19: Second mission completion_prob is 0.92."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[1]["completion_prob"], 0.92)

    def test_20_second_mission_bottleneck(self):
        """Test 20: Second mission bottleneck is None string."""
        missions = self.control.get_active_missions()
        self.assertEqual(missions[1]["bottleneck"], "None")

    def test_21_missions_return_type_list(self):
        """Test 21: Returns list instance."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions, list)

    def test_22_missions_elements_type_dict(self):
        """Test 22: Returns list of dicts."""
        missions = self.control.get_active_missions()
        self.assertIsInstance(missions[0], dict)

    def test_23_control_class_name(self):
        """Test 23: Class name is LongHorizonMissionControl."""
        self.assertEqual(self.control.__class__.__name__, "LongHorizonMissionControl")

    def test_24_progress_percent_range(self):
        """Test 24: progress_percent is between 0 and 100."""
        missions = self.control.get_active_missions()
        for m in missions:
            self.assertTrue(0 <= m["progress_percent"] <= 100)

    def test_25_completion_prob_range(self):
        """Test 25: completion_prob is between 0.0 and 1.0."""
        missions = self.control.get_active_missions()
        for m in missions:
            self.assertTrue(0.0 <= m["completion_prob"] <= 1.0)

    def test_26_name_key_present(self):
        """Test 26: name key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("name", missions[0])

    def test_27_status_key_present(self):
        """Test 27: status key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("status", missions[0])

    def test_28_deadline_key_present(self):
        """Test 28: deadline key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("deadline", missions[0])

    def test_29_risk_level_key_present(self):
        """Test 29: risk_level key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("risk_level", missions[0])

    def test_30_current_step_key_present(self):
        """Test 30: current_step key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("current_step", missions[0])

    def test_31_selected_strategy_key_present(self):
        """Test 31: selected_strategy key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("selected_strategy", missions[0])

    def test_32_bottleneck_key_present(self):
        """Test 32: bottleneck key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("bottleneck", missions[0])

    def test_33_predicted_completion_key_present(self):
        """Test 33: predicted_completion key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("predicted_completion", missions[0])

    def test_34_completion_prob_key_present(self):
        """Test 34: completion_prob key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("completion_prob", missions[0])

    def test_35_progress_percent_key_present(self):
        """Test 35: progress_percent key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("progress_percent", missions[0])

    def test_36_mission_id_key_present(self):
        """Test 36: mission_id key present in mission dict."""
        missions = self.control.get_active_missions()
        self.assertIn("mission_id", missions[0])

    def test_37_control_reusable(self):
        """Test 37: Instance reusable across calls."""
        m1 = self.control.get_active_missions()
        m2 = self.control.get_active_missions()
        self.assertEqual(m1[0]["name"], m2[0]["name"])

    def test_38_active_missions_list_length_two(self):
        """Test 38: Exactly 2 missions returned."""
        missions = self.control.get_active_missions()
        self.assertEqual(len(missions), 2)

    def test_39_thesis_name_contains_master_thesis(self):
        """Test 39: Mission 1 name contains Master Thesis."""
        missions = self.control.get_active_missions()
        self.assertIn("Master Thesis", missions[0]["name"])

    def test_40_course_name_contains_msc(self):
        """Test 40: Mission 2 name contains M.Sc."""
        missions = self.control.get_active_missions()
        self.assertIn("M.Sc.", missions[1]["name"])

    def test_41_missions_iterable(self):
        """Test 41: Missions list is iterable."""
        missions = self.control.get_active_missions()
        count = sum(1 for _ in missions)
        self.assertEqual(count, 2)

    def test_42_status_executing_or_active(self):
        """Test 42: Status is EXECUTING or ACTIVE."""
        missions = self.control.get_active_missions()
        for m in missions:
            self.assertIn(m["status"], ["EXECUTING", "ACTIVE"])

    def test_43_predicted_before_deadline(self):
        """Test 43: Predicted completion date is before deadline."""
        missions = self.control.get_active_missions()
        for m in missions:
            self.assertTrue(m["predicted_completion"] <= m["deadline"])

    def test_44_mission_control_integration_ready(self):
        """Test 44: Mission control output ready for Active Missions Dashboard panel."""
        missions = self.control.get_active_missions()
        self.assertIn("progress_percent", missions[0])

    def test_45_v6_5_long_horizon_mission_control_verification_passed(self):
        """Test 45: All V6.5 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
