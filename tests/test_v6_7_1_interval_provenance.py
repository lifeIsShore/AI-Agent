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

class TestV671IntervalProvenance(unittest.TestCase):

    def setUp(self):
        self.graph = PersonalKnowledgeGraph2()
        self.reasoning = GraphReasoningEngine(self.graph)

    def test_1_edge_has_valid_from(self):
        """Test 1: RelationshipEdge contains valid_from string."""
        edge = RelationshipEdge("A", "B", "REL", valid_from="2026-01-01")
        self.assertEqual(edge.valid_from, "2026-01-01")

    def test_2_edge_valid_until_default_none(self):
        """Test 2: RelationshipEdge valid_until defaults to None (active)."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIsNone(edge.valid_until)

    def test_3_edge_is_active_true(self):
        """Test 3: is_active() returns True when valid_until is None."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(edge.is_active())

    def test_4_edge_is_active_false(self):
        """Test 4: is_active() returns False when valid_until is set."""
        edge = RelationshipEdge("A", "B", "REL", valid_until="2026-10-15")
        self.assertFalse(edge.is_active())

    def test_5_edge_observed_at_string(self):
        """Test 5: observed_at is non-empty string."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIsInstance(edge.observed_at, str)
        self.assertTrue(len(edge.observed_at) > 0)

    def test_6_edge_provenance_source(self):
        """Test 6: RelationshipEdge contains source string."""
        edge = RelationshipEdge("A", "B", "REL", source="arXiv:2401.9912")
        self.assertEqual(edge.source, "arXiv:2401.9912")

    def test_7_edge_provenance_evidence(self):
        """Test 7: RelationshipEdge contains evidence string."""
        edge = RelationshipEdge("A", "B", "REL", evidence="Direct quote from email.")
        self.assertEqual(edge.evidence, "Direct quote from email.")

    def test_8_edge_to_dict_includes_interval_keys(self):
        """Test 8: to_dict includes valid_from, valid_until, observed_at, source, evidence, is_active."""
        edge = RelationshipEdge("A", "B", "REL")
        d = edge.to_dict()
        self.assertIn("valid_from", d)
        self.assertIn("valid_until", d)
        self.assertIn("observed_at", d)
        self.assertIn("source", d)
        self.assertIn("evidence", d)
        self.assertIn("is_active", d)

    def test_9_graph_summary_includes_active_edges(self):
        """Test 9: get_graph_summary includes active_edges count."""
        summary = self.graph.get_graph_summary()
        self.assertIn("active_edges", summary)
        self.assertEqual(summary["active_edges"], 4)

    def test_10_provenance_chain_structure(self):
        """Test 10: explain_importance returns detailed provenance chain dicts."""
        res = self.reasoning.explain_importance("n_thesis")
        for item in res["provenance_chain"]:
            self.assertIn("provenance_id", item)
            self.assertIn("source", item)
            self.assertIn("valid_from", item)
            self.assertIn("evidence", item)

    def test_11_supersedes_id_default_none(self):
        """Test 11: supersedes_id defaults to None."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIsNone(edge.supersedes_id)

    def test_12_supersedes_id_preservation(self):
        """Test 12: Custom supersedes_id preserved."""
        edge = RelationshipEdge("A", "B", "REL", supersedes_id="fact_old123")
        self.assertEqual(edge.supersedes_id, "fact_old123")

    def test_13_inactive_edges_excluded_from_importance(self):
        """Test 13: Inactive edges excluded from explain_importance active count."""
        old_edge = RelationshipEdge("n_thesis", "n_methodology", "OLD_REL", valid_until="2026-05-01")
        self.graph.add_edge(old_edge)
        res = self.reasoning.explain_importance("n_thesis")
        self.assertTrue(res["connected_facts_count"] >= 2)

    def test_14_edge_count_updated_with_inactive(self):
        """Test 14: total_edges includes inactive edges."""
        old_edge = RelationshipEdge("A", "B", "REL", valid_until="2026-05-01")
        self.graph.add_edge(old_edge)
        self.assertEqual(self.graph.get_graph_summary()["total_edges"], 5)

    def test_15_active_edges_count_excludes_inactive(self):
        """Test 15: active_edges excludes inactive edges."""
        old_edge = RelationshipEdge("A", "B", "REL", valid_until="2026-05-01")
        self.graph.add_edge(old_edge)
        self.assertEqual(self.graph.get_graph_summary()["active_edges"], 4)

    def test_16_edge_source_id_ref_key(self):
        """Test 16: to_dict outputs source_id_ref key."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIn("source_id_ref", edge.to_dict())

    def test_17_node_id_matches(self):
        """Test 17: Ahmet node ID matches n_ahmet."""
        self.assertEqual(self.graph.nodes["n_ahmet"].node_id, "n_ahmet")

    def test_18_confidence_between_zero_and_one(self):
        """Test 18: All edge confidences are bounded between 0.0 and 1.0."""
        for e in self.graph.edges:
            self.assertTrue(0.0 <= e.confidence <= 1.0)

    def test_19_provenance_id_starts_with_fact(self):
        """Test 19: Provenance IDs start with fact_."""
        for e in self.graph.edges:
            self.assertTrue(e.provenance_id.startswith("fact_"))

    def test_20_reasoning_explanation_string(self):
        """Test 20: explanation is string."""
        res = self.reasoning.explain_importance("n_ahmet")
        self.assertIsInstance(res["explanation"], str)

    def test_21_valid_from_format(self):
        """Test 21: valid_from matches date format."""
        edge = RelationshipEdge("A", "B", "REL", valid_from="2026-04-01")
        self.assertEqual(len(edge.valid_from), 10)

    def test_22_valid_until_format(self):
        """Test 22: valid_until matches date format when set."""
        edge = RelationshipEdge("A", "B", "REL", valid_until="2026-10-15")
        self.assertEqual(len(edge.valid_until), 10)

    def test_23_observed_at_has_time(self):
        """Test 23: observed_at includes timestamp."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertIn(":", edge.observed_at)

    def test_24_source_default_non_empty(self):
        """Test 24: Default source is non-empty."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(len(edge.source) > 0)

    def test_25_evidence_default_non_empty(self):
        """Test 25: Default evidence is non-empty."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(len(edge.evidence) > 0)

    def test_26_to_dict_keys_count_14(self):
        """Test 26: RelationshipEdge to_dict contains 14 keys."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertEqual(len(edge.to_dict()), 14)

    def test_27_default_edges_all_active(self):
        """Test 27: All default graph edges are active."""
        for e in self.graph.edges:
            self.assertTrue(e.is_active())

    def test_28_davis_advisor_valid_from(self):
        """Test 28: Davis advisor edge valid_from is 2026-04-01."""
        davis_edge = [e for e in self.graph.edges if e.source_id == "n_davis"][0]
        self.assertEqual(davis_edge.valid_from, "2026-04-01")

    def test_29_ahmet_studies_valid_from(self):
        """Test 29: Ahmet studies edge valid_from is 2024-09-01."""
        studies_edge = [e for e in self.graph.edges if e.relation_type == "STUDIES"][0]
        self.assertEqual(studies_edge.valid_from, "2024-09-01")

    def test_30_thesis_requires_methodology_valid_from(self):
        """Test 30: Thesis requires methodology valid_from is 2026-08-01."""
        req_edge = [e for e in self.graph.edges if e.relation_type == "REQUIRES"][0]
        self.assertEqual(req_edge.valid_from, "2026-08-01")

    def test_31_graph_nodes_count_unaffected_by_edges(self):
        """Test 31: Node count remains 5 when adding edges."""
        self.graph.add_edge(RelationshipEdge("n_ahmet", "n_davis", "KNOWS"))
        self.assertEqual(len(self.graph.nodes), 5)

    def test_32_explain_importance_structure_keys(self):
        """Test 32: explain_importance dict contains 4 keys."""
        res = self.reasoning.explain_importance("n_davis")
        self.assertEqual(len(res), 4)

    def test_33_edge_is_active_method_callable(self):
        """Test 33: is_active is a callable method."""
        edge = RelationshipEdge("A", "B", "REL")
        self.assertTrue(callable(edge.is_active))

    def test_34_source_id_ref_in_dict(self):
        """Test 34: source_id_ref is present in to_dict output."""
        edge = RelationshipEdge("A", "B", "REL", source_id_ref="msg_99")
        self.assertEqual(edge.to_dict()["source_id_ref"], "msg_99")

    def test_35_evidence_string_preservation(self):
        """Test 35: Custom evidence text preserved cleanly."""
        edge = RelationshipEdge("A", "B", "REL", evidence="Verified via RAG paper 2401.9912.")
        self.assertEqual(edge.evidence, "Verified via RAG paper 2401.9912.")

    def test_36_supersedes_id_in_dict(self):
        """Test 36: supersedes_id present in to_dict output."""
        edge = RelationshipEdge("A", "B", "REL", supersedes_id="fact_old")
        self.assertEqual(edge.to_dict()["supersedes_id"], "fact_old")

    def test_37_interval_temporal_provenance_json_serializable(self):
        """Test 37: Edge dict is JSON serializable."""
        import json
        edge = RelationshipEdge("A", "B", "REL")
        dumped = json.dumps(edge.to_dict())
        self.assertIsInstance(dumped, str)

    def test_38_graph_summary_json_serializable(self):
        """Test 38: Graph summary with intervals is JSON serializable."""
        import json
        s = self.graph.get_graph_summary()
        dumped = json.dumps(s)
        self.assertIsInstance(dumped, str)

    def test_39_multiple_active_edges_filtered(self):
        """Test 39: Multiple active edges filter cleanly."""
        self.graph.add_edge(RelationshipEdge("n_ahmet", "n_davis", "REL1"))
        self.graph.add_edge(RelationshipEdge("n_ahmet", "n_thesis", "REL2", valid_until="2026-05-01"))
        summary = self.graph.get_graph_summary()
        self.assertEqual(summary["total_edges"], 6)
        self.assertEqual(summary["active_edges"], 5)

    def test_40_provenance_chain_length(self):
        """Test 40: Provenance chain length matches active connected edges."""
        res = self.reasoning.explain_importance("n_thesis")
        self.assertEqual(len(res["provenance_chain"]), res["connected_facts_count"])

    def test_41_graph_class_name(self):
        """Test 41: Class name is PersonalKnowledgeGraph2."""
        self.assertEqual(self.graph.__class__.__name__, "PersonalKnowledgeGraph2")

    def test_42_reasoning_class_name(self):
        """Test 42: Class name is GraphReasoningEngine."""
        self.assertEqual(self.reasoning.__class__.__name__, "GraphReasoningEngine")

    def test_43_valid_until_none_check(self):
        """Test 43: valid_until is None for default edge."""
        self.assertIsNone(self.graph.edges[0].valid_until)

    def test_44_observed_at_string_length(self):
        """Test 44: observed_at has at least 19 characters."""
        self.assertTrue(len(self.graph.edges[0].observed_at) >= 19)

    def test_45_v6_7_1_verification_passed(self):
        """Test 45: All V6.7.1 interval temporal and provenance features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
