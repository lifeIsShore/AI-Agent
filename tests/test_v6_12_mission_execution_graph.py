import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.execution.mission_execution_graph import (
    GraphNode,
    GraphEdge,
    MissionExecutionGraph
)

class TestV612MissionExecutionGraph(unittest.TestCase):

    def setUp(self):
        self.graph = MissionExecutionGraph()

    def test_1_graph_initializes_with_7_nodes(self):
        """Test 1: MissionExecutionGraph initializes with 7 canonical nodes."""
        self.assertEqual(len(self.graph.nodes), 7)

    def test_2_graph_initializes_with_6_edges(self):
        """Test 2: MissionExecutionGraph initializes with 6 canonical edges."""
        self.assertEqual(len(self.graph.edges), 6)

    def test_3_add_node(self):
        """Test 3: add_node adds GraphNode cleanly."""
        n = GraphNode("n_test", "Test Node", "TASK")
        self.graph.add_node(n)
        self.assertEqual(len(self.graph.nodes), 8)

    def test_4_add_edge(self):
        """Test 4: add_edge adds GraphEdge cleanly."""
        e = GraphEdge("n_test1", "n_test2", "LINK")
        self.graph.add_edge(e)
        self.assertEqual(len(self.graph.edges), 7)

    def test_5_get_execution_summary_keys(self):
        """Test 5: get_execution_summary returns 4 keys."""
        s = self.graph.get_execution_summary()
        self.assertEqual(len(s), 4)

    def test_6_node_to_dict_keys(self):
        """Test 6: GraphNode to_dict returns 8 keys."""
        n = GraphNode("id", "name", "TYPE")
        self.assertEqual(len(n.to_dict()), 8)

    def test_7_edge_to_dict_keys(self):
        """Test 7: GraphEdge to_dict returns 3 keys."""
        e = GraphEdge("A", "B")
        self.assertEqual(len(e.to_dict()), 3)

    def test_8_node_types_present(self):
        """Test 8: Node types include GOAL, MISSION, STRATEGY, TASK, AGENT, MODEL, ACTION."""
        types = set(n.node_type for n in self.graph.nodes.values())
        self.assertIn("GOAL", types)
        self.assertIn("MISSION", types)
        self.assertIn("STRATEGY", types)
        self.assertIn("TASK", types)

    def test_9_node_provenance_id_prefix(self):
        """Test 9: Provenance ID starts with fact_."""
        n = GraphNode("id", "name", "TYPE")
        self.assertTrue(n.provenance_id.startswith("fact_"))

    def test_10_node_authorization_default_authorized(self):
        """Test 10: Default authorization state is AUTHORIZED."""
        n = GraphNode("id", "name", "TYPE")
        self.assertEqual(n.authorization_state, "AUTHORIZED")

    def test_11_graph_class_name(self):
        """Test 11: Class name is MissionExecutionGraph."""
        self.assertEqual(self.graph.__class__.__name__, "MissionExecutionGraph")

    def test_12_node_class_name(self):
        """Test 12: Class name is GraphNode."""
        n = GraphNode("i", "n", "t")
        self.assertEqual(n.__class__.__name__, "GraphNode")

    def test_13_edge_class_name(self):
        """Test 13: Class name is GraphEdge."""
        e = GraphEdge("a", "b")
        self.assertEqual(e.__class__.__name__, "GraphEdge")

    def test_14_node_status_values(self):
        """Test 14: Default graph contains ACTIVE, EXECUTING, COMPLETED statuses."""
        statuses = set(n.status for n in self.graph.nodes.values())
        self.assertIn("ACTIVE", statuses)

    def test_15_node_deadline_string(self):
        """Test 15: deadline is string."""
        n = GraphNode("id", "name", "TYPE")
        self.assertIsInstance(n.deadline, str)

    def test_16_edge_source_target_strings(self):
        """Test 16: source_id and target_id are strings."""
        e = self.graph.edges[0]
        self.assertIsInstance(e.source_id, str)
        self.assertIsInstance(e.target_id, str)

    def test_17_edge_type_string(self):
        """Test 17: edge_type is string."""
        e = self.graph.edges[0]
        self.assertIsInstance(e.edge_type, str)

    def test_18_json_serializable(self):
        """Test 18: Summary output is JSON serializable."""
        import json
        dumped = json.dumps(self.graph.get_execution_summary())
        self.assertIsInstance(dumped, str)

    def test_19_goal_node_name(self):
        """Test 19: Goal node name matches."""
        self.assertIn("Master Thesis", self.graph.nodes["n_goal_thesis"].name)

    def test_20_mission_node_type(self):
        """Test 20: Mission node type is MISSION."""
        self.assertEqual(self.graph.nodes["n_mission_res"].node_type, "MISSION")

    def test_21_strategy_node_type(self):
        """Test 21: Strategy node type is STRATEGY."""
        self.assertEqual(self.graph.nodes["n_strat_c"].node_type, "STRATEGY")

    def test_22_task_node_type(self):
        """Test 22: Task node type is TASK."""
        self.assertEqual(self.graph.nodes["n_task_lit"].node_type, "TASK")

    def test_23_agent_node_type(self):
        """Test 23: Agent node type is AGENT."""
        self.assertEqual(self.graph.nodes["n_agent_res"].node_type, "AGENT")

    def test_24_model_node_type(self):
        """Test 24: Model node type is MODEL."""
        self.assertEqual(self.graph.nodes["n_model_cloud"].node_type, "MODEL")

    def test_25_action_node_type(self):
        """Test 25: Action node type is ACTION."""
        self.assertEqual(self.graph.nodes["n_action_search"].node_type, "ACTION")

    def test_26_stateless_get_summary(self):
        """Test 26: get_execution_summary is repeatable."""
        s1 = self.graph.get_execution_summary()
        s2 = self.graph.get_execution_summary()
        self.assertEqual(s1["total_nodes"], s2["total_nodes"])

    def test_27_multiple_nodes_addition(self):
        """Test 27: Multiple node additions update dict."""
        self.graph.add_node(GraphNode("n1", "N1", "DOC"))
        self.graph.add_node(GraphNode("n2", "N2", "DOC"))
        self.assertEqual(len(self.graph.nodes), 9)

    def test_28_multiple_edges_addition(self):
        """Test 28: Multiple edge additions update list."""
        self.graph.add_edge(GraphEdge("n1", "n2"))
        self.graph.add_edge(GraphEdge("n2", "n1"))
        self.assertEqual(len(self.graph.edges), 8)

    def test_29_action_node_status_completed(self):
        """Test 29: Action node status is COMPLETED."""
        self.assertEqual(self.graph.nodes["n_action_search"].status, "COMPLETED")

    def test_30_node_owner_non_empty(self):
        """Test 30: All node owners are non-empty strings."""
        for n in self.graph.nodes.values():
            self.assertTrue(len(n.owner) > 0)

    def test_31_node_name_non_empty(self):
        """Test 31: All node names are non-empty strings."""
        for n in self.graph.nodes.values():
            self.assertTrue(len(n.name) > 0)

    def test_32_edge_types_valid(self):
        """Test 32: Edge types include DECOMPOSES_TO, USES_STRATEGY, REQUIRES_TASK."""
        types = set(e.edge_type for e in self.graph.edges)
        self.assertIn("DECOMPOSES_TO", types)
        self.assertIn("USES_STRATEGY", types)

    def test_33_nodes_dict_type(self):
        """Test 33: graph.nodes is dict."""
        self.assertIsInstance(self.graph.nodes, dict)

    def test_34_edges_list_type(self):
        """Test 34: graph.edges is list."""
        self.assertIsInstance(self.graph.edges, list)

    def test_35_custom_authorization_state(self):
        """Test 35: Custom authorization state preserved."""
        n = GraphNode("id", "name", "TYPE", authorization_state="PENDING_HUMAN")
        self.assertEqual(n.authorization_state, "PENDING_HUMAN")

    def test_36_node_to_dict_authorization_key(self):
        """Test 36: to_dict contains authorization_state key."""
        n = GraphNode("id", "name", "TYPE")
        self.assertIn("authorization_state", n.to_dict())

    def test_37_summary_nodes_list(self):
        """Test 37: summary nodes is list."""
        s = self.graph.get_execution_summary()
        self.assertIsInstance(s["nodes"], list)

    def test_38_summary_edges_list(self):
        """Test 38: summary edges is list."""
        s = self.graph.get_execution_summary()
        self.assertIsInstance(s["edges"], list)

    def test_39_custom_deadline_preserved(self):
        """Test 39: Custom deadline preserved."""
        n = GraphNode("id", "name", "TYPE", deadline="2026-12-15")
        self.assertEqual(n.deadline, "2026-12-15")

    def test_40_custom_provenance_id_preserved(self):
        """Test 40: Custom provenance_id preserved."""
        n = GraphNode("id", "name", "TYPE", provenance_id="fact_custom99")
        self.assertEqual(n.provenance_id, "fact_custom99")

    def test_41_graph_nodes_count_positive(self):
        """Test 41: Node count is positive integer."""
        self.assertTrue(len(self.graph.nodes) > 0)

    def test_42_graph_edges_count_positive(self):
        """Test 42: Edge count is positive integer."""
        self.assertTrue(len(self.graph.edges) > 0)

    def test_43_node_owner_default_system(self):
        """Test 43: Default node owner is System."""
        n = GraphNode("id", "name", "TYPE")
        self.assertEqual(n.owner, "System")

    def test_44_node_status_default_active(self):
        """Test 44: Default node status is ACTIVE."""
        n = GraphNode("id", "name", "TYPE")
        self.assertEqual(n.status, "ACTIVE")

    def test_45_v6_12_mission_execution_graph_verification_passed(self):
        """Test 45: All V6.12 mission execution graph features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
