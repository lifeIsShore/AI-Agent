import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.workflow.models import Workflow, WorkflowStep, WF_CREATED, WF_RUNNING, WF_COMPLETED, STEP_COMPLETED
from personal_agent.workflow.dag import WorkflowDAG
from personal_agent.workflow.verification import StepVerifier, VERIFIED_STATUS_VERIFIED, VERIFIED_STATUS_INCONSISTENT
from personal_agent.workflow.replanner import WorkflowReplanner

class TestV22WorkflowIntelligence(unittest.TestCase):

    def setUp(self):
        self.dag = WorkflowDAG()
        self.verifier = StepVerifier()
        self.replanner = WorkflowReplanner()

    def test_workflow_models_and_state_machine(self):
        """Test Workflow and WorkflowStep deterministic state machine transitions."""
        step = WorkflowStep(step_id="s1", objective="Inspect calendar")
        wf = Workflow(workflow_id="wf_001", objective="Study preparation", steps=[step])

        self.assertEqual(wf.status, WF_CREATED)
        wf.update_status(WF_RUNNING)
        self.assertEqual(wf.status, WF_RUNNING)

        step.mark_completed({"events_found": 2})
        self.assertEqual(step.status, STEP_COMPLETED)

    def test_dag_dependency_resolution(self):
        """Test WorkflowDAG resolves dependency graph readiness accurately."""
        s1 = WorkflowStep(step_id="s1", objective="Inspect calendar")
        s2 = WorkflowStep(step_id="s2", objective="Inspect emails")
        s3 = WorkflowStep(step_id="s3", objective="Create schedule", dependencies=["s1", "s2"])

        wf = Workflow(workflow_id="wf_dag_1", objective="Planning", steps=[s1, s2, s3])

        ready1 = self.dag.get_ready_steps(wf)
        self.assertEqual(len(ready1), 2)  # s1 and s2 ready in parallel
        self.assertNotIn(s3, ready1)

        # Mark s1 completed
        s1.mark_completed()
        ready2 = self.dag.get_ready_steps(wf)
        self.assertEqual(len(ready2), 1)  # s2 ready

        # Mark s2 completed
        s2.mark_completed()
        ready3 = self.dag.get_ready_steps(wf)
        self.assertEqual(len(ready3), 1)  # s3 now ready
        self.assertEqual(ready3[0].step_id, "s3")

    def test_checkpoint_recovery_zero_reexecution(self):
        """Test checkpoint restoration restores completed steps without re-execution."""
        s1 = WorkflowStep(step_id="s1", objective="Step 1", status=STEP_COMPLETED, output_result={"data": 123})
        s2 = WorkflowStep(step_id="s2", objective="Step 2", dependencies=["s1"])
        wf = Workflow(workflow_id="wf_cp_test", objective="Checkpoint test", steps=[s1, s2])

        # Save checkpoint to disk
        self.dag.checkpoint_workflow(wf)

        # Restore checkpoint
        restored = self.dag.restore_workflow_checkpoint("wf_cp_test")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.steps[0].status, STEP_COMPLETED)
        self.assertEqual(restored.steps[0].output_result["data"], 123)

        # s2 is ready, s1 is already completed (0 re-execution)
        ready = self.dag.get_ready_steps(restored)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].step_id, "s2")

    def test_step_verifier_post_execution_check(self):
        """Test StepVerifier validates actual execution output against expected state."""
        step = WorkflowStep(step_id="s1", objective="Create event")
        actual_output = {"event_id": "ev_99", "status": "confirmed"}
        expected_state = {"status": "confirmed"}

        res = self.verifier.verify_step_execution(step, actual_output, expected_state)
        self.assertTrue(res.verified)
        self.assertEqual(res.status, VERIFIED_STATUS_VERIFIED)

        # Mismatched expected state
        bad_expected = {"status": "cancelled"}
        res_bad = self.verifier.verify_step_execution(step, actual_output, bad_expected)
        self.assertFalse(res_bad.verified)
        self.assertEqual(res_bad.status, VERIFIED_STATUS_INCONSISTENT)

    def test_workflow_replanner_conflict_handling(self):
        """Test WorkflowReplanner adjusts remaining pending steps without resetting completed steps."""
        s1 = WorkflowStep(step_id="s1", objective="Read calendar", status=STEP_COMPLETED)
        s2 = WorkflowStep(step_id="s2", objective="Study accounting")
        wf = Workflow(workflow_id="wf_replan", objective="Study", steps=[s1, s2])

        conflict_event = {"summary": "Urgent lecture change"}
        has_conflict = self.replanner.detect_conflict(wf, conflict_event)
        self.assertTrue(has_conflict)

        replanned_wf, msg = self.replanner.replan_uncompleted_steps(wf, conflict_event)
        self.assertEqual(s1.status, STEP_COMPLETED) # Preserved!
        self.assertIn("Replanned", s2.objective)

if __name__ == "__main__":
    unittest.main()
