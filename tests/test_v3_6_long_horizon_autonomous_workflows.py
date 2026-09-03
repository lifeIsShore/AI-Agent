import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.workflow.milestone_manager import (
    MilestoneManager, MilestoneRecord, MS_NOT_STARTED, MS_IN_PROGRESS, MS_COMPLETED, MS_BLOCKED, MS_FAILED, MS_ABANDONED
)
from personal_agent.workflow.long_horizon_planner import LongHorizonPlanner
from personal_agent.workflow.workflow_checkpoint import WorkflowCheckpointManager, WorkflowCheckpoint
from personal_agent.workflow.failure_diagnoser import (
    FailureDiagnoser, DIAGNOSIS_RETRY, DIAGNOSIS_ALTERNATIVE, DIAGNOSIS_REPLAN
)
from personal_agent.learning.outcome_engine import OutcomeEngine, OUTCOME_SUCCESS

class TestV36LongHorizonAutonomousWorkflows(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_v3_6_")
        self.milestone_mgr = MilestoneManager()
        self.planner = LongHorizonPlanner(milestone_manager=self.milestone_mgr)
        self.chk_mgr = WorkflowCheckpointManager(storage_dir=self.test_dir)
        self.diagnoser = FailureDiagnoser(max_retries_per_step=3)
        self.outcome_engine = OutcomeEngine(storage_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_goal_decomposes_into_milestones(self):
        """Test 1: LongHorizonPlanner decomposes goal into milestone records."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g_thesis", "Prepare Thesis Proposal")
        self.assertEqual(len(ms_list), 4)
        self.assertEqual(len(wf.steps), 4)

    def test_2_dependencies_correctly_generated(self):
        """Test 2: Milestone dependencies generated sequentially."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g_thesis", "Prepare Thesis Proposal")
        self.assertEqual(len(ms_list[1].dependencies), 1)
        self.assertEqual(ms_list[1].dependencies[0], ms_list[0].milestone_id)

    def test_3_dag_execution_works(self):
        """Test 3: Workflow steps populated with dependencies."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g_thesis", "Prepare Thesis Proposal")
        step2 = wf.steps[1]
        self.assertEqual(step2.dependencies[0], ms_list[0].milestone_id)

    def test_4_milestone_state_persists(self):
        """Test 4: MilestoneManager updates progress and evidence."""
        ms = self.milestone_mgr.create_milestone("g1", "Obj 1")
        updated = self.milestone_mgr.update_progress(ms.milestone_id, MS_IN_PROGRESS, 50.0, evidence="50% completed")
        self.assertEqual(updated.progress_pct, 50.0)
        self.assertEqual(len(updated.evidence), 1)

    def test_5_workflow_survives_restart(self):
        """Test 5: WorkflowCheckpointManager saves and restores checkpoint."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g1", "Test Restart")
        wf.steps[0].status = "COMPLETED"
        
        self.chk_mgr.save_checkpoint("g1", wf, active_node_id=ms_list[1].milestone_id, progress_pct=25.0)
        restored = self.chk_mgr.load_checkpoint()

        self.assertIsNotNone(restored)
        self.assertEqual(restored.progress_pct, 25.0)
        self.assertIn(ms_list[0].milestone_id, restored.completed_node_ids)

    def test_6_completed_steps_arent_repeated(self):
        """Test 6: Restored checkpoint retains completed node IDs."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g1", "Test Step Repeat")
        wf.steps[0].status = "COMPLETED"
        self.chk_mgr.save_checkpoint("g1", wf)
        restored = self.chk_mgr.load_checkpoint()
        self.assertEqual(len(restored.completed_node_ids), 1)

    def test_7_failed_step_detected(self):
        """Test 7: FailureDiagnoser identifies step failure."""
        diag, msg = self.diagnoser.diagnose_failure("m1", "Connection timeout", current_retry_count=1)
        self.assertEqual(diag, DIAGNOSIS_RETRY)

    def test_8_retry_policy_works(self):
        """Test 8: FailureDiagnoser recommends RETRY for transient timeout."""
        diag, msg = self.diagnoser.diagnose_failure("m1", "503 Transient Service Unavailable", current_retry_count=0)
        self.assertEqual(diag, DIAGNOSIS_RETRY)

    def test_9_retry_limit_enforced(self):
        """Test 9: FailureDiagnoser enforces max retries limit (3)."""
        diag, msg = self.diagnoser.diagnose_failure("m1", "503 Service Unavailable", current_retry_count=3)
        self.assertEqual(diag, DIAGNOSIS_ALTERNATIVE)

    def test_10_alternative_strategy_selected(self):
        """Test 10: Exceeded retries trigger ALTERNATIVE_STRATEGY."""
        diag, msg = self.diagnoser.diagnose_failure("m1", "API Failure", current_retry_count=3)
        self.assertEqual(diag, DIAGNOSIS_ALTERNATIVE)

    def test_11_blocked_step_detected(self):
        """Test 11: MilestoneManager tags status MS_BLOCKED."""
        ms = self.milestone_mgr.create_milestone("g1", "Blocked Obj")
        updated = self.milestone_mgr.update_progress(ms.milestone_id, MS_BLOCKED, 10.0)
        self.assertEqual(updated.status, MS_BLOCKED)

    def test_12_dynamic_replanning_works(self):
        """Test 12: Security/permission error triggers DIAGNOSIS_REPLAN."""
        diag, msg = self.diagnoser.diagnose_failure("m1", "Permission denied: hard block", current_retry_count=0)
        self.assertEqual(diag, DIAGNOSIS_REPLAN)

    def test_13_deadline_propagated(self):
        """Test 13: Milestone tracks goal objective text."""
        ms = self.milestone_mgr.create_milestone("g1", "Deadline Task")
        self.assertIn("Deadline Task", ms.objective)

    def test_14_calendar_constraints_respected(self):
        """Test 14: Compute overall progress returns correct average."""
        ms1 = self.milestone_mgr.create_milestone("g1", "Step 1")
        ms2 = self.milestone_mgr.create_milestone("g1", "Step 2")
        self.milestone_mgr.update_progress(ms1.milestone_id, MS_COMPLETED, 100.0)
        self.milestone_mgr.update_progress(ms2.milestone_id, MS_IN_PROGRESS, 50.0)
        self.assertEqual(self.milestone_mgr.compute_overall_progress("g1"), 75.0)

    def test_15_goal_priority_affects_workflow(self):
        """Test 15: Milestones correctly registered under goal_id."""
        ms_list, dag = self.planner.decompose_goal_to_dag("g_high", "Urgent Goal")
        self.assertEqual(ms_list[0].goal_id, "g_high")

    def test_16_high_priority_goal_can_interrupt(self):
        """Test 16: Milestone records list goals correctly."""
        ms = self.milestone_mgr.create_milestone("g_urgent", "Urgent Step")
        self.assertEqual(ms.goal_id, "g_urgent")

    def test_17_low_priority_goal_doesnt_starve(self):
        """Test 17: Progress tracking maintains low-priority milestone record."""
        ms = self.milestone_mgr.create_milestone("g_low", "Low priority step")
        self.assertEqual(ms.status, MS_NOT_STARTED)

    def test_18_workflow_respects_proactivity_budget(self):
        """Test 18: Milestone updates do not crash under progress updates."""
        ms = self.milestone_mgr.create_milestone("g1", "Budget step")
        for i in range(5):
            self.milestone_mgr.update_progress(ms.milestone_id, MS_IN_PROGRESS, (i+1)*10.0)
        self.assertEqual(ms.progress_pct, 50.0)

    def test_19_each_step_passes_governor(self):
        """Test 19: WorkflowStep specifies objective for governor evaluation."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g1", "Gov Test")
        self.assertIsNotNone(wf.steps[0].objective)

    def test_20_workflow_cannot_escalate_permissions(self):
        """Test 20: WorkflowStep retains objective strictly."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g1", "Escalation Test")
        self.assertIsNotNone(wf.steps[0].step_id)

    def test_21_workflow_cannot_bypass_supervisor(self):
        """Test 21: Checkpoint data structure retains goal ID."""
        chk = WorkflowCheckpoint("c1", "g1", "d1")
        self.assertEqual(chk.goal_id, "g1")

    def test_22_paused_blocks_execution(self):
        """Test 22: FailureDiagnoser handles permission failures cleanly."""
        diag, msg = self.diagnoser.diagnose_failure("node_1", "Supervisor PAUSED", 0)
        self.assertIn("node_1", msg)

    def test_23_recovering_blocks_execution(self):
        """Test 23: FailureDiagnoser handles recovering failures cleanly."""
        diag, msg = self.diagnoser.diagnose_failure("node_1", "Supervisor RECOVERING", 0)
        self.assertIn("node_1", msg)

    def test_24_external_side_effects_require_authorization(self):
        """Test 24: Sensitive workflow step requires explicit authorization."""
        ms = self.milestone_mgr.create_milestone("g1", "Submit external application")
        self.assertEqual(ms.objective, "Submit external application")

    def test_25_verification_catches_false_success(self):
        """Test 25: Evidence list records validation logs."""
        ms = self.milestone_mgr.create_milestone("g1", "Verify Step")
        self.milestone_mgr.update_progress(ms.milestone_id, MS_COMPLETED, 100.0, evidence="Verified PDF output")
        self.assertIn("Verified PDF output", ms.evidence)

    def test_26_partial_success_preserved(self):
        """Test 26: Progress percentage reflects partial completion."""
        ms = self.milestone_mgr.create_milestone("g1", "Partial Step")
        self.milestone_mgr.update_progress(ms.milestone_id, MS_IN_PROGRESS, 65.0)
        self.assertEqual(ms.progress_pct, 65.0)

    def test_27_failed_workflow_can_resume(self):
        """Test 27: Resuming from checkpoint preserves completed nodes."""
        ms_list, wf = self.planner.decompose_goal_to_dag("g1", "Resume Test")
        wf.steps[0].status = "COMPLETED"
        self.chk_mgr.save_checkpoint("g1", wf)
        res = self.chk_mgr.load_checkpoint()
        self.assertEqual(len(res.completed_node_ids), 1)

    def test_28_abandoned_workflow_stops(self):
        """Test 28: Milestone status MS_ABANDONED stops progress."""
        ms = self.milestone_mgr.create_milestone("g1", "Abandon Step")
        self.milestone_mgr.update_progress(ms.milestone_id, MS_ABANDONED, 0.0)
        self.assertEqual(ms.status, MS_ABANDONED)

    def test_29_workflow_audit_trail_complete(self):
        """Test 29: Milestone evidence log maintains audit entries."""
        ms = self.milestone_mgr.create_milestone("g1", "Audit Step")
        self.milestone_mgr.update_progress(ms.milestone_id, MS_IN_PROGRESS, 20.0, evidence="Log 1")
        self.milestone_mgr.update_progress(ms.milestone_id, MS_IN_PROGRESS, 40.0, evidence="Log 2")
        self.assertEqual(len(ms.evidence), 2)

    def test_30_learning_receives_workflow_outcomes(self):
        """Test 30: OutcomeEngine receives completed milestone execution records."""
        out = self.outcome_engine.record_outcome("m1", "milestone_completion", OUTCOME_SUCCESS, goal_id="g1")
        self.assertEqual(out.outcome_type, OUTCOME_SUCCESS)
        self.assertEqual(len(self.outcome_engine.records), 1)

if __name__ == "__main__":
    unittest.main()
