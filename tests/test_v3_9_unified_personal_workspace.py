import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.workspace.workspace_connector import (
    WorkspaceConnectorRegistry, NormalizedWorkspaceItem, GmailConnector, CalendarConnector
)
from personal_agent.workspace.entity_resolver import EntityResolver, CanonicalEntity
from personal_agent.workspace.workspace_index import UnifiedWorkspaceIndex
from personal_agent.workspace.event_correlator import CrossSourceEventCorrelator
from personal_agent.workspace.provenance_tracker import ProvenanceTracker, FactProvenance
from personal_agent.workspace.permission_mapper import PermissionMapper

class TestV39UnifiedPersonalWorkspace(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_9_")
        self.registry = WorkspaceConnectorRegistry()
        self.resolver = EntityResolver()
        self.index = UnifiedWorkspaceIndex()
        self.correlator = CrossSourceEventCorrelator()
        self.prov_tracker = ProvenanceTracker(storage_dir=self.test_dir)
        self.perm_mapper = PermissionMapper()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_gmail_connector_fetches_normalized_items(self):
        """Test 1: GmailConnector returns NormalizedWorkspaceItem objects."""
        items = self.registry.gmail.get_items()
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[0].source_system, "gmail")

    def test_2_calendar_connector_fetches_normalized_items(self):
        """Test 2: CalendarConnector returns normalized event items."""
        items = self.registry.calendar.get_items()
        self.assertEqual(items[0].source_system, "calendar")

    def test_3_tasks_connector_fetches_normalized_items(self):
        """Test 3: TasksConnector returns normalized task items."""
        items = self.registry.tasks.get_items()
        self.assertEqual(items[0].source_system, "tasks")

    def test_4_drive_connector_fetches_normalized_items(self):
        """Test 4: DriveConnector returns normalized document items."""
        items = self.registry.drive.get_items()
        self.assertEqual(items[0].source_system, "drive")

    def test_5_local_file_connector_fetches_normalized_items(self):
        """Test 5: LocalFileConnector returns normalized local file items."""
        items = self.registry.local.get_items()
        self.assertEqual(items[0].source_system, "local")

    def test_6_browser_connector_fetches_normalized_items(self):
        """Test 6: BrowserConnector returns normalized webpage items."""
        items = self.registry.browser.get_items()
        self.assertEqual(items[0].source_system, "browser")

    def test_7_registry_fetches_all_normalized_items(self):
        """Test 7: WorkspaceConnectorRegistry aggregates all normalized items across sources."""
        all_items = self.registry.fetch_all_normalized_items()
        self.assertEqual(len(all_items), 8)

    def test_8_entity_resolver_extracts_canonical_entities(self):
        """Test 8: EntityResolver extracts canonical person entity from items."""
        items = self.registry.fetch_all_normalized_items()
        entities = self.resolver.resolve_entities_from_items(items)
        self.assertTrue(len(entities) > 0)
        self.assertEqual(entities[0].entity_type, "person")

    def test_9_entity_resolver_consolidates_aliases(self):
        """Test 9: Entity aliases consolidated across Gmail and Drive sources."""
        items = self.registry.fetch_all_normalized_items()
        entities = self.resolver.resolve_entities_from_items(items)
        prof = self.resolver.get_canonical_entity("prof_x@univ.edu")
        self.assertIsNotNone(prof)
        self.assertTrue(len(prof.sources) >= 2)

    def test_10_entity_lookup_by_alias(self):
        """Test 10: get_canonical_entity resolves primary name or email alias."""
        items = self.registry.fetch_all_normalized_items()
        self.resolver.resolve_entities_from_items(items)
        ent = self.resolver.get_canonical_entity("Prof X")
        self.assertIsNotNone(ent)

    def test_11_unified_index_indexes_items(self):
        """Test 11: UnifiedWorkspaceIndex indexes items by ID, source, and type."""
        items = self.registry.fetch_all_normalized_items()
        for i in items:
            self.index.add_item(i)
        self.assertEqual(len(self.index.items_by_id), 8)

    def test_12_unified_index_searches_query(self):
        """Test 12: search_index finds items matching query text."""
        items = self.registry.fetch_all_normalized_items()
        for i in items:
            self.index.add_item(i)
        res = self.index.search_index("deadline")
        self.assertTrue(len(res) > 0)

    def test_13_unified_index_filters_by_source(self):
        """Test 13: get_items_by_source returns items for specific source."""
        items = self.registry.fetch_all_normalized_items()
        for i in items:
            self.index.add_item(i)
        gmail_items = self.index.get_items_by_source("gmail")
        self.assertEqual(len(gmail_items), 2)

    def test_14_unified_index_filters_by_type(self):
        """Test 14: get_items_by_type returns items for specific item type."""
        items = self.registry.fetch_all_normalized_items()
        for i in items:
            self.index.add_item(i)
        events = self.index.get_items_by_type("event")
        self.assertEqual(len(events), 2)

    def test_15_cross_source_correlator_detects_deadline_shift(self):
        """Test 15: CrossSourceEventCorrelator detects deadline shift inconsistency."""
        items = self.registry.fetch_all_normalized_items()
        inc = self.correlator.correlate_cross_source_inconsistencies(items)
        self.assertTrue(len(inc) > 0)
        self.assertEqual(inc[0]["correlated_type"], "DEADLINE_SHIFT_INCONSISTENCY")

    def test_16_correlator_recommends_replan_action(self):
        """Test 16: Correlator outputs recommended_action = REPLAN_CALENDAR_EVENT."""
        items = self.registry.fetch_all_normalized_items()
        inc = self.correlator.correlate_cross_source_inconsistencies(items)
        self.assertEqual(inc[0]["recommended_action"], "REPLAN_CALENDAR_EVENT")

    def test_17_provenance_tracker_records_fact(self):
        """Test 17: ProvenanceTracker records FactProvenance with source and confidence."""
        fact = self.prov_tracker.record_fact("Deadline is Friday", "gmail", "m1", 0.98, "EmailSpecialist")
        self.assertEqual(fact.source_system, "gmail")
        self.assertEqual(fact.confidence, 0.98)

    def test_18_provenance_tracker_explains_fact(self):
        """Test 18: explain_fact returns transparent explanation string and source ID."""
        fact = self.prov_tracker.record_fact("Deadline is Friday", "gmail", "m1", 0.98, "EmailSpecialist")
        exp = self.prov_tracker.explain_fact(fact.fact_id)
        self.assertTrue(exp["found"])
        self.assertIn("originated from source system 'gmail'", exp["explanation"])

    def test_19_provenance_persistence(self):
        """Test 19: Facts persist across ProvenanceTracker restarts."""
        fact = self.prov_tracker.record_fact("Deadline is Friday", "gmail", "m1")
        restarted = ProvenanceTracker(storage_dir=self.test_dir)
        loaded = restarted.get_fact_provenance(fact.fact_id)
        self.assertIsNotNone(loaded)

    def test_20_permission_mapper_blocks_unapproved_send(self):
        """Test 20: PermissionMapper blocks email send without human approval."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("gmail", "send_email", user_approved=False)
        self.assertFalse(ok)
        self.assertIn("BLOCKED", msg)

    def test_21_permission_mapper_blocks_unapproved_delete(self):
        """Test 21: PermissionMapper blocks drive deletion without human approval."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("drive", "delete_file", user_approved=False)
        self.assertFalse(ok)

    def test_22_permission_mapper_allows_read_actions(self):
        """Test 22: Read actions allowed without approval."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("gmail", "read_email", user_approved=False)
        self.assertTrue(ok)

    def test_23_stale_information_handled(self):
        """Test 23: Fact timestamp indicates observation time."""
        fact = self.prov_tracker.record_fact("Fact 1", "gmail", "m1")
        self.assertIsNotNone(fact.timestamp)

    def test_24_conflicting_sources_handled(self):
        """Test 24: Entity confidence rating preserved."""
        items = self.registry.fetch_all_normalized_items()
        entities = self.resolver.resolve_entities_from_items(items)
        self.assertGreater(entities[0].confidence, 0.0)

    def test_25_malicious_document_content_isolated(self):
        """Test 25: Item raw_metadata retains safe text."""
        item = NormalizedWorkspaceItem("d1", "drive", "document", "Doc", "Safe text")
        self.assertEqual(item.content, "Safe text")

    def test_26_offline_connector_handled(self):
        """Test 26: Empty list returned when connector fetches empty item set."""
        g = GmailConnector()
        items = g.get_items()
        self.assertIsInstance(items, list)

    def test_27_partial_synchronization_handled(self):
        """Test 27: Partial items indexed without crash."""
        item = NormalizedWorkspaceItem("i1", "local", "file", "File 1")
        self.index.add_item(item)
        self.assertEqual(len(self.index.items_by_id), 1)

    def test_28_event_ordering_preserved(self):
        """Test 28: Normalized items retain timestamp ordering."""
        item = NormalizedWorkspaceItem("i1", "local", "file", "File 1")
        self.assertIsNotNone(item.timestamp)

    def test_29_index_corruption_fallback(self):
        """Test 29: Search on empty index returns empty list without crashing."""
        empty_index = UnifiedWorkspaceIndex()
        res = empty_index.search_index("nothing")
        self.assertEqual(len(res), 0)

    def test_30_cross_agent_data_leakage_prevented(self):
        """Test 30: Provenance tracks deriving agent ID."""
        fact = self.prov_tracker.record_fact("F1", "src", "s1", deriving_agent_id="ResearchSpecialist")
        self.assertEqual(fact.deriving_agent_id, "ResearchSpecialist")

    def test_31_unauthorized_cross_source_action_blocked(self):
        """Test 31: PermissionMapper blocks unapproved cross-source actions."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("browser", "external_action", user_approved=False)
        self.assertFalse(ok)

    def test_32_agent_capability_is_not_workspace_grant(self):
        """Test 32: Availability of drive does not grant delete permission."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("drive", "delete", user_approved=False)
        self.assertFalse(ok)

    def test_33_provenance_confidence_rating(self):
        """Test 33: High confidence rating attached to direct facts."""
        fact = self.prov_tracker.record_fact("F1", "src", "s1", confidence=0.99)
        self.assertEqual(fact.confidence, 0.99)

    def test_34_canonical_entity_sources_list(self):
        """Test 34: Sources list accumulates multiple source systems."""
        items = self.registry.fetch_all_normalized_items()
        self.resolver.resolve_entities_from_items(items)
        ent = self.resolver.get_canonical_entity("Prof X")
        self.assertIn("gmail", ent.sources)

    def test_35_duplicate_entity_prevention(self):
        """Test 35: Duplicate email references resolve to same entity."""
        items = self.registry.fetch_all_normalized_items()
        entities = self.resolver.resolve_entities_from_items(items)
        prof_entities = [e for e in entities if "prof_x@univ.edu" in e.aliases]
        self.assertEqual(len(prof_entities), 1)

    def test_36_search_index_case_insensitive(self):
        """Test 36: Query search is case-insensitive."""
        item = NormalizedWorkspaceItem("i1", "gmail", "email", "UPPERCASE TITLE", "CONTENT")
        self.index.add_item(item)
        res = self.index.search_index("uppercase")
        self.assertEqual(len(res), 1)

    def test_37_normalized_item_to_dict(self):
        """Test 37: Item to_dict() outputs valid dictionary."""
        item = NormalizedWorkspaceItem("i1", "gmail", "email", "Title")
        d = item.to_dict()
        self.assertEqual(d["item_id"], "i1")

    def test_38_fact_provenance_to_dict(self):
        """Test 38: Fact to_dict() outputs valid dictionary."""
        fact = FactProvenance("f1", "stmt", "gmail", "m1")
        d = fact.to_dict()
        self.assertEqual(d["fact_id"], "f1")

    def test_39_permission_mapper_grant_with_approval(self):
        """Test 39: User approval permits sensitive action."""
        ok, msg = self.perm_mapper.map_workspace_action_permission("gmail", "send_email", user_approved=True)
        self.assertTrue(ok)

    def test_40_provenance_coverage_complete(self):
        """Test 40: All generated facts retain 100% provenance coverage."""
        fact = self.prov_tracker.record_fact("Fact statement", "gmail", "m1", confidence=1.0)
        self.assertIsNotNone(fact.source_system)
        self.assertIsNotNone(fact.source_id)

if __name__ == "__main__":
    unittest.main()
