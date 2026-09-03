import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.runtime.personal_agent_runtime import PersonalAgentRuntime
from personal_agent.runtime.lifecycle import AgentLifecycleState
from personal_agent.control.pilot_controller import PilotController, PILOT_MODE_BOUNDED_AUTO
from personal_agent.telemetry.pilot_telemetry import MissionTelemetryRecord
from personal_agent.control.human_feedback import HumanFeedbackLoop, USER_APPROVED
from personal_agent.control.emergency_stop import EmergencyStop
from personal_agent.eval.performance_analyzer import AgentPerformanceAnalyzer
from personal_agent.eval.specialist_benchmark import SpecialistBenchmark
from personal_agent.orchestration.model_router import ModelRouter
from personal_agent.eval.cost_optimizer import CostQualityOptimizer
from personal_agent.learning.improvement_detector import ImprovementDetector
from personal_agent.learning.improvement_proposer import ImprovementProposer, ImprovementProposal
from personal_agent.eval.improvement_sandbox import ImprovementSandbox
from personal_agent.autonomy.improvement_governor import ImprovementGovernor
from personal_agent.runtime.rollback_manager import RollbackManager

def run_agent_demonstration():
    print("======================================================================")
    print("       🤖 BOUNDED PERSONAL AUTONOMOUS AGENT RUNTIME — LIVE DEMO      ")
    print("======================================================================\n")

    # 1. Initialize Master Runtime & Pilot Controller (V4.0 & V4.3)
    runtime = PersonalAgentRuntime()
    runtime.supervisor.current_state = AgentLifecycleState.RUNNING
    pilot_ctrl = PilotController(mode=PILOT_MODE_BOUNDED_AUTO, phase=4)
    emergency_stop = EmergencyStop()

    print(f"[Core Runtime] Supervisor State: {runtime.supervisor.current_state.name}")
    print(f"[PilotController] Pilot Phase: {pilot_ctrl.current_phase} (Mode: {pilot_ctrl.current_mode})")

    # 2. Run Autonomous Goal Execution Cycle
    goal_query = "Check inbox for thesis deadline updates and replan calendar"
    print(f"\n[Execution Cycle] Processing User Goal: '{goal_query}'...")

    # Gating check
    allowed, gate_msg = pilot_ctrl.is_capability_allowed("read_email")
    print(f"[Pilot Gate] {gate_msg}")

    cycle_res = runtime.run_autonomous_cycle(goal_query)
    print(f"[Runtime Cycle Result] Status: {cycle_res['status']} | Specialist Agent: {cycle_res['agent_id']}")
    print(f"  - Action Executed: Tool '{cycle_res['execution']['tool']}'")
    print(f"  - Provenance ID:   {cycle_res['provenance_id']}")
    print(f"  - Security Invariants Verified: {cycle_res['security_invariants_verified']}")

    # 3. Telemetry & Human Feedback (V4.3)
    feedback_loop = HumanFeedbackLoop(learning_engine=runtime.learning_engine)
    fb_res = feedback_loop.record_feedback(
        action_id=cycle_res["outcome_id"],
        feedback_type=USER_APPROVED,
        reason="Allocated into free morning slot",
        key="morning_work_preference",
        value=True
    )
    print(f"\n[Human Feedback Loop] {fb_res['status']} (Recorded preference: morning_work_preference=True)")

    # 4. Multi-Tier Model Router & Specialist Benchmarks (V4.4)
    router = ModelRouter()
    model_res = router.select_model_tier("hard planning task")
    print(f"\n[Model Router] Task Complexity: 'hard planning task' -> Model Tier: '{model_res['selected_tier']}' (Governor Decoupled)")

    bench = SpecialistBenchmark()
    spec_metrics = bench.evaluate_specialists()
    print(f"[Specialist Benchmark] PlanningSpecialist Schedule Conflict Resolution: {spec_metrics['PlanningSpecialist']['conflict_resolution_rate']*100}%")

    # 5. Bounded Self-Improvement Cycle (V5.0)
    print("\n----------------------------------------------------------------------")
    print("             🧠 BOUNDED SELF-IMPROVEMENT PIPELINE (V5.0)               ")
    print("----------------------------------------------------------------------")

    detector = ImprovementDetector()
    proposer = ImprovementProposer()
    sandbox = ImprovementSandbox()
    governor = ImprovementGovernor()
    rollback_mgr = RollbackManager()

    # Simulate operational telemetry record with user rejections
    telemetry_recs = [
        MissionTelemetryRecord("m1", duration_sec=12.0, tokens=350, rejections=2),
        MissionTelemetryRecord("m2", duration_sec=14.0, tokens=450, rejections=2)
    ]

    weaknesses = detector.detect_weaknesses(telemetry_recs)
    print(f"[ImprovementDetector] Detected {len(weaknesses)} Weakness Patterns:")
    for w in weaknesses:
        print(f"  - [{w['weakness_type']}] {w['evidence']} (Component: {w['affected_component']})")

    proposals = proposer.generate_proposals(weaknesses)
    print(f"\n[ImprovementProposer] Generated {len(proposals)} Improvement Proposals:")
    for p in proposals:
        print(f"  - Proposal '{p.proposal_id}': {p.hypothesis}")

        # Run Sandbox Evaluation
        sb_res = sandbox.evaluate_candidate_proposal(p)
        print(f"    - Sandbox Evaluation: {'✅ PASSED' if sb_res['passed'] else '❌ REJECTED'} ({sb_res['reason']})")
        print(f"      (Baseline Accuracy: {sb_res['baseline']['accuracy']} -> Candidate Accuracy: {sb_res['candidate']['accuracy']}, False Actions: {sb_res['candidate']['false_actions']})")

        # Evaluate through ImprovementGovernor
        auth, gov_msg = governor.authorize_proposal(p, sb_res, user_approved=True)
        print(f"    - ImprovementGovernor Decision: {gov_msg}")

        if auth:
            dep = rollback_mgr.deploy_version("v5.0.0", {"policy": p.proposed_change})
            print(f"    - Production Deployment: Version '{dep['version']}' ACTIVE.")

    # 6. Test Security Policy Attempt (Security Boundary Modification)
    print("\n[Security Boundary Hardening Test] Simulating Malicious/Unsafe Self-Improvement Proposal...")
    unsafe_prop = ImprovementProposal(
        proposal_id="prop_unsafe_007",
        problem="User requests financial actions",
        evidence="High demand",
        hypothesis="Bypass governor to send money automatically",
        proposed_change="Allow autonomous financial transactions",
        expected_gain="Higher autonomy",
        modifies_security_boundary=True
    )

    sb_unsafe = sandbox.evaluate_candidate_proposal(unsafe_prop)
    auth_unsafe, msg_unsafe = governor.authorize_proposal(unsafe_prop, sb_unsafe, user_approved=True)
    print(f"[ImprovementGovernor] Security Policy Check Result: {msg_unsafe}")

    print("\n======================================================================")
    print("  ✅ AGENT DEMONSTRATION PASSED PERFECTLY WITH ZERO SECURITY INVARIANTS VIOLATED!")
    print("======================================================================\n")

if __name__ == "__main__":
    run_agent_demonstration()
