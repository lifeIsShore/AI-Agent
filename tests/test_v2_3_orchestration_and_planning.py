import sys
import os
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.orchestration.planner import ExecutionPlanner, ExecutionPlan
from personal_agent.orchestration.roles import ROLE_INBOX_ANALYST, ROLE_CALENDAR_PLANNER
from personal_agent.orchestration.executor import ParallelExecutor
from personal_agent.orchestration.router import ToolRouter
from personal_agent.orchestration.validator import PlanValidator
from personal_agent.orchestration.budget import WorkflowBudget

class TestV23OrchestrationAndPlanning(unittest.TestCase):

    def setUp(self):
        self.planner = ExecutionPlanner()
        self.executor = ParallelExecutor()
        self.router = ToolRouter()
        self.validator = PlanValidator()
        self.budget = WorkflowBudget(max_tokens=500, max_cost_eur=0.05)

    def test_execution_planner_and_roles(self):
        """Test ExecutionPlanner creates valid ExecutionPlan with specialist role assignments."""
        plan = self.planner.create_execution_plan("Plan my day")

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertGreaterEqual(len(plan.steps), 4)
        self.assertEqual(plan.steps[0]["role"], ROLE_INBOX_ANALYST)
        self.assertEqual(plan.steps[1]["role"], ROLE_CALENDAR_PLANNER)
        self.assertEqual(len(plan.parallel_groups), 2)

    def test_parallel_executor_latency_speedup(self):
        """Test ParallelExecutor runs ready steps concurrently and measures latency speedup."""
        def task_a(): time.sleep(0.015); return "A"
        def task_b(): time.sleep(0.015); return "B"

        group = [("step_a", task_a), ("step_b", task_b)]
        res = self.executor.execute_parallel_group(group)

        self.assertIsNotNone(res)
        self.assertEqual(res["results"]["step_a"]["output"], "A")
        self.assertEqual(res["results"]["step_b"]["output"], "B")
        self.assertGreaterEqual(res["speedup_ratio"], 1.0)

    def test_tool_router_capability_resolution(self):
        """Test ToolRouter resolves tools deterministically based on capability matching."""
        success, tool_name, reason = self.router.resolve_tool_for_capability("gmail.read")
        self.assertTrue(success)
        self.assertEqual(tool_name, "list_recent_emails")

        # Test overriding unauthorized tool proposal
        success_ov, tool_ov, reason_ov = self.router.resolve_tool_for_capability("gmail.read", requested_tool="delete_all")
        self.assertTrue(success_ov)
        self.assertEqual(tool_ov, "list_recent_emails")
        self.assertIn("Override", reason_ov)

    def test_plan_validator_structural_and_security_checks(self):
        """Test PlanValidator validates plan structures and blocks forbidden capabilities."""
        plan = self.planner.create_execution_plan("Plan my day")
        res = self.validator.validate_plan(plan, self.budget)
        self.assertTrue(res.valid)

        # Test forbidden capability plan
        bad_plan = self.planner.create_execution_plan("Malicious plan")
        bad_plan.steps.append({"step_id": "bad", "required_capability": "system.admin", "dependencies": []})

        res_bad = self.validator.validate_plan(bad_plan, self.budget)
        self.assertFalse(res_bad.valid)
        self.assertIn("Forbidden capability", res_bad.reason)

    def test_workflow_budget_enforcement(self):
        """Test WorkflowBudget halts execution safely when resource limits are exceeded."""
        b = WorkflowBudget(max_tokens=100)
        ok, msg = b.record_usage(tokens=50)
        self.assertTrue(ok)

        ok_exceed, msg_exceed = b.record_usage(tokens=60)
        self.assertFalse(ok_exceed)
        self.assertIn("SAFE_STOP", msg_exceed)

if __name__ == "__main__":
    unittest.main()
