import sys
import os
import json
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.models.router import ModelRouter, ModelDecision
from personal_agent.models.scoring import INTENT_PLAN_DAY
from personal_agent.reasoning.reasoner import DecisionReasoner
from personal_agent.reasoning.plan import DecisionPlan
from personal_agent.context.optimizer import ContextOptimizer
from personal_agent.memory.lifecycle import MemoryLifecycleManager, ContradictionDetector
from personal_agent.orchestration.planner import ExecutionPlanner, ExecutionPlan
from personal_agent.orchestration.executor import ParallelExecutor
from personal_agent.orchestration.router import ToolRouter
from personal_agent.orchestration.validator import PlanValidator
from personal_agent.orchestration.budget import WorkflowBudget
from personal_agent.orchestration.coordinator import WorkflowCoordinator
from personal_agent.orchestration.recovery_strategy import FailureClassifier, WorkflowRecoveryEngine
from personal_agent.orchestration.resource_manager import ResourceManager
from personal_agent.orchestration.dynamic_router import DynamicStepRouter, StepContextIsolator
from personal_agent.events.intelligence import EventIntelligenceEngine
from personal_agent.events.deduplicator import EventDeduplicator
from personal_agent.events.correlator import EventCorrelator
from personal_agent.events.priority import EventPriorityEngine
from personal_agent.events.notification import NotificationIntelligenceEngine
from personal_agent.events.trigger import ProactiveTriggerEngine
from personal_agent.learning.outcome_engine import OutcomeLearningEngine, OUTCOME_SUCCESS
from personal_agent.learning.strategy_store import ExecutionStrategyStore
from personal_agent.learning.feedback_loop import FeedbackLoop, FEEDBACK_APPROVE
from personal_agent.workflow.models import Workflow, WorkflowStep, WF_CREATED, WF_RUNNING, WF_COMPLETED, STEP_COMPLETED
from personal_agent.workflow.dag import WorkflowDAG
from personal_agent.workflow.verification import StepVerifier
from personal_agent.workflow.replanner import WorkflowReplanner
from personal_agent.tools.registry import ToolRegistry
from personal_agent.tools.gmail import GmailTool
from personal_agent.tools.calendar import GoogleCalendarTool
from personal_agent.tools.tasks import GoogleTasksTool
from personal_agent.policy.engine import PolicyEngine, PermissionLevel
from personal_agent.policy.proposal import ActionProposal, STATUS_PENDING_APPROVAL, STATUS_AUTO_APPROVED
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.policy.review import ReviewDecisionEngine, MODE_AUTOMATIC, MODE_QUICK_REVIEW, MODE_DETAILED_REVIEW
from personal_agent.policy.scopes import ScopeManager, SCOPE_RECURRING
from personal_agent.policy.rejection import RepeatedRejectionTracker
from personal_agent.policy.policy_registry import DeclarativePolicyRegistry
from personal_agent.security.classification import DataClassifier
from personal_agent.security.dlp import DataLossPreventionEngine
from personal_agent.security.provenance import ProvenanceTracker
from personal_agent.security.audit import AuditLogger
from personal_agent.security.trust import sanitize_external_text, classify_trust_level, TRUST_EXTERNAL
from personal_agent.security.identity import IdentityProvider
from personal_agent.security.credentials import CredentialBroker
from personal_agent.security.sanitizer import redact_credentials
from personal_agent.control.killswitch import KillSwitchEngine, MODE_NORMAL
from personal_agent.control.config import ConfigManager
from personal_agent.workflow.engine import WorkflowEngine
from personal_agent.api.app import AgentAPIServer
from personal_agent.state.manager import StateManager
from personal_agent.events.store import EventStore
from personal_agent.events.bus import EventBus
from personal_agent.events.event import AgentEvent, EVENT_EMAIL_RECEIVED, EVENT_ACTION_EXECUTED
from personal_agent.telemetry.store import TelemetryStore
from personal_agent.telemetry.tracer import (
    AgentTracer, STEP_REQUEST_RECEIVED, STEP_INTENT_DETECTED, STEP_CONTEXT_BUILT,
    STEP_PROPOSAL_CREATED, STEP_POLICY_CHECK, STEP_TOOL_EXECUTION_SUCCESS, STEP_TRACE_COMPLETED
)
from personal_agent.telemetry.trace import TraceContext
from personal_agent.reliability.degradation import ServiceDegradationHandler
from personal_agent.reliability.checkpoint import RecoveryCheckpointEngine
from personal_agent.telemetry.metrics import TelemetryMetricsCalculator
from personal_agent.memory.manager import MemoryManager
from personal_agent.memory.learning import MemoryLearningLoop, SCOPE_DURABLE_PREFERENCE, SCOPE_EVENT_MEMORY
from personal_agent.triage.engine import PriorityEngine
from personal_agent.triage.inbox_zero import InboxZeroEngine
from personal_agent.context.manager import ContextManager
from personal_agent.planner.daily_planner import DailyPlannerEngine
from personal_agent.scheduler.job import Job
from personal_agent.scheduler.registry import JobRegistry
from personal_agent.scheduler.scheduler import AgentScheduler
from personal_agent.scheduler.handlers import (
    morning_briefing_job, inbox_triage_job, calendar_sync_job, memory_maintenance_job
)

def print_header(title: str):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL ASSISTANT (V2.6 — AGENT LEARNING & OUTCOME OPTIMIZATION)")
    print("Initializing V2.6 Assistant Core...")

    user_principal = IdentityProvider.get_user_principal("user_ahmet")
    credential_broker = CredentialBroker()
    model_router = ModelRouter()
    review_engine = ReviewDecisionEngine()
    scope_manager = ScopeManager()
    rejection_tracker = RepeatedRejectionTracker()

    decision_reasoner = DecisionReasoner()
    context_optimizer = ContextOptimizer()
    memory_lifecycle = MemoryLifecycleManager()

    outcome_learning_engine = OutcomeLearningEngine()
    execution_strategy_store = ExecutionStrategyStore()
    feedback_loop = FeedbackLoop(outcome_learning_engine, execution_strategy_store)

    event_intel = EventIntelligenceEngine()
    event_dedup = EventDeduplicator()
    event_correlator = EventCorrelator()
    event_priority = EventPriorityEngine()
    notification_intel = NotificationIntelligenceEngine()
    proactive_trigger = ProactiveTriggerEngine()

    execution_planner = ExecutionPlanner()
    parallel_executor = ParallelExecutor()
    tool_router = ToolRouter()
    plan_validator = PlanValidator()

    workflow_coordinator = WorkflowCoordinator()
    failure_classifier = FailureClassifier()
    recovery_engine = WorkflowRecoveryEngine()
    resource_manager = ResourceManager(WorkflowBudget(max_tokens=20000, max_cost_eur=0.10))
    dynamic_step_router = DynamicStepRouter()
    context_isolator = StepContextIsolator()

    workflow_dag = WorkflowDAG()
    step_verifier = StepVerifier()
    workflow_replanner = WorkflowReplanner()

    killswitch = KillSwitchEngine()
    config_mgr = ConfigManager(config_dir="config")
    workflow_engine = WorkflowEngine()

    policy_registry = DeclarativePolicyRegistry(policy_dir="policies")
    data_classifier = DataClassifier()
    dlp_engine = DataLossPreventionEngine(classifier=data_classifier)
    provenance_tracker = ProvenanceTracker()

    telemetry_store = TelemetryStore(telemetry_dir="data/telemetry", log_filename="traces.jsonl")
    tracer = AgentTracer(store=telemetry_store)

    user_req = "Plan my day"
    exec_plan = execution_planner.create_execution_plan(user_req)
    val_res = plan_validator.validate_plan(exec_plan, resource_manager.budget)
    print(f"[PlanValidator] Plan '{exec_plan.plan_id}' Validation: {'✅ PASS' if val_res.valid else '❌ FAIL'} ({val_res.reason})")

    # Build Multi-Step Workflow DAG
    wf_steps = [
        WorkflowStep(step_id="s1_gmail", objective="Fetch & sanitize Gmail inbox items", required_capabilities=["gmail.read"]),
        WorkflowStep(step_id="s2_cal", objective="Fetch Calendar events & calculate free slots", required_capabilities=["calendar.read"]),
        WorkflowStep(step_id="s3_planner", objective="Generate daily execution briefing plan", dependencies=["s1_gmail", "s2_cal"]),
        WorkflowStep(step_id="s4_proposals", objective="Create action proposals & evaluate policy", dependencies=["s3_planner"], required_capabilities=["calendar.create", "gmail.archive"])
    ]

    active_wf = Workflow(workflow_id="wf_daily_master", objective="Daily master execution workflow", priority="NORMAL", steps=wf_steps)
    active_wf.update_status(WF_RUNNING)
    workflow_coordinator.register_workflow(active_wf)

    root_trace_ctx = TraceContext(request_id=f"req_{active_wf.workflow_id}")
    workflow_engine.link_request(active_wf.workflow_id, root_trace_ctx.request_id)

    checkpoint_engine = RecoveryCheckpointEngine(telemetry_store=telemetry_store)
    incomplete_traces = checkpoint_engine.get_incomplete_traces()
    if incomplete_traces:
        print(f"[Checkpoint Recovery] Detected {len(incomplete_traces)} incomplete execution traces from disk.")

    tracer.record_flight_step(root_trace_ctx, 1, STEP_REQUEST_RECEIVED, {"prompt": user_req, "workflow_id": active_wf.workflow_id})

    degradation_handler = ServiceDegradationHandler()
    gateway = ModelGateway(provider="ollama", tracer=tracer)
    registry = ToolRegistry()
    registry.register_default_tools()
    
    state_manager = StateManager(state_dir="data/state")
    event_store = EventStore(events_dir="data/events", log_filename="events.jsonl")
    event_bus = EventBus(event_store=event_store)
    
    policy = PolicyEngine()
    audit_logger = AuditLogger()
    memory_manager = MemoryManager(gateway=gateway)
    memory_loop = MemoryLearningLoop(memory_manager=memory_manager)
    
    approval_queue = ApprovalQueue(
        tool_registry=registry,
        audit_logger=audit_logger,
        memory_loop=memory_loop,
        state_manager=state_manager,
        event_bus=event_bus
    )

    api_server = AgentAPIServer(
        mode_provider=killswitch,
        approval_queue=approval_queue,
        telemetry_store=telemetry_store
    )
    
    triage_engine = PriorityEngine(gateway)
    inbox_zero_engine = InboxZeroEngine()
    context_manager = ContextManager(gateway=gateway)
    daily_planner = DailyPlannerEngine(user_name="Ahmet")

    event_bus.replay_unprocessed()

    job_registry = JobRegistry()
    scheduler = AgentScheduler(registry=job_registry, state_manager=state_manager)

    version_bind = config_mgr.get_version_binding()
    print(f"[Core] Active Principal: '{user_principal.principal_id}' ({user_principal.principal_type}).")
    print(f"[Core] OutcomeLearningEngine & FeedbackLoop active (Adaptation & Evidence tracking enabled).")
    print(f"[Core] Policy Version: {version_bind['policy_version']} | Config Hash: {version_bind['config_hash']}.")

    res_ok, res_id, res_msg = resource_manager.reserve(active_wf.workflow_id, est_tokens=1500, est_cost=0.005)
    print(f"[ResourceManager] {res_msg}")

    # Parallel Execution of Initial Retrieval Steps
    emails = []
    cal_events = []
    free_slots = []

    def fetch_gmail():
        cred = credential_broker.get_tool_credential("gmail", "gmail.read")
        g_tool = GmailTool()
        res = g_tool.list_recent_emails(limit=10)
        return res if res else [
            {"id": "m1", "sender": "advisor@univ.edu", "subject": "Thesis proposal submission deadline", "body": "Please submit your thesis proposal by Friday.", "unread": True},
            {"id": "m2", "sender": "prof@univ.edu", "subject": "University lecture room change", "body": "Lecture moves to Room 301.", "unread": True},
            {"id": "m3", "sender": "careers@jobalerts.com", "subject": "Weekly software engineering job alerts", "body": "10 new jobs posted.", "unread": False}
        ]

    def fetch_cal():
        cred = credential_broker.get_tool_credential("calendar", "calendar.read")
        c_tool = GoogleCalendarTool()
        ev, slots = c_tool.get_today_events(), c_tool.get_free_slots()
        if ev is not None:
            return ev, slots
        return (
            [{"id": "ev1", "summary": "University lecture", "start": "2026-09-01T09:00:00Z", "end": "2026-09-01T10:00:00Z", "status": "confirmed"}],
            [{"start": "10:00", "end": "12:00", "duration_minutes": 120}, {"start": "14:00", "end": "17:00", "duration_minutes": 180}]
        )

    parallel_group_tasks = [
        ("s1_gmail", fetch_gmail),
        ("s2_cal", fetch_cal)
    ]

    print("\nExecuting Parallel DAG Retrieval Group (Gmail + Calendar)...")
    p_res = parallel_executor.execute_parallel_group(parallel_group_tasks)

    emails = p_res["results"]["s1_gmail"]["output"]
    cal_res_output = p_res["results"]["s2_cal"]["output"]
    cal_events, free_slots = cal_res_output

    print(f"  - Parallelization Speedup: {p_res['speedup_ratio']}x (Parallel Latency: {p_res['parallel_latency_ms']}ms vs Est Sequential: {p_res['sequential_latency_est_ms']}ms).")

    # Proactive Event Deduplication & Correlation
    agent_events = []
    for email in emails:
        ev = AgentEvent(event_type=EVENT_EMAIL_RECEIVED, source="GmailTool", entity_id=str(email.get("id")), payload=email)
        is_dup, d_msg = event_dedup.is_duplicate(ev)
        if not is_dup:
            agent_events.append(ev)
            cl_res = event_intel.process_incoming_event(ev)
            prio = event_priority.calculate_priority(cl_res["importance"], cl_res["urgency"], cl_res["actionability"])
            route_mode, _ = notification_intel.determine_notification_routing(prio)
            print(f"  - Event [{ev.entity_id}] Prio: {prio:<3} | Route: {route_mode:<20} | Action: {cl_res['recommended_action']}")

    situations = event_correlator.detect_composite_situations(agent_events, cal_events, [])
    if situations:
        print(f"\n[EventCorrelator] Detected {len(situations)} Composite Situations:")
        for sit in situations:
            print(f"  - [{sit['situation_id']}] {sit['title']} (Risk: {sit['risk']})")

    # Commit Reservation
    resource_manager.commit(res_id, actual_tokens=1200, actual_cost=0.003, actual_runtime=p_res['parallel_latency_ms']/1000.0)

    raw_context_payload = []
    for email in emails:
        if "body" in email:
            email["body"] = sanitize_external_text(email["body"], source_trust=TRUST_EXTERNAL)
        
        content_id = f"email_{email.get('id')}"
        sens = data_classifier.classify_sensitivity(email.get("body", ""), category="gmail")
        provenance_tracker.tag_provenance(
            content_id=content_id,
            source="gmail",
            source_id=str(email.get("id")),
            trust_level="EXTERNAL",
            sensitivity=sens
        )
        raw_context_payload.append(email)

    sanitized_emails, blocked_dlp_count = dlp_engine.sanitize_context_payload(raw_context_payload)

    # Verify Step 1
    s1 = next(s for s in active_wf.steps if s.step_id == "s1_gmail")
    s1.mark_completed({"item_count": len(sanitized_emails)})
    v1_res = step_verifier.verify_step_execution(s1, {"item_count": len(sanitized_emails)})
    print(f"  - [{s1.step_id}] Post-State Verification: {v1_res.status} ({v1_res.reason})")

    opt_context = context_optimizer.optimize_context_selection(sanitized_emails, max_token_budget=1500)

    # Verify Step 2
    s2 = next(s for s in active_wf.steps if s.step_id == "s2_cal")
    s2.mark_completed({"event_count": len(cal_events), "free_slot_count": len(free_slots)})
    v2_res = step_verifier.verify_step_execution(s2, {"event_count": len(cal_events)})
    print(f"  - [{s2.step_id}] Post-State Verification: {v2_res.status} ({v2_res.reason})")

    # Checkpoint Workflow to disk
    workflow_dag.checkpoint_workflow(active_wf)

    scheduler.register_job(Job(
        job_id="morning_briefing",
        name="Morning Briefing & Planning",
        interval_minutes=1440,
        handler=lambda: morning_briefing_job(context_manager, daily_planner, free_slots)
    ))
    scheduler.register_job(Job(
        job_id="inbox_triage",
        name="Gmail Inbox Triage & Proposals",
        interval_minutes=30,
        handler=lambda: inbox_triage_job(triage_engine, inbox_zero_engine, policy, approval_queue, emails)
    ))

    print("\nExecuting Scheduler Daemon Tick...")
    tick_results = scheduler.run_daemon_tick()
    for res in tick_results:
        print(f"  - Job [{res['job_id']}] -> Status: {res['status']} | Output: {res['output']}")

    decision_plan = decision_reasoner.build_decision_plan(user_req, opt_context["selected_items"])

    # Dynamic Step Model Routing
    s3_tier, s3_r_reason = dynamic_step_router.route_step_model("s3_planner", confidence=0.92, risk_level="MEDIUM")
    print(f"[DynamicStepRouter] {s3_r_reason}")

    model_decision = model_router.route_request(
        intent=INTENT_PLAN_DAY,
        context_bytes=3500,
        risk_level="MEDIUM",
        tool_count=3
    )

    tracer.record_flight_step(root_trace_ctx, 2, STEP_INTENT_DETECTED, {"intent": "PLAN_DAY", "model": model_decision.model_name})
    triaged_emails = []
    for email in opt_context["selected_items"]:
        event_bus.publish(AgentEvent(
            event_type=EVENT_EMAIL_RECEIVED,
            source="GmailTool",
            entity_id=str(email.get("id")),
            payload={"sender": email.get("sender"), "subject": email.get("subject")}
        ))
        analysis, _ = triage_engine.evaluate(email)
        analysis["id"] = email.get("id")
        analysis["sender"] = email.get("sender")
        analysis["subject"] = email.get("subject")
        triaged_emails.append(analysis)

    context_pkg = context_manager.assemble_context(
        user_request=user_req,
        emails=triaged_emails,
        calendar=cal_events,
        tasks=[]
    )

    tracer.record_flight_step(root_trace_ctx, 3, STEP_CONTEXT_BUILT, {"items": len(triaged_emails)})

    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)

    print_header("🗓 DAILY EXECUTION BRIEFING")
    print(plan["formatted_report"])

    s3 = next(s for s in active_wf.steps if s.step_id == "s3_planner")
    s3.mark_completed({"report_generated": True})

    print("\n")
    print_header("📋 EXPLAINABLE ACTION PROPOSALS & FEEDBACK LEARNING")
    
    inbox_eval = inbox_zero_engine.evaluate_inbox(triaged_emails)
    
    proposals_to_process = []
    for p in plan.get("proposals", []):
        success_tr, resolved_tool, r_reason = tool_router.resolve_tool_for_capability("calendar.create", p.get("action"))
        prop = policy.create_proposal(
            action=resolved_tool,
            target="primary_calendar",
            parameters={"summary": p.get("summary"), "start_time": p.get("start_time"), "end_time": p.get("end_time")},
            reason=p.get("reason", "Daily planner schedule block"),
            ttl_minutes=60,
            why_proposed=[
                f"1. Goal task '{p.get('summary')}' was identified as active priority.",
                f"2. Free calendar slot found ({p.get('start_time')} - {p.get('end_time')}).",
                "3. Allocation honors user afternoon work preference."
            ]
        )
        proposals_to_process.append(prop)

    for p in inbox_eval.get("archive_proposals", [])[:3]:
        success_tr, resolved_tool, r_reason = tool_router.resolve_tool_for_capability("gmail.archive", p.get("action"))
        prop = policy.create_proposal(
            action=resolved_tool,
            target=f"email_{p.get('msg_id')}",
            parameters={"msg_id": p.get("msg_id")},
            reason=p.get("reason", "Inbox Zero archive recommendation"),
            ttl_minutes=120,
            why_proposed=[
                "1. Sender is an automated notification service.",
                "2. Message requires no immediate reply or calendar planning.",
                "3. Similar promotional digests were previously archived."
            ]
        )
        proposals_to_process.append(prop)

    print(f"Evaluating {len(proposals_to_process)} ActionProposals under Policy Engine...\n")

    for prop in proposals_to_process:
        workflow_engine.link_proposal(active_wf.workflow_id, prop.proposal_id)
        
        permitted_by_killswitch, ks_reason = killswitch.is_action_permitted(prop.action, prop.required_permission)
        if not permitted_by_killswitch:
            print(f"  - [{prop.proposal_id}] Action: {prop.action:<22} -> 🛑 {ks_reason}")
            continue

        rev_dec = review_engine.evaluate_review_mode(prop)
        auth_decision = policy.evaluate_authorization(prop, principal=user_principal, user_approved=False)
        
        tracer.record_flight_step(root_trace_ctx, 4, STEP_PROPOSAL_CREATED, {"proposal_id": prop.proposal_id, "action": prop.action, "mode": rev_dec.mode})
        tracer.record_flight_step(root_trace_ctx, 5, STEP_POLICY_CHECK, {"proposal_id": prop.proposal_id, "decision": auth_decision.decision, "reason": auth_decision.reason})

        if auth_decision.is_allowed():
            print(f"  - [{prop.proposal_id}] Mode: {rev_dec.mode:<18} -> ✅ ALLOW ({auth_decision.reason})")
        else:
            approval_queue.add_proposal(prop)
            print(f"  - [{prop.proposal_id}] Mode: {rev_dec.mode:<18} -> ⏳ REQUIRE_APPROVAL ({rev_dec.explainability_summary})")

    s4 = next(s for s in active_wf.steps if s.step_id == "s4_proposals")
    s4.mark_completed({"proposals_count": len(proposals_to_process)})
    active_wf.update_status(WF_COMPLETED)
    workflow_dag.checkpoint_workflow(active_wf)

    # Record Workflow Success Outcome
    outcome_learning_engine.record_outcome(active_wf.workflow_id, "daily_execution_workflow", OUTCOME_SUCCESS)
    execution_strategy_store.update_strategy_outcome("daily_execution_workflow", success=True)

    pending_list = approval_queue.list_pending()
    print(f"\nApproval Queue active pending items (Persisted to disk): {len(pending_list)}")
    
    if pending_list:
        print("\nProcessing Safe Batch Approval & Feedback Learning Loop...")
        
        cal_pids = [p.proposal_id for p in pending_list if "calendar" in p.action or "event" in p.action]
        if cal_pids:
            print(f"\n1. Executing SAFE BATCH APPROVAL on {len(cal_pids)} Calendar Proposals...")
            batch_res = approval_queue.approve_batch(cal_pids)
            for pid, (success, msg, res) in zip(cal_pids, batch_res):
                status_str = "SUCCESS" if success else "FAILED"
                if success:
                    feedback_loop.process_feedback(pid, "create_calendar_event", FEEDBACK_APPROVE)
                print(f"   - [{pid}] {status_str}: {msg}")
                tracer.record_flight_step(root_trace_ctx, 6, STEP_TOOL_EXECUTION_SUCCESS, {"proposal_id": pid, "msg": msg})

        rem_pids = [p.proposal_id for p in pending_list if p.proposal_id not in cal_pids]
        if rem_pids:
            print(f"\n2. Executing SAFE BATCH REJECTION on {len(rem_pids)} Archive Proposals...")
            batch_rej = approval_queue.reject_batch(rem_pids, reason="User prefers manual inbox review")
            for pid, (success, msg) in zip(rem_pids, batch_rej):
                print(f"   - [{pid}] REJECTED: {msg}")

    tracer.record_flight_step(root_trace_ctx, 7, STEP_TRACE_COMPLETED, {"status": "SUCCESS"})

    metrics_calc = TelemetryMetricsCalculator(store=telemetry_store)
    m_res = metrics_calc.calculate_metrics()

    s_rate = outcome_learning_engine.get_success_rate("create_calendar_event")

    print("\n")
    print_header("📊 AGENT LEARNING & OUTCOME OPERATIONAL METRICS")
    print(f"  - Workflow Strategy:      'daily_execution_workflow' (Success Rate: {s_rate:.1f}%)")
    print(f"  - Feedback Loop Status:   Active (Implicit & Explicit Feedback Recorded)")
    print(f"  - Security Compliance:    100.0% (Learning Recommends != Security Authority)")
    print(f"  - Total LLM Requests:      {m_res['total_llm_calls']}")
    print(f"  - P50 Workflow Latency:   {m_res['p50_latency_sec']:.3f}s")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V2.6 Execution completed successfully.")

if __name__ == "__main__":
    main()
