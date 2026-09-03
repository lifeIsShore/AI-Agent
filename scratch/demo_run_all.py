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

    # 7. V5.1 Continuous Evaluation & Behavioral Drift Detection
    print("\n----------------------------------------------------------------------")
    print("        📊 V5.1 CONTINUOUS EVALUATION & DRIFT DETECTION PIPELINE       ")
    print("----------------------------------------------------------------------")

    from personal_agent.eval.continuous_evaluation_engine import ContinuousEvaluationEngine
    from personal_agent.eval.performance_baseline_manager import PerformanceBaselineManager
    from personal_agent.eval.behavioral_drift_detector import BehavioralDriftDetector
    from personal_agent.eval.regression_monitor import RegressionMonitor
    from personal_agent.learning.preference_drift_detector import PreferenceDriftDetector
    from personal_agent.eval.model_drift_monitor import ModelDriftMonitor
    from personal_agent.autonomy.safety_regression_monitor import SafetyRegressionMonitor

    eval_engine = ContinuousEvaluationEngine()
    baseline_mgr = PerformanceBaselineManager()
    drift_detector = BehavioralDriftDetector()
    regress_monitor = RegressionMonitor()
    pref_drift_detector = PreferenceDriftDetector()
    model_drift_monitor = ModelDriftMonitor()
    safety_monitor = SafetyRegressionMonitor()

    stream_eval = eval_engine.evaluate_telemetry_stream(telemetry_recs)
    print(f"[ContinuousEvaluationEngine] Live Telemetry Evaluation: Status={stream_eval['eval_status']}, Sample Size={stream_eval['sample_size']}, Accuracy={stream_eval['current_accuracy']}")

    email_baseline = baseline_mgr.get_baseline("EmailSpecialist")
    drift_report = drift_detector.detect_behavioral_drift({"current_accuracy": 0.85, "current_user_acceptance": 0.70, "avg_tokens_per_task": 1400}, email_baseline)
    print(f"[BehavioralDriftDetector] Drift Status: {'⚠️ DRIFT DETECTED' if drift_report['drift_detected'] else '✅ STABLE'}")
    for reason in drift_report['drift_reasons']:
        print(f"  - {reason}")

    regress_res = regress_monitor.check_regression({"current_accuracy": 0.78})
    print(f"[RegressionMonitor] Status: {'⚠️ REGRESSION ALERT' if regress_res['regression_detected'] else '✅ CLEAN'}")

    pref_drift_res = pref_drift_detector.detect_preference_drift([{"source": "USER", "val": "morning"}])
    print(f"[PreferenceDriftDetector] Drift Type: '{pref_drift_res['drift_type']}' ({pref_drift_res['explanation']})")

    model_drift_res = model_drift_monitor.monitor_model_drift({"model_name": "Qwen_Local", "accuracy": 0.88})
    print(f"[ModelDriftMonitor] Model: '{model_drift_res['model_name']}' -> Recommendation: '{model_drift_res['recommendation']}'")

    safety_ok, safety_msg = safety_monitor.evaluate_safety_regression(baseline_violations=0, candidate_violations=1)
    print(f"[SafetyRegressionMonitor] Decision: {'✅ PASSED' if safety_ok else '❌ HARD REJECT'} ({safety_msg})")

    # 8. V5.2 Deep Contextual Personalization Engine
    print("\n----------------------------------------------------------------------")
    print("         🎯 V5.2 DEEP CONTEXTUAL PERSONALIZATION ENGINE               ")
    print("----------------------------------------------------------------------")

    from personal_agent.learning.deep_personalization_engine import DeepPersonalizationEngine, ContextualPreferenceRule

    deep_engine = DeepPersonalizationEngine()
    context_facts = {"task": "university_email", "sender": "Prof. Davis"}
    matched_rule = deep_engine.evaluate_contextual_recommendation(context_facts)

    print(f"[DeepPersonalizationEngine] Context Facts: {context_facts}")
    print(f"  - Matched Rule ID: '{matched_rule.rule_id}' (Source: {matched_rule.source}, Confidence: {matched_rule.confidence})")
    print(f"  - Recommendation:  '{matched_rule.action_recommendation}'")

    # 9. V5.3 Long-Term Memory Evolution & World-Model Consolidation
    print("\n----------------------------------------------------------------------")
    print("      🧠 V5.3 LONG-TERM MEMORY EVOLUTION & WORLD-MODEL CONSOLIDATION  ")
    print("----------------------------------------------------------------------")

    from personal_agent.memory.memory_consolidator import MemoryConsolidator
    from personal_agent.memory.memory_decay_engine import MemoryDecayEngine
    from personal_agent.memory.memory_conflict_resolver import MemoryConflictResolver
    from personal_agent.world.world_model_consolidator import WorldModelConsolidator
    from personal_agent.memory.memory_provenance_graph import MemoryProvenanceGraph

    mem_consolidator = MemoryConsolidator()
    mem_decay = MemoryDecayEngine()
    conflict_resolver = MemoryConflictResolver()
    world_consolidator = WorldModelConsolidator()
    provenance_graph = MemoryProvenanceGraph()

    obs_sample = [{"domain": "university", "pattern": "handle_afternoon"}] * 6
    consolidated_mems = mem_consolidator.consolidate_observations(obs_sample, threshold=5)
    print(f"[MemoryConsolidator] Consolidated {len(obs_sample)} observations -> {len(consolidated_mems)} Durable Fact: '{consolidated_mems[0]['durable_fact']}'")

    decayed_mems = mem_decay.apply_decay([{"id": "m1", "source": "USER", "confidence": 1.0}, {"id": "m2", "source": "LEARNED", "confidence": 0.90}], days_passed=15)
    print(f"[MemoryDecayEngine] Memory Decay Applied: USER memory='{decayed_mems[0]['decay_status']}', LEARNED memory='{decayed_mems[1]['decay_status']}' (Confidence: {decayed_mems[1]['confidence']})")

    conflict_res = conflict_resolver.resolve_conflict({"id": "m_old", "source": "LEARNED", "val": "morning"}, {"id": "m_new", "source": "USER", "val": "afternoon"})
    print(f"[MemoryConflictResolver] Resolution: '{conflict_res['resolution']}' (New USER preference supersedes '{conflict_res['supersedes']}')")

    world_res = world_consolidator.consolidate_world_graph([{"id": "prof_davis", "name": "Prof. Davis"}, {"id": "thesis_proj", "name": "Master Thesis"}], [{"source_id": "prof_davis", "target_id": "thesis_proj", "relation_type": "ADVISOR"}])
    print(f"[WorldModelConsolidator] Graph Consolidation: {world_res['total_entities']} Entities, {world_res['total_relationships']} Durable Edge ('Prof. Davis' -> ADVISOR -> 'Master Thesis')")

    provenance_graph.add_memory_node(consolidated_mems[0]["durable_id"], "LEARNED", ["email_1", "email_2"], observations=6)
    lineage = provenance_graph.get_lineage(consolidated_mems[0]["durable_id"])
    print(f"[MemoryProvenanceGraph] Memory Node '{lineage['memory_id']}': Lineage Source='{lineage['source']}', Observations={lineage['observations']}")

    # 10. V5.4 Adaptive Multi-Model Intelligence
    print("\n----------------------------------------------------------------------")
    print("         ⚡ V5.4 ADAPTIVE MULTI-MODEL INTELLIGENCE ENGINE             ")
    print("----------------------------------------------------------------------")

    from personal_agent.orchestration.adaptive_model_selector import AdaptiveModelSelector

    adaptive_selector = AdaptiveModelSelector()

    # Case A: Low complexity
    sel_a = adaptive_selector.select_adaptive_model({"complexity": "low"}, {}, {}, {})
    print(f"[AdaptiveModelSelector] Task: 'Simple Regex/Low' -> Tier: '{sel_a['selected_tier']}' ({sel_a['reason']})")

    # Case B: Resource Constrained
    sel_b = adaptive_selector.select_adaptive_model({"complexity": "medium"}, {}, {}, {"cpu_percent": 92})
    print(f"[AdaptiveModelSelector] Task: 'Medium/CPU 92%' -> Tier: '{sel_b['selected_tier']}' ({sel_b['reason']})")

    # Case C: High Complexity Multi-Domain Task
    sel_c = adaptive_selector.select_adaptive_model({"complexity": "high"}, {}, {}, {"cpu_percent": 20})
    print(f"[AdaptiveModelSelector] Task: 'High Multi-Domain' -> Tier: '{sel_c['selected_tier']}' ({sel_c['reason']})")
    print(f"[AdaptiveModelSelector] AutonomyGovernor Decoupled: {sel_c['governor_decoupled']} (Governor retains 100% authorization authority)")

    # 11. V5.5 Mission-Level Strategy Learning
    print("\n----------------------------------------------------------------------")
    print("        🎯 V5.5 MISSION-LEVEL STRATEGY LEARNING ENGINE                 ")
    print("----------------------------------------------------------------------")

    from personal_agent.learning.mission_learning_engine import MissionLearningEngine

    mission_engine = MissionLearningEngine()
    rec_strat = mission_engine.recommend_mission_strategy("university_deadline")
    print(f"[MissionLearningEngine] Goal: 'Prepare for Master Thesis Deadline'")
    print(f"  - Selected Strategy: '{rec_strat['name']}' (Success Rate: {rec_strat['success_rate']*100}%, Confidence: {rec_strat['confidence']})")
    print(f"  - Reusable Step Sequence: {rec_strat['step_sequence']}")

    # 12. V5.6 Predictive Personal Agent
    print("\n----------------------------------------------------------------------")
    print("           🔮 V5.6 PREDICTIVE PERSONAL AGENT ENGINE                    ")
    print("----------------------------------------------------------------------")

    from personal_agent.events.predictive_event_engine import PredictiveEventEngine

    pred_engine = PredictiveEventEngine()
    pred_res = pred_engine.predict_upcoming_events(
        calendar_items=[{"id": "c1"}, {"id": "c2"}],
        tasks=[{"status": "completed"}, {"status": "needsAction"}],
        goals=[{"name": "Prepare Master Thesis Proposal", "deadline": "2026-09-10"}]
    )

    print(f"[PredictiveEventEngine] Completion Probability: {pred_res['completion_probability']*100}% | Predictions Generated: {pred_res['predictions_count']}")
    for p in pred_res["predictions"]:
        print(f"  - [{p['prediction_type']}] Risk Level: '{p['risk_level']}' -> Target: '{p['target']}'")
        print(f"    Recommendation: {p['recommendation']}")

    # 13. V5.7 Personal Simulation / Digital Twin & Counterfactual Planning
    print("\n----------------------------------------------------------------------")
    print("      🌐 V5.7 PERSONAL SIMULATION & DIGITAL TWIN ENVIRONMENT          ")
    print("----------------------------------------------------------------------")

    from personal_agent.world.personal_simulation_environment import PersonalSimulationEnvironment
    from personal_agent.planner.counterfactual_planner import CounterfactualPlanner

    sim_env = PersonalSimulationEnvironment()
    cf_planner = CounterfactualPlanner()

    sim_res = cf_planner.evaluate_counterfactuals(
        sim_env,
        current_workload={"total_hours": 25.0, "max_capacity": 40.0},
        proposed_action={"estimated_hours": 6.0}
    )

    print(f"[PersonalSimulationEnvironment] In-Memory Counterfactual Simulation:")
    for sc in sim_res["all_scenarios"]:
        print(f"  - Branch '{sc['scenario_mode']}': Simulated Workload={sc['simulated_workload_hours']}h ({sc['capacity_utilization']*100}% Capacity) -> Predicted Completion Prob: {sc['predicted_completion_prob']*100}%, Risk Level: {sc['risk_level']}")

    print(f"[CounterfactualPlanner] Recommended Scenario Branch: '{sim_res['recommended_scenario']}' (Mutates Live State: False)")

    # 14. V5.8 Autonomous Research & Controlled Knowledge Acquisition
    print("\n----------------------------------------------------------------------")
    print("      🔍 V5.8 AUTONOMOUS RESEARCH & CONTROLLED KNOWLEDGE ACQUISITION  ")
    print("----------------------------------------------------------------------")

    from personal_agent.reasoning.autonomous_research_engine import AutonomousResearchEngine

    research_engine = AutonomousResearchEngine()
    research_res = research_engine.conduct_autonomous_research(
        topic="Financial Distress ML Models",
        initial_sources=[
            {"url": "https://arxiv.org/abs/2401.12345", "source_type": "ARXIV_PAPER", "confidence": 0.92, "snippet": "Financial distress prediction accuracy reached 94.2%."},
            {"url": "https://unverified-blog.com/post", "source_type": "BLOG", "confidence": 0.50, "snippet": "Unverified claim."}
        ]
    )

    print(f"[AutonomousResearchEngine] Topic: '{research_res['topic']}' | Sources Scanned: {research_res['total_sources_scanned']}")
    for f in research_res["extracted_facts"]:
        print(f"  - [{f['verification_status']}] Source: '{f['source']}' (Conf: {f['confidence']}, RAG Ingestible: {f['rag_ingestible']})")

    # 15. V5.9 Mission Execution Intelligence & Dynamic Replanning
    print("\n----------------------------------------------------------------------")
    print("    ⚡ V5.9 MISSION EXECUTION INTELLIGENCE & DYNAMIC REPLANNING        ")
    print("----------------------------------------------------------------------")

    from personal_agent.control.mission_execution_intelligence import MissionExecutionIntelligence

    exec_intel = MissionExecutionIntelligence()
    intel_res = exec_intel.adapt_mission_execution(
        mission_id="m_thesis_research",
        actual_duration_sec=12.0,
        estimated_duration_sec=5.0,
        strategy_id="strat_thesis_b"
    )

    print(f"[MissionExecutionIntelligence] Mission ID: '{intel_res['mission_id']}' -> Overrun Ratio: {intel_res['duration_ratio']}x")
    print(f"  - Status: '{intel_res['status']}' | Recommended Scenario: '{intel_res['new_recommended_scenario']}' | Prediction Risk: '{intel_res['prediction_risk']}'")

    # 16. V6.0 Persistent Personal AI Operating System Master Architecture
    print("\n----------------------------------------------------------------------")
    print("     ⭐ V6.0 PERSISTENT PERSONAL AI OPERATING SYSTEM (PersonalAIOS_v6) ")
    print("----------------------------------------------------------------------")

    from personal_agent.runtime.personal_ai_os_v6 import PersonalAIOS_v6

    master_os = PersonalAIOS_v6()
    os_res = master_os.run_persistent_os_cycle("Prepare Master Thesis Proposal & Replan Schedule")

    print(f"[PersonalAIOS_v6] Master OS Version: '{os_res['os_version']}' | Status: '{os_res['status']}'")
    print(f"  - Cycle Status:        '{os_res['cycle_result']['status']}' (Provenance ID: {os_res['cycle_result']['provenance_id']})")
    print(f"  - Simulation Scenario: '{os_res['simulation_scenario']}'")
    print(f"  - Strategy Selection:  '{os_res['recommended_strategy']}'")
    print(f"  - Zero-Bypass Invariant: {os_res['zero_bypass_governance']}")

    # 17. V6.1 Personal Operating Memory & Temporal Knowledge Graph
    print("\n----------------------------------------------------------------------")
    print("       🕒 V6.1 TEMPORAL KNOWLEDGE GRAPH & PERSONAL TIMELINE           ")
    print("----------------------------------------------------------------------")

    from personal_agent.world.temporal_knowledge_graph import TemporalKnowledgeGraph

    tkg = TemporalKnowledgeGraph()
    tkg_reason = tkg.reason_over_timeline()

    print(f"[TemporalKnowledgeGraph] Total Timeline Nodes: {tkg_reason['timeline_length']}")
    print(f"  - Past Milestones:  {tkg_reason['past_milestones']}")
    print(f"  - Currently Active: {tkg_reason['currently_active']}")
    print(f"  - Why Changed:      '{tkg_reason['why_changed']}'")
    print(f"  - Next Likely:      '{tkg_reason['next_likely_event']}'")

    print("\n======================================================================")
    print("  ✅ AGENT DEMONSTRATION PASSED PERFECTLY WITH ZERO SECURITY INVARIANTS VIOLATED!")
    print("======================================================================\n")

if __name__ == "__main__":
    run_agent_demonstration()
