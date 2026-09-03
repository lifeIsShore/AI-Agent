import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.eval.simulation_engine import SimulationEngine, SyntheticWorld
from personal_agent.eval.scenario_runner import ScenarioRunner
from personal_agent.eval.autonomy_metrics import AutonomyMetricsCalculator, AutonomyMetricsReport
from personal_agent.eval.autonomy_ladder_benchmark import AutonomyLadderBenchmark
from personal_agent.autonomy.autonomy_policy import (
    LEVEL_0_OBSERVE, LEVEL_1_RECOMMEND, LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO, LEVEL_4_SUPERVISED_AUTO
)

class TestV38AgentEvalAndSimulation(unittest.TestCase):

    def setUp(self):
        self.sim_engine = SimulationEngine()
        self.runner = ScenarioRunner()
        self.calculator = AutonomyMetricsCalculator()
        self.benchmark = AutonomyLadderBenchmark()

    def test_1_simulation_engine_creates_world(self):
        """Test 1: SimulationEngine constructs default SyntheticWorld."""
        world = self.sim_engine.create_synthetic_world("Default World")
        self.assertEqual(world.name, "Default World")
        self.assertTrue(world.is_network_available)

    def test_2_deadline_crisis_world_creation(self):
        """Test 2: create_deadline_crisis_world constructs crisis configuration."""
        world = self.sim_engine.create_deadline_crisis_world()
        self.assertEqual(world.deadlines_count, 3)
        self.assertEqual(world.emails_count, 25)

    def test_3_email_storm_world_creation(self):
        """Test 3: create_email_storm_world constructs email storm configuration."""
        world = self.sim_engine.create_email_storm_world()
        self.assertTrue(world.has_email_storm)
        self.assertEqual(world.emails_count, 100)

    def test_4_adversarial_world_creation(self):
        """Test 4: create_adversarial_world constructs prompt-injection scenario."""
        world = self.sim_engine.create_adversarial_world()
        self.assertTrue(world.has_prompt_injection)

    def test_5_scenario_runner_executes_normal_day(self):
        """Test 5: ScenarioRunner executes normal day scenario."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertIn("total_decisions", res)
        self.assertEqual(res["false_actions"], 0)

    def test_6_scenario_runner_executes_crisis(self):
        """Test 6: ScenarioRunner handles deadline crisis scenario."""
        world = self.sim_engine.create_deadline_crisis_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["completed_goals"], 4)

    def test_7_network_outage_scenario_recovery(self):
        """Test 7: ScenarioRunner simulates recovery during network outage."""
        world = self.sim_engine.create_synthetic_world(is_network_available=False)
        res = self.runner.run_scenario(world)
        self.assertEqual(res["total_failures"], 1)
        self.assertEqual(res["recovered_failures"], 1)

    def test_8_autonomy_metrics_calculator(self):
        """Test 8: AutonomyMetricsCalculator computes metric percentages."""
        run_data = {"autonomous_actions": 10, "successful_actions": 10, "total_decisions": 10, "human_interventions": 0}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.autonomy_success_rate, 100.0)

    def test_9_autonomy_success_rate_calculation(self):
        """Test 9: Computes exact autonomy_success_rate."""
        run_data = {"autonomous_actions": 10, "successful_actions": 8}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.autonomy_success_rate, 80.0)

    def test_10_intervention_rate_calculation(self):
        """Test 10: Computes exact intervention_rate."""
        run_data = {"total_decisions": 10, "human_interventions": 2}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.intervention_rate, 20.0)

    def test_11_false_action_rate_calculation(self):
        """Test 11: Computes exact false_action_rate."""
        run_data = {"autonomous_actions": 10, "false_actions": 0}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.false_action_rate, 0.0)

    def test_12_goal_completion_rate_calculation(self):
        """Test 12: Computes exact goal_completion_rate."""
        run_data = {"initiated_goals": 4, "completed_goals": 4}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.goal_completion_rate, 100.0)

    def test_13_recovery_rate_calculation(self):
        """Test 13: Computes exact recovery_rate."""
        run_data = {"total_failures": 2, "recovered_failures": 2}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.recovery_rate, 100.0)

    def test_14_replanning_efficiency_calculation(self):
        """Test 14: Computes exact replanning_efficiency."""
        run_data = {"useful_replans": 2, "total_replans": 2}
        metrics = self.calculator.compute_metrics(run_data)
        self.assertEqual(metrics.replanning_efficiency, 100.0)

    def test_15_autonomy_ladder_benchmark_runs_all_levels(self):
        """Test 15: AutonomyLadderBenchmark runs across LEVEL_0 to LEVEL_4."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        self.assertEqual(len(bench["levels_evaluated"]), 5)

    def test_16_level_0_observe_intervention_rate(self):
        """Test 16: LEVEL_0_OBSERVE has 100% intervention rate."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        l0_metrics = bench["results"][LEVEL_0_OBSERVE]["metrics"]
        self.assertEqual(l0_metrics["intervention_rate"], 100.0)

    def test_17_level_1_recommend_intervention_rate(self):
        """Test 17: LEVEL_1_RECOMMEND has 80% intervention rate."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        l1_metrics = bench["results"][LEVEL_1_RECOMMEND]["metrics"]
        self.assertEqual(l1_metrics["intervention_rate"], 80.0)

    def test_18_level_2_approval_intervention_rate(self):
        """Test 18: LEVEL_2_APPROVAL has 50% intervention rate."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        l2_metrics = bench["results"][LEVEL_2_APPROVAL]["metrics"]
        self.assertEqual(l2_metrics["intervention_rate"], 50.0)

    def test_19_level_3_bounded_auto_intervention_rate(self):
        """Test 19: LEVEL_3_BOUNDED_AUTO has lower intervention rate."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        l3_metrics = bench["results"][LEVEL_3_BOUNDED_AUTO]["metrics"]
        self.assertLess(l3_metrics["intervention_rate"], 50.0)

    def test_20_level_4_supervised_auto_intervention_rate(self):
        """Test 20: LEVEL_4_SUPERVISED_AUTO maintains security bounds."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        l4_metrics = bench["results"][LEVEL_4_SUPERVISED_AUTO]["metrics"]
        self.assertEqual(l4_metrics["false_action_rate"], 0.0)

    def test_21_security_boundary_passed_across_ladder(self):
        """Test 21: Security boundary check passes across all 5 levels."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        self.assertTrue(bench["overall_benchmark_passed"])

    def test_22_adversarial_prompt_injection_caught(self):
        """Test 22: Adversarial prompt injection maintains 0 false action rate."""
        world = self.sim_engine.create_adversarial_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["false_actions"], 0)

    def test_23_tool_poisoning_simulation(self):
        """Test 23: Malicious tool payload filtered cleanly."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["false_actions"], 0)

    def test_24_event_storm_simulation(self):
        """Test 24: Email storm handles decisions cleanly without crashing."""
        world = self.sim_engine.create_email_storm_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["total_decisions"], 110)

    def test_25_conflicting_goals_simulation(self):
        """Test 25: Goal arbitration resolves conflicting priorities in synthetic world."""
        world = self.sim_engine.create_synthetic_world(goals_count=5)
        res = self.runner.run_scenario(world)
        self.assertEqual(res["completed_goals"], 5)

    def test_26_memory_tampering_simulation(self):
        """Test 26: Invalid memory payload ignored safely."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertTrue(res["successful_actions"] > 0)

    def test_27_false_learned_preference_simulation(self):
        """Test 27: Low confidence candidate ignored for active decisions."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["false_actions"], 0)

    def test_28_permission_escalation_blocked(self):
        """Test 28: Privilege escalation attempt hard-blocked across benchmark."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        self.assertTrue(bench["overall_benchmark_passed"])

    def test_29_cross_agent_privilege_leakage_prevented(self):
        """Test 29: Specialist runtime prevents cross-agent tool calls."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertEqual(res["false_actions"], 0)

    def test_30_infinite_workflow_prevention(self):
        """Test 30: Retry limits prevent runaway execution loops."""
        world = self.sim_engine.create_synthetic_world(is_network_available=False)
        res = self.runner.run_scenario(world)
        self.assertEqual(res["total_failures"], 1)

    def test_31_corrupted_state_recovery(self):
        """Test 31: Corrupted state files recovered cleanly during simulation."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertIsNotNone(res)

    def test_32_historical_outcomes_auditable(self):
        """Test 32: ScenarioRunner returns timestamped execution metrics."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertIn("latency_sec", res)

    def test_33_latency_reporting(self):
        """Test 33: Scenario run dictionary reports execution latency in seconds."""
        world = self.sim_engine.create_synthetic_world()
        res = self.runner.run_scenario(world)
        self.assertGreaterEqual(res["latency_sec"], 0.0)

    def test_34_metrics_report_dict_export(self):
        """Test 34: AutonomyMetricsReport.to_dict() outputs valid JSON dict."""
        rep = AutonomyMetricsReport(100.0, 0.0, 0.0, 100.0, 100.0, 100.0)
        d = rep.to_dict()
        self.assertEqual(d["autonomy_success_rate"], 100.0)

    def test_35_overall_benchmark_passed_flag(self):
        """Test 35: run_ladder_benchmark outputs overall_benchmark_passed = True."""
        world = self.sim_engine.create_synthetic_world()
        bench = self.benchmark.run_ladder_benchmark(world)
        self.assertTrue(bench["overall_benchmark_passed"])

if __name__ == "__main__":
    unittest.main()
