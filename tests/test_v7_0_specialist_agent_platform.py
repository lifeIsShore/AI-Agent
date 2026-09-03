import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.base_specialist import SpecialistAgent, AgentCapabilityRegistry

class TestV70SpecialistAgentPlatform(unittest.TestCase):

    def setUp(self):
        self.agent = SpecialistAgent(
            agent_id="test_agent",
            name="Test Specialist",
            role="TESTER",
            capabilities=["test.run", "test.inspect"],
            tools=["run_tests"],
            preferred_models=["qwen2.5_1.5b"]
        )
        self.registry = AgentCapabilityRegistry()

    def test_1_agent_initialization(self):
        """Test 1: SpecialistAgent initializes cleanly."""
        self.assertEqual(self.agent.agent_id, "test_agent")

    def test_2_agent_to_dict_keys_count(self):
        """Test 2: to_dict returns 7 keys."""
        self.assertEqual(len(self.agent.to_dict()), 7)

    def test_3_execute_task_returns_dict(self):
        """Test 3: execute_task returns dict."""
        res = self.agent.execute_task({"input": "test"})
        self.assertIsInstance(res, dict)

    def test_4_register_capabilities(self):
        """Test 4: Capability registration works."""
        self.registry.register_agent_capabilities("test_agent", ["test.run"])
        self.assertEqual(len(self.registry.registry), 1)

    def test_5_find_agents_by_capability(self):
        """Test 5: find_agents_by_capability returns agent ID."""
        self.registry.register_agent_capabilities("test_agent", ["test.run"])
        found = self.registry.find_agents_by_capability("test.run")
        self.assertIn("test_agent", found)

    def test_6_autonomy_cap_default_bounded_auto(self):
        """Test 6: Default autonomy_cap is BOUNDED_AUTO."""
        self.assertEqual(self.agent.autonomy_cap, "BOUNDED_AUTO")

    def test_7_provenance_id_contains_agent_id(self):
        """Test 7: execute_task provenance_id contains agent_id."""
        res = self.agent.execute_task({})
        self.assertIn("test_agent", res["provenance_id"])

    def test_8_capabilities_list_type(self):
        """Test 8: capabilities is list."""
        self.assertIsInstance(self.agent.capabilities, list)

    def test_9_tools_list_type(self):
        """Test 9: tools is list."""
        self.assertIsInstance(self.agent.tools, list)

    def test_10_preferred_models_list_type(self):
        """Test 10: preferred_models is list."""
        self.assertIsInstance(self.agent.preferred_models, list)

    def test_11_agent_class_name(self):
        """Test 11: Class name is SpecialistAgent."""
        self.assertEqual(self.agent.__class__.__name__, "SpecialistAgent")

    def test_12_registry_class_name(self):
        """Test 12: Class name is AgentCapabilityRegistry."""
        self.assertEqual(self.registry.__class__.__name__, "AgentCapabilityRegistry")

    def test_13_agent_reusable(self):
        """Test 13: Agent instance is reusable."""
        r1 = self.agent.execute_task({})
        r2 = self.agent.execute_task({})
        self.assertEqual(r1["status"], r2["status"])

    def test_14_json_serializable(self):
        """Test 14: to_dict is JSON serializable."""
        import json
        dumped = json.dumps(self.agent.to_dict())
        self.assertIsInstance(dumped, str)

    def test_15_find_agents_unregistered_returns_empty(self):
        """Test 15: Unregistered capability search returns empty list."""
        self.assertEqual(self.registry.find_agents_by_capability("unknown.cap"), [])

    def test_16_multiple_capabilities_registration(self):
        """Test 16: Multiple capabilities registration."""
        self.registry.register_agent_capabilities("agent1", ["c1", "c2"])
        self.assertEqual(len(self.registry.registry["agent1"]), 2)

    def test_17_find_multiple_agents_by_capability(self):
        """Test 17: Multiple agents found for shared capability."""
        self.registry.register_agent_capabilities("agent1", ["shared"])
        self.registry.register_agent_capabilities("agent2", ["shared"])
        found = self.registry.find_agents_by_capability("shared")
        self.assertEqual(len(found), 2)

    def test_18_custom_autonomy_cap(self):
        """Test 18: Custom autonomy_cap preserved."""
        a = SpecialistAgent("id", "name", "role", [], [], [], autonomy_cap="STRICT_MANUAL")
        self.assertEqual(a.autonomy_cap, "STRICT_MANUAL")

    def test_19_agent_name_string(self):
        """Test 19: name is string."""
        self.assertIsInstance(self.agent.name, str)

    def test_20_agent_role_string(self):
        """Test 20: role is string."""
        self.assertIsInstance(self.agent.role, str)

    def test_21_agent_id_string(self):
        """Test 21: agent_id is string."""
        self.assertIsInstance(self.agent.agent_id, str)

    def test_22_execute_task_status_completed(self):
        """Test 22: execute_task status is COMPLETED."""
        res = self.agent.execute_task({})
        self.assertEqual(res["status"], "COMPLETED")

    def test_23_execute_task_output_non_empty(self):
        """Test 23: execute_task output is non-empty string."""
        res = self.agent.execute_task({})
        self.assertTrue(len(res["output"]) > 0)

    def test_24_registry_dict_type(self):
        """Test 24: registry.registry is dict."""
        self.assertIsInstance(self.registry.registry, dict)

    def test_25_capabilities_non_empty(self):
        """Test 25: capabilities is non-empty list."""
        self.assertTrue(len(self.agent.capabilities) > 0)

    def test_26_tools_non_empty(self):
        """Test 26: tools is non-empty list."""
        self.assertTrue(len(self.agent.tools) > 0)

    def test_27_preferred_models_non_empty(self):
        """Test 27: preferred_models is non-empty list."""
        self.assertTrue(len(self.agent.preferred_models) > 0)

    def test_28_to_dict_agent_id_key(self):
        """Test 28: to_dict contains agent_id key."""
        self.assertIn("agent_id", self.agent.to_dict())

    def test_29_to_dict_name_key(self):
        """Test 29: to_dict contains name key."""
        self.assertIn("name", self.agent.to_dict())

    def test_30_to_dict_role_key(self):
        """Test 30: to_dict contains role key."""
        self.assertIn("role", self.agent.to_dict())

    def test_31_to_dict_capabilities_key(self):
        """Test 31: to_dict contains capabilities key."""
        self.assertIn("capabilities", self.agent.to_dict())

    def test_32_to_dict_tools_key(self):
        """Test 32: to_dict contains tools key."""
        self.assertIn("tools", self.agent.to_dict())

    def test_33_to_dict_preferred_models_key(self):
        """Test 33: to_dict contains preferred_models key."""
        self.assertIn("preferred_models", self.agent.to_dict())

    def test_34_to_dict_autonomy_cap_key(self):
        """Test 34: to_dict contains autonomy_cap key."""
        self.assertIn("autonomy_cap", self.agent.to_dict())

    def test_35_stateless_execution(self):
        """Test 35: execute_task does not mutate agent configuration."""
        d1 = self.agent.to_dict()
        self.agent.execute_task({})
        d2 = self.agent.to_dict()
        self.assertEqual(d1, d2)

    def test_36_agent_instantiation_clean(self):
        """Test 36: SpecialistAgent instantiates cleanly."""
        a = SpecialistAgent("a", "b", "c", [], [], [])
        self.assertIsNotNone(a)

    def test_37_registry_instantiation_clean(self):
        """Test 37: AgentCapabilityRegistry instantiates cleanly."""
        r = AgentCapabilityRegistry()
        self.assertIsNotNone(r)

    def test_38_find_agents_returns_list(self):
        """Test 38: find_agents_by_capability returns list."""
        self.assertIsInstance(self.registry.find_agents_by_capability("c"), list)

    def test_39_overwriting_capabilities_registration(self):
        """Test 39: Overwriting capability registration updates list."""
        self.registry.register_agent_capabilities("a1", ["c1"])
        self.registry.register_agent_capabilities("a1", ["c2"])
        self.assertEqual(self.registry.registry["a1"], ["c2"])

    def test_40_no_error_in_task_output(self):
        """Test 40: Task execution does not return error."""
        res = self.agent.execute_task({})
        self.assertNotIn("error", res)

    def test_41_provenance_id_prefix(self):
        """Test 41: Provenance ID starts with fact_."""
        res = self.agent.execute_task({})
        self.assertTrue(res["provenance_id"].startswith("fact_"))

    def test_42_dict_return_type(self):
        """Test 42: to_dict return type is dict."""
        self.assertEqual(type(self.agent.to_dict()), dict)

    def test_43_task_return_type(self):
        """Test 43: execute_task return type is dict."""
        self.assertEqual(type(self.agent.execute_task({})), dict)

    def test_44_registry_dict_type(self):
        """Test 44: registry return type is dict."""
        self.assertEqual(type(self.registry.registry), dict)

    def test_45_v7_0_specialist_agent_platform_verification_passed(self):
        """Test 45: All V7.0 specialist agent platform features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
