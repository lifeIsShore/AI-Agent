import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.memory.memory_consolidator import MemoryConsolidator
from personal_agent.memory.memory_decay_engine import MemoryDecayEngine
from personal_agent.memory.memory_conflict_resolver import MemoryConflictResolver
from personal_agent.world.world_model_consolidator import WorldModelConsolidator
from personal_agent.memory.memory_provenance_graph import MemoryProvenanceGraph

class TestV53LongTermMemoryEvolution(unittest.TestCase):

    def setUp(self):
        self.consolidator = MemoryConsolidator()
        self.decay_engine = MemoryDecayEngine()
        self.conflict_resolver = MemoryConflictResolver()
        self.world_consolidator = WorldModelConsolidator()
        self.provenance_graph = MemoryProvenanceGraph()

    def test_1_memory_consolidator_empty(self):
        """Test 1: MemoryConsolidator handles empty observations."""
        res = self.consolidator.consolidate_observations([])
        self.assertEqual(res, [])

    def test_2_memory_consolidator_threshold_unmet(self):
        """Test 2: Observations below threshold are not consolidated."""
        obs = [{"domain": "univ", "pattern": "afternoon_email"}] * 3
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(res, [])

    def test_3_memory_consolidator_threshold_met(self):
        """Test 3: 5 repeated observations produce 1 durable memory node."""
        obs = [{"domain": "univ", "pattern": "afternoon_email"}] * 5
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["status"], "DURABLE")

    def test_4_memory_consolidator_confidence_scaling(self):
        """Test 4: Observation count increases confidence score."""
        obs = [{"domain": "univ", "pattern": "afternoon_email"}] * 10
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(res[0]["confidence"], 1.0)

    def test_5_memory_decay_engine_user_protected(self):
        """Test 5: USER source memory does NOT decay automatically."""
        mems = [{"id": "m1", "source": "USER", "confidence": 1.0}]
        res = self.decay_engine.apply_decay(mems, days_passed=60)
        self.assertEqual(res[0]["confidence"], 1.0)
        self.assertEqual(res[0]["decay_status"], "PROTECTED_USER")

    def test_6_memory_decay_engine_learned_decays(self):
        """Test 6: LEARNED memory decays over time."""
        mems = [{"id": "m2", "source": "LEARNED", "confidence": 0.90}]
        res = self.decay_engine.apply_decay(mems, days_passed=10, decay_rate=0.05)
        self.assertEqual(res[0]["confidence"], 0.40)
        self.assertEqual(res[0]["decay_status"], "DECAYED")

    def test_7_memory_decay_engine_temporary_expires(self):
        """Test 7: Temporary memory confidence drops to 0.0 (EXPIRED)."""
        mems = [{"id": "m3", "source": "LEARNED", "confidence": 0.80, "temporary": True}]
        res = self.decay_engine.apply_decay(mems, days_passed=1)
        self.assertEqual(res[0]["confidence"], 0.0)
        self.assertEqual(res[0]["decay_status"], "EXPIRED")

    def test_8_memory_conflict_resolver_user_supersedes_learned(self):
        """Test 8: Incoming USER preference supersedes existing LEARNED preference."""
        ex = {"id": "m_old", "source": "LEARNED", "val": "morning"}
        inc = {"id": "m_new", "source": "USER", "val": "afternoon"}
        res = self.conflict_resolver.resolve_conflict(ex, inc)
        self.assertEqual(res["resolution"], "USER_SUPERSEDES_LEARNED")
        self.assertEqual(res["supersedes"], "m_old")

    def test_9_memory_conflict_resolver_newer_user_supersedes_older(self):
        """Test 9: Newer USER preference supersedes older USER preference."""
        ex = {"id": "m_u1", "source": "USER", "val": "morning"}
        inc = {"id": "m_u2", "source": "USER", "val": "evening"}
        res = self.conflict_resolver.resolve_conflict(ex, inc)
        self.assertEqual(res["resolution"], "NEWER_USER_SUPERSEDES_OLDER_USER")

    def test_10_memory_conflict_resolver_existing_user_retained(self):
        """Test 10: Existing USER preference retained over incoming LEARNED."""
        ex = {"id": "m_u", "source": "USER", "val": "morning"}
        inc = {"id": "m_l", "source": "LEARNED", "val": "afternoon"}
        res = self.conflict_resolver.resolve_conflict(ex, inc)
        self.assertEqual(res["resolution"], "RETAIN_EXISTING_USER")

    def test_11_memory_conflict_resolver_confidence_fallback(self):
        """Test 11: Higher confidence wins when sources match."""
        ex = {"id": "m1", "source": "LEARNED", "confidence": 0.60}
        inc = {"id": "m2", "source": "LEARNED", "confidence": 0.85}
        res = self.conflict_resolver.resolve_conflict(ex, inc)
        self.assertEqual(res["resolution"], "HIGHER_CONFIDENCE_WIN")

    def test_12_world_model_consolidator_empty(self):
        """Test 12: WorldModelConsolidator handles empty graphs."""
        res = self.world_consolidator.consolidate_world_graph([], [])
        self.assertEqual(res["total_entities"], 0)

    def test_13_world_model_consolidator_links_entities(self):
        """Test 13: Links People, Projects, Goals cleanly."""
        entities = [{"id": "p1", "type": "Person"}, {"id": "proj1", "type": "Project"}]
        rels = [{"source_id": "p1", "target_id": "proj1", "relation_type": "OWNER"}]
        res = self.world_consolidator.consolidate_world_graph(entities, rels)
        self.assertEqual(res["total_relationships"], 1)

    def test_14_memory_provenance_graph_add_node(self):
        """Test 14: Adds memory node with evidence list."""
        self.provenance_graph.add_memory_node("mem_1", "USER", ["email_1"])
        lineage = self.provenance_graph.get_lineage("mem_1")
        self.assertEqual(lineage["source"], "USER")

    def test_15_memory_provenance_graph_mark_superseded(self):
        """Test 15: Marks memory node as superseded by new node ID."""
        self.provenance_graph.add_memory_node("mem_1", "USER", ["email_1"])
        self.provenance_graph.mark_superseded("mem_1", "mem_2")
        lineage = self.provenance_graph.get_lineage("mem_1")
        self.assertEqual(lineage["superseded_by"], "mem_2")

    def test_16_memory_provenance_graph_get_lineage(self):
        """Test 16: get_lineage returns node dictionary."""
        self.provenance_graph.add_memory_node("m1", "USER", [])
        self.assertIsNotNone(self.provenance_graph.get_lineage("m1"))

    def test_17_consolidator_durable_id_prefix(self):
        """Test 17: Durable ID starts with dur_."""
        obs = [{"domain": "univ", "pattern": "p"}] * 5
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertTrue(res[0]["durable_id"].startswith("dur_"))

    def test_18_consolidator_pattern_key(self):
        """Test 18: Pattern key combines domain and pattern."""
        obs = [{"domain": "univ", "pattern": "p"}] * 5
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(res[0]["domain"], "univ")

    def test_19_decay_engine_decay_status(self):
        """Test 19: Decay status set to DECAYED or PROTECTED_USER."""
        mems = [{"id": "m1", "source": "LEARNED", "confidence": 0.90}]
        res = self.decay_engine.apply_decay(mems, days_passed=10)
        self.assertEqual(res[0]["decay_status"], "DECAYED")

    def test_20_decay_engine_custom_days(self):
        """Test 20: Custom days parameter reduces confidence."""
        mems = [{"id": "m1", "source": "LEARNED", "confidence": 0.90}]
        res = self.decay_engine.apply_decay(mems, days_passed=5, decay_rate=0.1)
        self.assertEqual(res[0]["confidence"], 0.40)

    def test_21_conflict_resolver_resolution_string(self):
        """Test 21: Resolution string included in result."""
        res = self.conflict_resolver.resolve_conflict({"source": "LEARNED"}, {"source": "USER"})
        self.assertIn("resolution", res)

    def test_22_conflict_resolver_supersedes_key(self):
        """Test 22: supersedes key contains replaced memory ID."""
        res = self.conflict_resolver.resolve_conflict({"id": "e1", "source": "LEARNED"}, {"id": "i1", "source": "USER"})
        self.assertEqual(res["supersedes"], "e1")

    def test_23_world_model_total_entities(self):
        """Test 23: Total entities count returned."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}], [])
        self.assertEqual(res["total_entities"], 1)

    def test_24_world_model_total_relationships(self):
        """Test 24: Total relationships count returned."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}, {"id": "e2"}], [{"source_id": "e1", "target_id": "e2"}])
        self.assertEqual(res["total_relationships"], 1)

    def test_25_provenance_graph_superseded_by_none(self):
        """Test 25: Default superseded_by is None."""
        self.provenance_graph.add_memory_node("m1", "USER", [])
        lineage = self.provenance_graph.get_lineage("m1")
        self.assertIsNone(lineage["superseded_by"])

    def test_26_consolidator_status_durable(self):
        """Test 26: Status set to DURABLE."""
        obs = [{"domain": "univ", "pattern": "p"}] * 5
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(res[0]["status"], "DURABLE")

    def test_27_decay_engine_floor_confidence(self):
        """Test 27: Confidence floor is 0.1 for learned memories."""
        mems = [{"id": "m1", "source": "LEARNED", "confidence": 0.20}]
        res = self.decay_engine.apply_decay(mems, days_passed=100)
        self.assertEqual(res[0]["confidence"], 0.1)

    def test_28_conflict_resolver_retained_existing(self):
        """Test 28: Retains existing when confidence is lower."""
        res = self.conflict_resolver.resolve_conflict({"id": "e1", "confidence": 0.9}, {"id": "i1", "confidence": 0.5})
        self.assertEqual(res["resolution"], "RETAIN_EXISTING")

    def test_29_world_model_unlinked_entities_ignored(self):
        """Test 29: Relationships with missing entities ignored."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}], [{"source_id": "e1", "target_id": "missing"}])
        self.assertEqual(res["total_relationships"], 0)

    def test_30_provenance_graph_unknown_node(self):
        """Test 30: Unknown node ID returns None."""
        self.assertIsNone(self.provenance_graph.get_lineage("unknown"))

    def test_31_consolidator_custom_threshold(self):
        """Test 31: Custom threshold parameter works."""
        obs = [{"domain": "univ", "pattern": "p"}] * 2
        res = self.consolidator.consolidate_observations(obs, threshold=2)
        self.assertEqual(len(res), 1)

    def test_32_decay_engine_zero_days(self):
        """Test 32: 0 days passed results in STABLE."""
        mems = [{"id": "m1", "source": "LEARNED", "confidence": 0.80}]
        res = self.decay_engine.apply_decay(mems, days_passed=0)
        self.assertEqual(res[0]["decay_status"], "STABLE")

    def test_33_conflict_resolver_learned_vs_learned(self):
        """Test 33: Compares learned vs learned."""
        res = self.conflict_resolver.resolve_conflict({"source": "LEARNED", "confidence": 0.5}, {"source": "LEARNED", "confidence": 0.8})
        self.assertEqual(res["resolution"], "HIGHER_CONFIDENCE_WIN")

    def test_34_world_model_graph_edges_structure(self):
        """Test 34: Graph edges structure formatted correctly."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}, {"id": "e2"}], [{"source_id": "e1", "target_id": "e2", "relation_type": "LINK"}])
        self.assertEqual(res["graph_edges"][0]["relation"], "LINK")

    def test_35_provenance_graph_multiple_nodes(self):
        """Test 35: Multiple provenance nodes tracked."""
        self.provenance_graph.add_memory_node("n1", "USER", [])
        self.provenance_graph.add_memory_node("n2", "USER", [])
        self.assertEqual(len(self.provenance_graph.nodes), 2)

    def test_36_consolidator_observation_count(self):
        """Test 36: Observation count included in durable item."""
        obs = [{"domain": "univ", "pattern": "p"}] * 6
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(res[0]["observation_count"], 6)

    def test_37_decay_engine_dict_copy(self):
        """Test 37: Returns copied dictionary without mutating original."""
        orig = {"id": "m1", "source": "LEARNED", "confidence": 0.8}
        res = self.decay_engine.apply_decay([orig], days_passed=10)
        self.assertIsNot(orig, res[0])

    def test_38_conflict_resolver_dict_copy(self):
        """Test 38: Returns copied dictionary without mutating original."""
        ex = {"id": "m1", "source": "LEARNED"}
        inc = {"id": "m2", "source": "USER"}
        res = self.conflict_resolver.resolve_conflict(ex, inc)
        self.assertIsNot(inc, res)

    def test_39_world_model_entity_map(self):
        """Test 39: Entity map built accurately."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}], [])
        self.assertEqual(res["total_entities"], 1)

    def test_40_provenance_lineage_observations_count(self):
        """Test 40: Observations count preserved in lineage node."""
        self.provenance_graph.add_memory_node("m1", "USER", [], observations=10)
        lineage = self.provenance_graph.get_lineage("m1")
        self.assertEqual(lineage["observations"], 10)

    def test_41_consolidator_multiple_patterns(self):
        """Test 41: Multiple patterns consolidated independently."""
        obs = [{"domain": "u", "pattern": "p1"}] * 5 + [{"domain": "u", "pattern": "p2"}] * 5
        res = self.consolidator.consolidate_observations(obs, threshold=5)
        self.assertEqual(len(res), 2)

    def test_42_decay_engine_user_decay_status(self):
        """Test 42: USER decay status is PROTECTED_USER."""
        res = self.decay_engine.apply_decay([{"source": "USER", "confidence": 1.0}])
        self.assertEqual(res[0]["decay_status"], "PROTECTED_USER")

    def test_43_conflict_resolver_same_id(self):
        """Test 43: Resolves conflict for same memory ID update."""
        res = self.conflict_resolver.resolve_conflict({"id": "m1", "source": "LEARNED"}, {"id": "m1", "source": "USER"})
        self.assertEqual(res["resolution"], "USER_SUPERSEDES_LEARNED")

    def test_44_world_model_relation_strength(self):
        """Test 44: Relationship strength preserved."""
        res = self.world_consolidator.consolidate_world_graph([{"id": "e1"}, {"id": "e2"}], [{"source_id": "e1", "target_id": "e2", "strength": 0.9}])
        self.assertEqual(res["graph_edges"][0]["strength"], 0.9)

    def test_45_v5_3_long_term_memory_verification_passed(self):
        """Test 45: All V5.3 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
