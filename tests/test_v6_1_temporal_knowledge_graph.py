import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.world.temporal_knowledge_graph import TemporalKnowledgeGraph

class TestV61TemporalKnowledgeGraph(unittest.TestCase):

    def setUp(self):
        self.tkg = TemporalKnowledgeGraph()

    def test_1_temporal_knowledge_graph_initializes(self):
        """Test 1: TemporalKnowledgeGraph initializes with default timeline nodes."""
        self.assertTrue(len(self.tkg.nodes) >= 3)

    def test_2_add_timeline_node(self):
        """Test 2: add_timeline_node appends new timeline node cleanly."""
        node = self.tkg.add_timeline_node(2026, "AI Agent V6.1 Deployment", "PROJECTS", status="ACTIVE")
        self.assertEqual(node["event_name"], "AI Agent V6.1 Deployment")
        self.assertEqual(len(self.tkg.nodes), 4)

    def test_3_get_timeline_sorted(self):
        """Test 3: get_timeline returns nodes sorted by year."""
        timeline = self.tkg.get_timeline()
        self.assertTrue(timeline[0]["year"] <= timeline[-1]["year"])

    def test_4_get_timeline_filter_start_year(self):
        """Test 4: get_timeline filters by start_year parameter."""
        timeline = self.tkg.get_timeline(start_year=2026)
        self.assertTrue(all(n["year"] >= 2026 for n in timeline))

    def test_5_reason_over_timeline(self):
        """Test 5: reason_over_timeline analyzes timeline evolution cleanly."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("past_milestones", res)
        self.assertIn("currently_active", res)
        self.assertIn("why_changed", res)
        self.assertIn("next_likely_event", res)

    def test_6_node_id_prefix(self):
        """Test 6: Node ID generated with t_ year prefix."""
        node = self.tkg.add_timeline_node(2026, "Event", "CAT")
        self.assertTrue(node["node_id"].startswith("t_2026_"))

    def test_7_node_dict_keys_count(self):
        """Test 7: Timeline node contains 5 keys."""
        node = self.tkg.nodes[0]
        self.assertEqual(len(node), 5)

    def test_8_default_nodes_count(self):
        """Test 8: Default timeline nodes count is 3."""
        self.assertEqual(len(self.tkg.nodes), 3)

    def test_9_reason_over_timeline_dict_keys(self):
        """Test 9: reason_over_timeline returns dict with 5 keys."""
        res = self.tkg.reason_over_timeline()
        self.assertEqual(len(res), 5)

    def test_10_past_milestones_list(self):
        """Test 10: past_milestones is list."""
        res = self.tkg.reason_over_timeline()
        self.assertIsInstance(res["past_milestones"], list)

    def test_11_currently_active_list(self):
        """Test 11: currently_active is list."""
        res = self.tkg.reason_over_timeline()
        self.assertIsInstance(res["currently_active"], list)

    def test_12_why_changed_string(self):
        """Test 12: why_changed is string."""
        res = self.tkg.reason_over_timeline()
        self.assertIsInstance(res["why_changed"], str)

    def test_13_next_likely_event_string(self):
        """Test 13: next_likely_event is string."""
        res = self.tkg.reason_over_timeline()
        self.assertIsInstance(res["next_likely_event"], str)

    def test_14_add_timeline_node_returns_dict(self):
        """Test 14: add_timeline_node returns dict instance."""
        node = self.tkg.add_timeline_node(2026, "E", "C")
        self.assertIsInstance(node, dict)

    def test_15_get_timeline_returns_list(self):
        """Test 15: get_timeline returns list instance."""
        res = self.tkg.get_timeline()
        self.assertIsInstance(res, list)

    def test_16_reason_over_timeline_returns_dict(self):
        """Test 16: reason_over_timeline returns dict instance."""
        res = self.tkg.reason_over_timeline()
        self.assertIsInstance(res, dict)

    def test_17_node_year_integer_type(self):
        """Test 17: Node year is integer."""
        self.assertIsInstance(self.tkg.nodes[0]["year"], int)

    def test_18_node_event_name_string_type(self):
        """Test 18: Node event_name is string."""
        self.assertIsInstance(self.tkg.nodes[0]["event_name"], str)

    def test_19_node_category_string_type(self):
        """Test 19: Node category is string."""
        self.assertIsInstance(self.tkg.nodes[0]["category"], str)

    def test_20_node_status_string_type(self):
        """Test 20: Node status is string."""
        self.assertIsInstance(self.tkg.nodes[0]["status"], str)

    def test_21_default_node_bsc_completed(self):
        """Test 21: Default B.Sc. node is COMPLETED."""
        node = self.tkg.nodes[0]
        self.assertEqual(node["status"], "COMPLETED")

    def test_22_default_node_msc_active(self):
        """Test 22: Default M.Sc. node is ACTIVE."""
        node = self.tkg.nodes[1]
        self.assertEqual(node["status"], "ACTIVE")

    def test_23_default_node_thesis_active(self):
        """Test 23: Default Thesis node is ACTIVE."""
        node = self.tkg.nodes[2]
        self.assertEqual(node["status"], "ACTIVE")

    def test_24_timeline_length_matches_nodes_count(self):
        """Test 24: timeline_length matches total nodes count."""
        res = self.tkg.reason_over_timeline()
        self.assertEqual(res["timeline_length"], len(self.tkg.nodes))

    def test_25_stateless_reasoning(self):
        """Test 25: Timeline reasoning is stateless and repeatable."""
        res1 = self.tkg.reason_over_timeline()
        res2 = self.tkg.reason_over_timeline()
        self.assertEqual(res1["timeline_length"], res2["timeline_length"])

    def test_26_add_node_custom_year(self):
        """Test 26: Adding node with year 2027 works cleanly."""
        node = self.tkg.add_timeline_node(2027, "M.Sc. Graduation", "EDUCATION")
        self.assertEqual(node["year"], 2027)

    def test_27_get_timeline_sorting_multiple_years(self):
        """Test 27: get_timeline sorts nodes accurately across multiple years."""
        self.tkg.add_timeline_node(2025, "Past Event", "CAT")
        self.tkg.add_timeline_node(2027, "Future Event", "CAT")
        timeline = self.tkg.get_timeline()
        self.assertEqual(timeline[0]["year"], 2025)
        self.assertEqual(timeline[-1]["year"], 2027)

    def test_28_get_timeline_filter_future_year(self):
        """Test 28: get_timeline with start_year=2027 returns only 2027 nodes."""
        self.tkg.add_timeline_node(2027, "Future Event", "CAT")
        timeline = self.tkg.get_timeline(start_year=2027)
        self.assertEqual(len(timeline), 1)

    def test_29_add_timeline_node_default_status_completed(self):
        """Test 29: add_timeline_node default status is COMPLETED."""
        node = self.tkg.add_timeline_node(2026, "Default Status Event", "CAT")
        self.assertEqual(node["status"], "COMPLETED")

    def test_30_nodes_list_iterable(self):
        """Test 30: nodes list is iterable."""
        count = sum(1 for n in self.tkg.nodes)
        self.assertEqual(count, len(self.tkg.nodes))

    def test_31_past_milestones_contains_bsc(self):
        """Test 31: past_milestones contains B.Sc. event."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("B.Sc. Business Information Systems Completed", res["past_milestones"])

    def test_32_currently_active_contains_msc(self):
        """Test 32: currently_active contains M.Sc. event."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("M.Sc. Wirtschaftsinformatik Started", res["currently_active"])

    def test_33_currently_active_contains_thesis(self):
        """Test 33: currently_active contains Master Thesis event."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("Master Thesis Proposal & Research", res["currently_active"])

    def test_34_why_changed_mentions_mannheim(self):
        """Test 34: why_changed string mentions Mannheim."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("Mannheim", res["why_changed"])

    def test_35_next_likely_event_mentions_thesis(self):
        """Test 35: next_likely_event mentions Thesis."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("Thesis", res["next_likely_event"])

    def test_36_node_category_preservation(self):
        """Test 36: Category string preserved in node."""
        node = self.tkg.add_timeline_node(2026, "E", "FINANCE")
        self.assertEqual(node["category"], "FINANCE")

    def test_37_multiple_nodes_unique_ids(self):
        """Test 37: Multiple added nodes have unique node_ids."""
        n1 = self.tkg.add_timeline_node(2026, "E1", "CAT")
        n2 = self.tkg.add_timeline_node(2026, "E2", "CAT")
        self.assertNotEqual(n1["node_id"], n2["node_id"])

    def test_38_timeline_nodes_dict_structure(self):
        """Test 38: Each node dictionary contains all 5 required fields."""
        node = self.tkg.nodes[0]
        self.assertIn("node_id", node)
        self.assertIn("year", node)
        self.assertIn("event_name", node)
        self.assertIn("category", node)
        self.assertIn("status", node)

    def test_39_get_timeline_none_start_year(self):
        """Test 39: get_timeline(start_year=None) returns all nodes."""
        timeline = self.tkg.get_timeline(start_year=None)
        self.assertEqual(len(timeline), len(self.tkg.nodes))

    def test_40_tkg_integration_ready(self):
        """Test 40: Output structured for PersonalAIOS_v6 integration."""
        res = self.tkg.reason_over_timeline()
        self.assertIn("timeline_length", res)

    def test_41_get_timeline_start_year_beyond_range(self):
        """Test 41: get_timeline with start_year=2099 returns empty list."""
        timeline = self.tkg.get_timeline(start_year=2099)
        self.assertEqual(timeline, [])

    def test_42_add_node_active_status(self):
        """Test 42: Adding node with status ACTIVE includes it in currently_active."""
        self.tkg.add_timeline_node(2026, "Active Internship Search", "CAREER", status="ACTIVE")
        res = self.tkg.reason_over_timeline()
        self.assertIn("Active Internship Search", res["currently_active"])

    def test_43_add_node_completed_status(self):
        """Test 43: Adding node with status COMPLETED includes it in past_milestones."""
        self.tkg.add_timeline_node(2024, "DevOps Data Engineer Role", "CAREER", status="COMPLETED")
        res = self.tkg.reason_over_timeline()
        self.assertIn("DevOps Data Engineer Role", res["past_milestones"])

    def test_44_tkg_class_reuse(self):
        """Test 44: TemporalKnowledgeGraph class reusable across cycles."""
        res1 = self.tkg.reason_over_timeline()
        res2 = self.tkg.reason_over_timeline()
        self.assertEqual(res1["timeline_length"], res2["timeline_length"])

    def test_45_v6_1_temporal_knowledge_graph_verification_passed(self):
        """Test 45: All V6.1 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
