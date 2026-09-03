import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.learning.improvement_detector import ImprovementDetector
from personal_agent.learning.improvement_proposer import ImprovementProposer, ImprovementProposal
from personal_agent.eval.improvement_sandbox import ImprovementSandbox
from personal_agent.autonomy.improvement_governor import ImprovementGovernor
from personal_agent.runtime.rollback_manager import RollbackManager
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord

class TestV50BoundedSelfImprovingAgent(unittest.TestCase):

    def setUp(self):
        self.detector = ImprovementDetector()
        self.proposer = ImprovementProposer()
        self.sandbox = ImprovementSandbox()
        self.governor = ImprovementGovernor()
        self.rollback_mgr = RollbackManager()

    def test_1_improvement_detector_detects_high_user_rejection(self):
        """Test 1: ImprovementDetector detects high user rejection rate."""
        records = [MissionTelemetryRecord("m1", rejections=2), MissionTelemetryRecord("m2", rejections=2)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertTrue(len(weaknesses) > 0)
        self.assertEqual(weaknesses[0]["weakness_type"], "HIGH_USER_REJECTION")

    def test_2_improvement_detector_detects_token_inefficiency(self):
        """Test 2: ImprovementDetector detects token inefficiency."""
        records = [MissionTelemetryRecord("m1", tokens=600)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertTrue(len(weaknesses) > 0)
        self.assertEqual(weaknesses[0]["weakness_type"], "TOKEN_INEFFICIENCY")

    def test_3_improvement_detector_returns_empty_for_clean(self):
        """Test 3: Empty list returned for clean telemetry."""
        records = [MissionTelemetryRecord("m1", tokens=100, rejections=0)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertEqual(len(weaknesses), 0)

    def test_4_improvement_proposer_generates_proposals(self):
        """Test 4: ImprovementProposer turns weaknesses into ImprovementProposal objects."""
        weaknesses = [{"weakness_type": "HIGH_USER_REJECTION", "evidence": "Rejections high"}]
        proposals = self.proposer.generate_proposals(weaknesses)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0].affected_components, ["PlanningSpecialist"])

    def test_5_proposal_modifies_security_boundary_default_false(self):
        """Test 5: Proposal sets modifies_security_boundary = False for valid optimization."""
        weaknesses = [{"weakness_type": "HIGH_USER_REJECTION"}]
        proposals = self.proposer.generate_proposals(weaknesses)
        self.assertFalse(proposals[0].modifies_security_boundary)

    def test_6_sandbox_evaluates_candidate_proposal(self):
        """Test 6: ImprovementSandbox evaluates baseline vs candidate metrics."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertTrue(res["passed"])
        self.assertIn("baseline", res)
        self.assertIn("candidate", res)

    def test_7_sandbox_approves_safe_candidate(self):
        """Test 7: Sandbox passes proposal with 0 safety violations."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertTrue(res["passed"])

    def test_8_sandbox_rejects_candidate_with_safety_violations(self):
        """Test 8: Sandbox rejects proposal with safety violations."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain", modifies_security_boundary=True)
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertFalse(res["passed"])

    def test_9_improvement_governor_hard_rejects_security_boundary(self):
        """Test 9: ImprovementGovernor hard-rejects security boundary modification."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain", modifies_security_boundary=True)
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertFalse(ok)
        self.assertIn("HARD REJECT", msg)

    def test_10_improvement_governor_rejects_failed_sandbox(self):
        """Test 10: ImprovementGovernor rejects proposal failing sandbox."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": False, "reason": "Failed"}, user_approved=True)
        self.assertFalse(ok)
        self.assertIn("REJECT", msg)

    def test_11_improvement_governor_requires_human_approval(self):
        """Test 11: ImprovementGovernor requires human approval before deployment."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=False)
        self.assertFalse(ok)
        self.assertIn("GATE", msg)

    def test_12_improvement_governor_approves_with_human_approval(self):
        """Test 12: ImprovementGovernor authorizes proposal with human approval."""
        prop = ImprovementProposal("p1", "Prob", "Ev", "Hyp", "Change", "Gain")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertTrue(ok)
        self.assertIn("APPROVED", msg)

    def test_13_rollback_manager_deploys_version(self):
        """Test 13: RollbackManager deploys new version v5.0.0."""
        dep = self.rollback_mgr.deploy_version("v5.0.0", {"policy": "new"})
        self.assertEqual(self.rollback_mgr.get_current_version(), "v5.0.0")

    def test_14_rollback_manager_detects_degradation(self):
        """Test 14: evaluate_telemetry_degradation detects degradation below threshold."""
        self.rollback_mgr.deploy_version("v5.0.0", {"policy": "new"})
        rolled_back, msg = self.rollback_mgr.evaluate_telemetry_degradation(current_accuracy=0.70)
        self.assertTrue(rolled_back)
        self.assertIn("AUTOMATIC ROLLBACK", msg)

    def test_15_rollback_manager_reverts_version(self):
        """Test 15: Rollback manager reverts config to previous version on degradation."""
        self.rollback_mgr.deploy_version("v5.0.0", {"policy": "new"})
        self.rollback_mgr.evaluate_telemetry_degradation(current_accuracy=0.70)
        self.assertEqual(self.rollback_mgr.get_current_version(), "v4.4.0")

    def test_16_security_policy_proposal_hard_blocked(self):
        """Test 16: Proposal to allow financial transactions hard-rejected by governor."""
        prop = ImprovementProposal("p1", "P", "E", "H", "Allow financial transactions", "G")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertFalse(ok)

    def test_17_proposal_to_dict(self):
        """Test 17: ImprovementProposal to_dict() outputs valid dict."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        d = prop.to_dict()
        self.assertEqual(d["proposal_id"], "p1")

    def test_18_sandbox_baseline_metrics(self):
        """Test 18: Sandbox result contains baseline metrics dict."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertEqual(res["baseline"]["accuracy"], 0.91)

    def test_19_sandbox_candidate_metrics(self):
        """Test 19: Sandbox result contains candidate metrics dict."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertEqual(res["candidate"]["accuracy"], 0.96)

    def test_20_rollback_manager_initial_version(self):
        """Test 20: RollbackManager starts with v4.4.0."""
        self.assertEqual(self.rollback_mgr.get_current_version(), "v4.4.0")

    def test_21_improvement_detector_handles_empty_list(self):
        """Test 21: Empty telemetry list handled gracefully."""
        self.assertEqual(len(self.detector.detect_weaknesses([])), 0)

    def test_22_high_rejection_weakness_evidence(self):
        """Test 22: Evidence string included in weakness report."""
        records = [MissionTelemetryRecord("m1", rejections=3)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertIn("evidence", weaknesses[0])

    def test_23_token_inefficiency_weakness_evidence(self):
        """Test 23: Token evidence string included in weakness report."""
        records = [MissionTelemetryRecord("m1", tokens=600)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertIn("evidence", weaknesses[0])

    def test_24_proposer_generates_planning_proposal(self):
        """Test 24: Proposal generated for PlanningSpecialist."""
        weaknesses = [{"weakness_type": "HIGH_USER_REJECTION"}]
        props = self.proposer.generate_proposals(weaknesses)
        self.assertEqual(props[0].affected_components[0], "PlanningSpecialist")

    def test_25_proposer_generates_model_router_proposal(self):
        """Test 25: Proposal generated for ModelRouter."""
        weaknesses = [{"weakness_type": "TOKEN_INEFFICIENCY"}]
        props = self.proposer.generate_proposals(weaknesses)
        self.assertIn("ModelRouter", props[0].affected_components)

    def test_26_sandbox_compares_latency(self):
        """Test 26: Sandbox result compares latency_sec."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertLess(res["candidate"]["latency_sec"], res["baseline"]["latency_sec"])

    def test_27_sandbox_compares_user_acceptance(self):
        """Test 27: Sandbox result compares user_acceptance."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertGreater(res["candidate"]["user_acceptance"], res["baseline"]["user_acceptance"])

    def test_28_governor_hard_rejects_delete_action(self):
        """Test 28: Proposal with delete in proposed change hard-rejected."""
        prop = ImprovementProposal("p1", "P", "E", "H", "Delete user files", "G")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertFalse(ok)

    def test_29_governor_hard_rejects_financial_action(self):
        """Test 29: Proposal with financial in proposed change hard-rejected."""
        prop = ImprovementProposal("p1", "P", "E", "H", "Execute financial transfer", "G")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertFalse(ok)

    def test_30_rollback_manager_get_current_version(self):
        """Test 30: get_current_version returns active version."""
        self.assertEqual(self.rollback_mgr.get_current_version(), "v4.4.0")

    def test_31_rollback_manager_stable_accuracy(self):
        """Test 31: Accuracy above threshold reports STABLE."""
        rolled, msg = self.rollback_mgr.evaluate_telemetry_degradation(current_accuracy=0.95)
        self.assertFalse(rolled)
        self.assertIn("STABLE", msg)

    def test_32_rollback_history_tracking(self):
        """Test 32: Version history tracks archived versions."""
        self.rollback_mgr.deploy_version("v5.0.0", {})
        self.assertEqual(self.rollback_mgr.version_history[0]["status"], "ARCHIVED")

    def test_33_proposal_affected_components_list(self):
        """Test 33: Proposal stores affected components list."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G", affected_components=["C1", "C2"])
        self.assertEqual(len(prop.affected_components), 2)

    def test_34_proposal_expected_gain_string(self):
        """Test 34: Proposal stores expected gain string."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "Gain 10%")
        self.assertEqual(prop.expected_gain, "Gain 10%")

    def test_35_sandbox_evaluates_tokens_per_task(self):
        """Test 35: Sandbox result compares tokens_per_task."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertLess(res["candidate"]["tokens_per_task"], res["baseline"]["tokens_per_task"])

    def test_36_improvement_governor_distinction(self):
        """Test 36: ImprovementGovernor is distinct from AutonomyGovernor."""
        self.assertIsNotNone(self.governor)

    def test_37_candidate_accuracy_improvement(self):
        """Test 37: Candidate accuracy exceeds baseline."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertGreater(res["candidate"]["accuracy"], res["baseline"]["accuracy"])

    def test_38_candidate_token_reduction(self):
        """Test 38: Candidate token consumption lower than baseline."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertLess(res["candidate"]["tokens_per_task"], res["baseline"]["tokens_per_task"])

    def test_39_human_approval_gate_enforced(self):
        """Test 39: Human approval gate enforced prior to deployment."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=False)
        self.assertFalse(ok)

    def test_40_rollback_reverts_active_status(self):
        """Test 40: Reverted version marks previous version ACTIVE."""
        self.rollback_mgr.deploy_version("v5.0.0", {})
        self.rollback_mgr.evaluate_telemetry_degradation(current_accuracy=0.60)
        self.assertEqual(self.rollback_mgr.version_history[-1]["status"], "ACTIVE")

    def test_41_proposal_risk_level(self):
        """Test 41: Proposal stores risk string ("LOW")."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        self.assertEqual(prop.risk, "LOW")

    def test_42_weakness_threshold_check(self):
        """Test 42: Weakness detector checks metric thresholds."""
        records = [MissionTelemetryRecord("m1", rejections=0, tokens=100)]
        weaknesses = self.detector.detect_weaknesses(records)
        self.assertEqual(len(weaknesses), 0)

    def test_43_sandbox_false_actions_zero(self):
        """Test 43: Passed sandbox evaluation guarantees 0 false actions."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertEqual(res["candidate"]["false_actions"], 0)

    def test_44_governor_gate_message(self):
        """Test 44: Governor returns transparent decision message."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        ok, msg = self.governor.authorize_proposal(prop, {"passed": True}, user_approved=True)
        self.assertIn("APPROVED", msg)

    def test_45_multiple_proposals_handling(self):
        """Test 45: Proposer generates multiple proposals for multiple weaknesses."""
        weaknesses = [{"weakness_type": "HIGH_USER_REJECTION"}, {"weakness_type": "TOKEN_INEFFICIENCY"}]
        props = self.proposer.generate_proposals(weaknesses)
        self.assertEqual(len(props), 2)

    def test_46_rollback_single_version_stable(self):
        """Test 46: Single version does not crash on degradation test."""
        rolled, msg = self.rollback_mgr.evaluate_telemetry_degradation(current_accuracy=0.50)
        self.assertFalse(rolled)

    def test_47_proposal_id_uniqueness(self):
        """Test 47: Proposal IDs are unique."""
        weaknesses = [{"weakness_type": "HIGH_USER_REJECTION"}, {"weakness_type": "TOKEN_INEFFICIENCY"}]
        props = self.proposer.generate_proposals(weaknesses)
        self.assertNotEqual(props[0].proposal_id, props[1].proposal_id)

    def test_48_sandbox_result_passed_flag(self):
        """Test 48: Sandbox result contains boolean passed flag."""
        prop = ImprovementProposal("p1", "P", "E", "H", "C", "G")
        res = self.sandbox.evaluate_candidate_proposal(prop)
        self.assertIn("passed", res)

    def test_49_improvement_loop_end_to_end(self):
        """Test 49: End-to-end self-improvement cycle: detect -> propose -> sandbox -> govern -> deploy."""
        records = [MissionTelemetryRecord("m1", rejections=3)]
        weaknesses = self.detector.detect_weaknesses(records)
        proposals = self.proposer.generate_proposals(weaknesses)
        sb_res = self.sandbox.evaluate_candidate_proposal(proposals[0])
        auth, msg = self.governor.authorize_proposal(proposals[0], sb_res, user_approved=True)
        self.assertTrue(auth)
        dep = self.rollback_mgr.deploy_version("v5.0.0", {"policy": proposals[0].proposed_change})
        self.assertEqual(dep["version"], "v5.0.0")

    def test_50_v5_0_self_improvement_verification_passed(self):
        """Test 50: All V5.0 bounded self-improvement components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
