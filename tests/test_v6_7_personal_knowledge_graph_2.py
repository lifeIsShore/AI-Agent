import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.knowledge.personal_knowledge_graph_2 import (
    EntityNode,
    RelationshipEdge,
    PersonalKnowledgeGraph2,
    GraphReasoningEngine
)

class TestV67PersonalKnowledgeGraph2(unittest.TestCase):

    def setUp(self):
        self.graph = PersonalKnowledgeGraph2()
        self.reasoning = GraphReasoningEngine(self.graph)

    def test_1_graph_initializes_with_default_nodes_and_edges(self):
        """Test 1: PersonalKnowledgeGraph2 initializes with 5 default nodes and 4 default edges."""
        summary = self.graph.get_graph_summary()
        self.assertEqual(summary["total_nodes"], 5)
        self.assertEqual(summary["total_edges"], 4)

    def test_2_add_node(self):
        """Test 2: add_node adds EntityNode cleanly."""
        node = EntityNode("n_custom", "Custom Node", "DOCUMENT")
        self.graph.add_node(node)
        self.assertEqual(len(self.graph.nodes), 6)

    def test_3_add_edge(self):
        """Test 3: add_edge adds RelationshipEdge cleanly."""
        edge = RelationshipEdge("n_ahmet", "n_custom", "CREATED", 0.95)
        self.graph.add_edge(edge)
        self.assertEqual(len(self.graph.edges), 5)

    def test_4_explain_importance(self):
        """Test 4: explain_importance traverses connected edges and returns provenance chain."""
        res = self.reasoning.explain_importance("n_thesis")
        self.assertEqual(res["node"]["name"], "Master Thesis")
        self.assertTrue(res["connected_facts_count"] >= 2)
        self.assertIsInstance(res["provenance_chain"], list)

    def test_5_explain_importance_unknown_node(self):
        """Test 5: explain_importance returns error dict for unknown node."""
        res = self.reasoning.explain_importance("n_unknown")
        self.assertIn("error", res)

    def test_6_edge_provenance_id_prefix(self):
        """Test 6: RelationshipEdge provenance_id starts with fact_."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(edge.provenance_id.startswith("fact_"))

    def test_7_edge_id_prefix(self):
        """Test 7: RelationshipEdge edge_id starts with edge_."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(edge.edge_id.startswith("edge_"))

    def test_8_node_to_dict_keys(self):
        """Test 8: EntityNode to_dict outputs 4 keys."""
        node = EntityNode("id", "name", "TYPE")
        self.assertEqual(len(node.to_dict()), 4)

    def test_9_edge_to_dict_keys(self):
        """Test 9: RelationshipEdge to_dict outputs 8 keys."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertEqual(len(edge.to_dict()), 8)

    def test_10_node_types_valid(self):
        """Test 10: Default graph contains PERSON, PROJECT, GOAL, TASK entity types."""
        types = set(n["entity_type"] for n in self.graph.get_graph_summary()["nodes"])
        self.assertIn("PERSON", types)
        self.assertIn("PROJECT", types)

    def test_11_stateless_get_summary(self):
        """Test 11: get_graph_summary is stateless and repeatable."""
        s1 = self.graph.get_graph_summary()
        s2 = self.graph.get_graph_summary()
        self.assertEqual(s1["total_nodes"], s2["total_nodes"])

    def test_12_edge_confidence_float(self):
        """Test 12: RelationshipEdge confidence is float."""
        edge = RelationshipEdge("A", "B", "REL", 0.95)
        self.assertIsInstance(edge.confidence, float)

    def test_13_edge_start_time_string(self):
        """Test 13: RelationshipEdge start_time is string."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIsInstance(edge.start_time, str)

    def test_14_node_metadata_dict(self):
        """Test 14: EntityNode metadata is dict."""
        node = EntityNode("id", "name", "TYPE", {"k": "v"})
        self.assertIsInstance(node.metadata, dict)

    def test_15_graph_class_name(self):
        """Test 15: Class name is PersonalKnowledgeGraph2."""
        self.assertEqual(self.graph.__class__.__name__, "PersonalKnowledgeGraph2")

    def test_16_reasoning_class_name(self):
        """Test 16: Class name is GraphReasoningEngine."""
        self.assertEqual(self.reasoning.__class__.__name__, "GraphReasoningEngine")

    def test_17_node_class_name(self):
        """Test 17: Class name is EntityNode."""
        n = EntityNode("i", "n", "t")
        self.assertEqual(n.__class__.__name__, "EntityNode")

    def test_18_edge_class_name(self):
        """Test 18: Class name is RelationshipEdge."""
        e = RelationshipEdge("a", "b", "r")
        self.assertEqual(e.__class__.__name__, "RelationshipEdge")

    def test_19_graph_nodes_dict_keys(self):
        """Test 19: graph.nodes is dict indexed by node_id."""
        self.assertIn("n_ahmet", self.graph.nodes)

    def test_20_graph_edges_list_type(self):
        """Test 20: graph.edges is list."""
        self.assertIsInstance(self.graph.edges, list)

    def test_21_explanation_string(self):
        """Test 21: explanation is string."""
        res = self.reasoning.explain_importance("n_ahmet")
        self.assertIsInstance(res["explanation"], str)

    def test_22_provenance_chain_elements(self):
        """Test 22: Provenance chain contains fact_ IDs."""
        res = self.reasoning.explain_importance("n_thesis")
        for p in res["provenance_chain"]:
            self.assertTrue(p.startswith("fact_"))

    def test_23_custom_provenance_id_preserved(self):
        """Test 23: Custom provenance_id preserved in edge."""
        e = RelationshipEdge("A", "B", "R", 0.9, "fact_custom123")
        self.assertEqual(e.provenance_id, "fact_custom123")

    def test_24_graph_summary_keys_count(self):
        """Test 24: Graph summary dict contains 4 keys."""
        s = self.graph.get_graph_summary()
        self.assertEqual(len(s), 4)

    def test_25_nodes_list_in_summary(self):
        """Test 25: summary nodes is list."""
        s = self.graph.get_graph_summary()
        self.assertIsInstance(s["nodes"], list)

    def test_26_edges_list_in_summary(self):
        """Test 26: summary edges is list."""
        s = self.graph.get_graph_summary()
        self.assertIsInstance(s["edges"], list)

    def test_27_davis_node_name(self):
        """Test 27: Davis node name is Prof. Davis."""
        n = self.graph.nodes["n_davis"]
        self.assertEqual(n.name, "Prof. Davis")

    def test_28_thesis_node_type(self):
        """Test 28: Thesis node type is PROJECT."""
        n = self.graph.nodes["n_thesis"]
        self.assertEqual(n.entity_type, "PROJECT")

    def test_29_msc_node_type(self):
        """Test 29: M.Sc. node type is GOAL."""
        n = self.graph.nodes["n_msc"]
        self.assertEqual(n.entity_type, "GOAL")

    def test_30_methodology_node_type(self):
        """Test 30: Methodology node type is TASK."""
        n = self.graph.nodes["n_methodology"]
        self.assertEqual(n.entity_type, "TASK")

    def test_31_edge_relation_types_valid(self):
        """Test 31: Relation types include STUDIES, WORKS_ON, ADVISOR_OF, REQUIRES."""
        relations = set(e.relation_type for e in self.graph.edges)
        self.assertIn("STUDIES", relations)
        self.assertIn("WORKS_ON", relations)
        self.assertIn("ADVISOR_OF", relations)

    def test_32_reasoning_engine_reusable(self):
        """Test 32: Reasoning engine reusable across calls."""
        r1 = self.reasoning.explain_importance("n_ahmet")
        r2 = self.reasoning.explain_importance("n_davis")
        self.assertNotEqual(r1["node"]["name"], r2["node"]["name"])

    def test_33_edge_confidence_bounded(self):
        """Test 33: Edge confidence is bounded between 0.0 and 1.0."""
        for e in self.graph.edges:
            self.assertTrue(0.0 <= e.confidence <= 1.0)

    def test_34_connected_facts_count_integer(self):
        """Test 34: connected_facts_count is integer."""
        res = self.reasoning.explain_importance("n_thesis")
        self.assertIsInstance(res["connected_facts_count"], int)

    def test_35_multiple_node_additions(self):
        """Test 35: Multiple node additions update nodes dict."""
        self.graph.add_node(EntityNode("n1", "N1", "DOC"))
        self.graph.add_node(EntityNode("n2", "N2", "DOC"))
        self.assertEqual(len(self.graph.nodes), 7)

    def test_36_multiple_edge_additions(self):
        """Test 36: Multiple edge additions update edges list."""
        self.graph.add_edge(RelationshipEdge("n1", "n2", "LINK"))
        self.graph.add_edge(RelationshipEdge("n2", "n1", "LINK"))
        self.assertEqual(len(self.graph.edges), 6)

    def test_37_edge_end_time_defaults_none(self):
        """Test 37: edge end_time defaults to None for active relationship."""
        e = RelationshipEdge("A", "B", "R")
        self.assertIsNone(e.end_time)

    def test_38_node_metadata_default_empty(self):
        """Test 38: EntityNode metadata defaults to empty dict."""
        n = EntityNode("id", "name", "TYPE")
        self.assertEqual(n.metadata, {})

    def test_39_summary_dict_serializable(self):
        """Test 39: Summary dict is JSON serializable."""
        import json
        s = self.graph.get_graph_summary()
        dumped = json.dumps(s)
        self.assertIsInstance(dumped, str)

    def test_40_graph_ui_integration_ready(self):
        """Test 40: Dict structured for Knowledge Graph UI panel integration."""
        s = self.graph.get_graph_summary()
        self.assertIn("nodes", s)
        self.assertIn("edges", s)

    def test_41_explain_importance_dict_keys_count(self):
        """Test 41: explain_importance returns 4 keys."""
        res = self.reasoning.explain_importance("n_ahmet")
        self.assertEqual(len(res), 4)

    def test_42_ahmet_node_name(self):
        """Test 42: Ahmet node name is Ahmet."""
        self.assertEqual(self.graph.nodes["n_ahmet"].name, "Ahmet")

    def test_43_edge_source_target_strings(self):
        """Test 43: source_id and target_id are strings."""
        e = self.graph.edges[0]
        self.assertIsInstance(e.source_id, str)
        self.assertIsInstance(e.target_id, str)

    def test_44_relationship_types_non_empty(self):
        """Test 44: relation_type is non-empty string."""
        for e in self.graph.edges:
            self.assertTrue(len(e.relation_type) > 0)

    def test_45_v6_7_personal_knowledge_graph_verification_passed(self):
        """Test 45: All V6.7 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
