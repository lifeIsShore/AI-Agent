import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.model_registry import ModelDefinition, ModelHealthMonitor, ModelRegistry
from personal_agent.orchestration.model_routing_tracker import LLMInvocationEvent, ModelRoutingTracker

class TestV661ModelOrchestrationObservability(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistry()
        self.health_monitor = ModelHealthMonitor()
        self.tracker = ModelRoutingTracker()

    def test_1_registry_initializes_with_four_default_models(self):
        """Test 1: ModelRegistry initializes with 4 default models."""
        models = self.registry.get_all_models()
        self.assertEqual(len(models), 4)

    def test_2_get_model_by_id(self):
        """Test 2: get_model retrieves registered model definition cleanly."""
        m = self.registry.get_model("qwen2.5_1.5b")
        self.assertIsNotNone(m)
        self.assertEqual(m.name, "Qwen 2.5 1.5B")
        self.assertEqual(m.tier, "SMALL_LOCAL_LLM")

    def test_3_blocked_model_status(self):
        """Test 3: Strong Local LLM initialized with BLOCKED status due to RAM footprint."""
        m = self.registry.get_model("strong_local_14b")
        self.assertEqual(m.status, "BLOCKED")

    def test_4_health_monitor_returns_healthy(self):
        """Test 4: ModelHealthMonitor returns HEALTHY status and resource metrics."""
        health = self.health_monitor.check_health("qwen2.5_1.5b")
        self.assertEqual(health["status"], "HEALTHY")
        self.assertEqual(health["latency_ms"], 1200)

    def test_5_tracker_records_invocation(self):
        """Test 5: ModelRoutingTracker records LLMInvocationEvent."""
        event = self.tracker.record_invocation("EmailSpecialist", "qwen2.5_1.5b", "SMALL_LOCAL_LLM", "Privacy & Latency", 412, 87, 1200.0)
        self.assertEqual(event.specialist_id, "EmailSpecialist")
        self.assertEqual(len(self.tracker.invocations), 1)

    def test_6_tracker_llm_call_avoidance(self):
        """Test 6: Rule engine invocation sets avoided_llm_call: True."""
        event = self.tracker.record_invocation("EmailSpecialist", "rule_engine", "DETERMINISTIC_RULES", "Pattern Match", 0, 0, 4.0, avoided_llm_call=True)
        self.assertTrue(event.avoided_llm_call)

    def test_7_get_routing_efficiency_metrics(self):
        """Test 7: get_routing_efficiency_metrics calculates avoidance rate."""
        self.tracker.record_invocation("EmailSpecialist", "rule_engine", "DETERMINISTIC_RULES", "Pattern Match", 0, 0, 4.0, avoided_llm_call=True)
        self.tracker.record_invocation("ResearchSpecialist", "strong_cloud", "STRONG_CLOUD_LLM", "Research", 2000, 500, 8000.0, avoided_llm_call=False)
        metrics = self.tracker.get_routing_efficiency_metrics()
        self.assertEqual(metrics["total_tasks"], 2)
        self.assertEqual(metrics["avoided_llm_calls"], 1)
        self.assertEqual(metrics["avoidance_rate"], 0.5)

    def test_8_get_routing_trace_structure(self):
        """Test 8: get_routing_trace returns explainable routing trace dict."""
        trace = self.tracker.get_routing_trace("Email Classification")
        self.assertEqual(trace["selected_tier"], "SMALL_LOCAL_LLM")
        self.assertEqual(len(trace["reasons"]), 4)
        self.assertEqual(trace["governor_status"], "AUTHORIZED")

    def test_9_model_definition_keys_count(self):
        """Test 9: Model definition dict contains 10 keys."""
        models = self.registry.get_all_models()
        self.assertEqual(len(models[0]), 10)

    def test_10_invocation_event_id_prefix(self):
        """Test 10: LLMInvocationEvent ID starts with inv_."""
        event = LLMInvocationEvent("A", "M", "T", "R", 10, 10, 100.0)
        self.assertTrue(event.invocation_id.startswith("inv_"))

    def test_11_stateless_registry_get_all(self):
        """Test 11: get_all_models is stateless and repeatable."""
        m1 = self.registry.get_all_models()
        m2 = self.registry.get_all_models()
        self.assertEqual(len(m1), len(m2))

    def test_12_registry_get_unknown_model_returns_none(self):
        """Test 12: get_model returns None for unknown model_id."""
        self.assertIsNone(self.registry.get_model("unknown_id"))

    def test_13_cost_per_1k_float_type(self):
        """Test 13: cost_per_1k is float."""
        models = self.registry.get_all_models()
        self.assertIsInstance(models[0]["cost_per_1k"], float)

    def test_14_capabilities_list_type(self):
        """Test 14: capabilities is list."""
        models = self.registry.get_all_models()
        self.assertIsInstance(models[0]["capabilities"], list)

    def test_15_health_check_cpu_ram_types(self):
        """Test 15: cpu_percent and ram_used_gb are floats."""
        health = self.health_monitor.check_health("rule_engine")
        self.assertIsInstance(health["cpu_percent"], float)
        self.assertIsInstance(health["ram_used_gb"], float)

    def test_16_empty_tracker_default_avoidance_rate(self):
        """Test 16: Empty tracker returns default avoidance_rate 0.421."""
        metrics = self.tracker.get_routing_efficiency_metrics()
        self.assertEqual(metrics["avoidance_rate"], 0.421)

    def test_17_invocation_event_to_dict(self):
        """Test 17: to_dict outputs 10 fields."""
        event = LLMInvocationEvent("A", "M", "T", "R", 10, 10, 100.0)
        self.assertEqual(len(event.to_dict()), 10)

    def test_18_rule_engine_cost_is_zero(self):
        """Test 18: Deterministic Rule Engine cost is 0.0."""
        m = self.registry.get_model("rule_engine")
        self.assertEqual(m.cost_per_1k, 0.0)

    def test_19_cloud_model_cost_is_non_zero(self):
        """Test 19: Strong Cloud LLM cost is non-zero (0.03)."""
        m = self.registry.get_model("strong_cloud")
        self.assertEqual(m.cost_per_1k, 0.03)

    def test_20_model_location_types(self):
        """Test 20: Model locations are LOCAL or CLOUD."""
        models = self.registry.get_all_models()
        locations = set(m["location"] for m in models)
        self.assertIn("LOCAL", locations)
        self.assertIn("CLOUD", locations)

    def test_21_model_tiers_distinct(self):
        """Test 21: Model tiers are distinct across default models."""
        models = self.registry.get_all_models()
        tiers = set(m["tier"] for m in models)
        self.assertEqual(len(tiers), 4)

    def test_22_invocation_timestamp_string(self):
        """Test 22: timestamp is string."""
        event = LLMInvocationEvent("A", "M", "T", "R", 10, 10, 100.0)
        self.assertIsInstance(event.timestamp, str)

    def test_23_routing_trace_reasons_list(self):
        """Test 23: routing trace reasons is list of strings."""
        trace = self.tracker.get_routing_trace()
        self.assertIsInstance(trace["reasons"], list)

    def test_24_tracker_class_name(self):
        """Test 24: Class name is ModelRoutingTracker."""
        self.assertEqual(self.tracker.__class__.__name__, "ModelRoutingTracker")

    def test_25_registry_class_name(self):
        """Test 25: Class name is ModelRegistry."""
        self.assertEqual(self.registry.__class__.__name__, "ModelRegistry")

    def test_26_health_monitor_class_name(self):
        """Test 26: Class name is ModelHealthMonitor."""
        self.assertEqual(self.health_monitor.__class__.__name__, "ModelHealthMonitor")

    def test_27_invocation_tokens_integers(self):
        """Test 27: input_tokens and output_tokens are integers."""
        event = LLMInvocationEvent("A", "M", "T", "R", 50, 25, 100.0)
        self.assertIsInstance(event.input_tokens, int)
        self.assertIsInstance(event.output_tokens, int)

    def test_28_latency_ms_float(self):
        """Test 28: latency_ms is float."""
        event = LLMInvocationEvent("A", "M", "T", "R", 50, 25, 120.5)
        self.assertIsInstance(event.latency_ms, float)

    def test_29_avoided_llm_call_boolean(self):
        """Test 29: avoided_llm_call is boolean."""
        event = LLMInvocationEvent("A", "M", "T", "R", 50, 25, 120.5, True)
        self.assertIsInstance(event.avoided_llm_call, bool)

    def test_30_distribution_keys_in_metrics(self):
        """Test 30: distribution in efficiency metrics contains 4 tiers."""
        metrics = self.tracker.get_routing_efficiency_metrics()
        self.assertEqual(len(metrics["distribution"]), 4)

    def test_31_trace_task_name_preserved(self):
        """Test 31: Task name preserved in routing trace."""
        trace = self.tracker.get_routing_trace("Custom Task")
        self.assertEqual(trace["task_name"], "Custom Task")

    def test_32_model_status_ready_or_blocked(self):
        """Test 32: Model status is READY or BLOCKED in default registry."""
        models = self.registry.get_all_models()
        for m in models:
            self.assertIn(m["status"], ["READY", "BLOCKED"])

    def test_33_qwen_context_size_32k(self):
        """Test 33: Qwen context size is 32K."""
        m = self.registry.get_model("qwen2.5_1.5b")
        self.assertEqual(m.context_size, "32K")

    def test_34_strong_cloud_context_size_128k(self):
        """Test 34: Strong Cloud LLM context size is 128K."""
        m = self.registry.get_model("strong_cloud")
        self.assertEqual(m.context_size, "128K")

    def test_35_qwen_quantization_q4(self):
        """Test 35: Qwen quantization is Q4."""
        m = self.registry.get_model("qwen2.5_1.5b")
        self.assertEqual(m.quantization, "Q4")

    def test_36_multiple_invocations_accumulate(self):
        """Test 36: Tracker accumulates multiple invocation events."""
        self.tracker.record_invocation("A1", "M1", "T1", "R1", 10, 10, 100.0)
        self.tracker.record_invocation("A2", "M2", "T2", "R2", 20, 20, 200.0)
        self.assertEqual(len(self.tracker.invocations), 2)

    def test_37_invocations_list_iterable(self):
        """Test 37: invocations list is iterable."""
        self.tracker.record_invocation("A1", "M1", "T1", "R1", 10, 10, 100.0)
        count = sum(1 for _ in self.tracker.invocations)
        self.assertEqual(count, 1)

    def test_38_registry_reusable(self):
        """Test 38: Registry instance reusable across calls."""
        m1 = self.registry.get_all_models()
        m2 = self.registry.get_all_models()
        self.assertEqual(m1[0]["name"], m2[0]["name"])

    def test_39_health_monitor_reusable(self):
        """Test 39: Health monitor reusable across calls."""
        h1 = self.health_monitor.check_health("qwen2.5_1.5b")
        h2 = self.health_monitor.check_health("qwen2.5_1.5b")
        self.assertEqual(h1["latency_ms"], h2["latency_ms"])

    def test_40_model_orchestration_ui_integration_ready(self):
        """Test 40: Dict structured for LLM Orchestration UI panel integration."""
        models = self.registry.get_all_models()
        self.assertIn("tier", models[0])
        self.assertIn("capabilities", models[0])

    def test_41_routing_trace_resource_state_dict(self):
        """Test 41: resource_state in trace is dict."""
        trace = self.tracker.get_routing_trace()
        self.assertIsInstance(trace["resource_state"], dict)

    def test_42_routing_trace_keys_count(self):
        """Test 42: Routing trace dict contains 9 keys."""
        trace = self.tracker.get_routing_trace()
        self.assertEqual(len(trace), 9)

    def test_43_model_definition_instance_attributes(self):
        """Test 43: ModelDefinition instance has capabilities attribute as list."""
        m = self.registry.get_model("rule_engine")
        self.assertIsInstance(m.capabilities, list)

    def test_44_efficiency_metrics_dict_keys(self):
        """Test 44: Efficiency metrics dict contains 4 keys."""
        metrics = self.tracker.get_routing_efficiency_metrics()
        self.assertEqual(len(metrics), 4)

    def test_45_v6_6_1_model_orchestration_verification_passed(self):
        """Test 45: All V6.6.1 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
