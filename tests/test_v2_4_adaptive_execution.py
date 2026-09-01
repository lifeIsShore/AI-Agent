import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.workflow.models import Workflow, WorkflowStep, WF_CANCELLED, STEP_COMPLETED
from personal_agent.orchestration.coordinator import WorkflowCoordinator
from personal_agent.orchestration.recovery_strategy import FailureClassifier, WorkflowRecoveryEngine, FAIL_RATE_LIMITED, FAIL_PERMISSION_DENIED
from personal_agent.orchestration.resource_manager import ResourceManager
from personal_agent.orchestration.budget import WorkflowBudget
from personal_agent.orchestration.dynamic_router import DynamicStepRouter, StepContextIsolator, MODEL_TIER_REMOTE_LARGE, MODEL_TIER_LOCAL_SMALL
from personal_agent.orchestration.roles import ROLE_INBOX_ANALYST

class TestV24AdaptiveExecution(unittest.TestCase):

    def setUp(self):
        self.coordinator = WorkflowCoordinator()
        self.classifier = FailureClassifier()
        self.recovery = WorkflowRecoveryEngine()
        self.resource_mgr = ResourceManager(WorkflowBudget(max_tokens=1000, max_cost_eur=0.10))
        self.step_router = DynamicStepRouter()
        self.isolator = StepContextIsolator()

    def test_workflow_coordinator_state_and_cancellation(self):
        """Test WorkflowCoordinator manages next-step actions and targeted workflow cancellation."""
        s1 = WorkflowStep(step_id="s1", objective="Step 1")
        wf = Workflow(workflow_id="wf_coord_1", objective="Test coord", steps=[s1])
        self.coordinator.register_workflow(wf)

        action, ready_steps = self.coordinator.determine_next_action("wf_coord_1")
        self.assertEqual(action, "EXECUTE_PARALLEL_STEPS")
        self.assertEqual(len(ready_steps), 1)

        # Test targeted cancellation
        cancel_ok, msg = self.coordinator.cancel_workflow("wf_coord_1")
        self.assertTrue(cancel_ok)
        self.assertEqual(wf.status, WF_CANCELLED)

    def test_failure_classifier_and_recovery_policy(self):
        """Test FailureClassifier distinguishes HTTP 429 (retry) from HTTP 403 (stop immediately)."""
        step = WorkflowStep(step_id="s1", objective="Step 1")
        
        f1, act1, retry1 = self.recovery.handle_step_failure(step, "HTTP 429 Too Many Requests")
        self.assertEqual(f1, FAIL_RATE_LIMITED)
        self.assertTrue(retry1)
        self.assertEqual(act1, "RETRY_WITH_BACKOFF")

        f2, act2, retry2 = self.recovery.handle_step_failure(step, "HTTP 403 Forbidden - Permission Denied")
        self.assertEqual(f2, FAIL_PERMISSION_DENIED)
        self.assertFalse(retry2)
        self.assertEqual(act2, "STOP_NO_RETRY")

    def test_resource_manager_reservation_and_commit(self):
        """Test ResourceManager reservation, commit, and budget overflow rejection."""
        ok_res, res_id, msg_res = self.resource_mgr.reserve("wf_1", est_tokens=500, est_cost=0.01)
        self.assertTrue(ok_res)
        self.assertTrue(res_id.startswith("res_"))

        ok_commit, msg_commit = self.resource_mgr.commit(res_id, actual_tokens=450, actual_cost=0.009, actual_runtime=0.5)
        self.assertTrue(ok_commit)

        # Test budget overflow rejection
        ok_bad, res_bad, msg_bad = self.resource_mgr.reserve("wf_1", est_tokens=800, est_cost=0.05)
        self.assertFalse(ok_bad)
        self.assertIn("rejected", msg_bad)

    def test_dynamic_step_router_escalation(self):
        """Test DynamicStepRouter escalates low confidence or high risk steps to remote-large."""
        tier1, reason1 = self.step_router.route_step_model("step_1", confidence=0.92, risk_level="LOW")
        self.assertEqual(tier1, MODEL_TIER_LOCAL_SMALL)

        tier2, reason2 = self.step_router.route_step_model("step_2", confidence=0.55, risk_level="HIGH")
        self.assertEqual(tier2, MODEL_TIER_REMOTE_LARGE)

    def test_step_context_isolator_role_scoping(self):
        """Test StepContextIsolator strips unrelated context for specialist roles."""
        full_ctx = {
            "emails": [{"id": "m1"}],
            "calendar_events": [{"id": "ev1"}],
            "financial_docs": [{"id": "fin1"}]
        }
        filtered = self.isolator.filter_context_for_role(ROLE_INBOX_ANALYST, full_ctx)

        self.assertIn("emails", filtered)
        self.assertNotIn("financial_docs", filtered)
        self.assertNotIn("calendar_events", filtered)

if __name__ == "__main__":
    unittest.main()
