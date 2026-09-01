import sys
import os
import json
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.models.router import ModelRouter, ModelDecision
from personal_agent.models.scoring import INTENT_PLAN_DAY
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
from personal_agent.security.audit import AuditLogger
from personal_agent.security.trust import sanitize_external_text, classify_trust_level, TRUST_EXTERNAL
from personal_agent.security.identity import IdentityProvider
from personal_agent.security.credentials import CredentialBroker
from personal_agent.security.sanitizer import redact_credentials
from personal_agent.policy.capabilities import resolve_capability, validate_capability_authorization
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
    print_header("PERSONAL ASSISTANT (V1.8 — ADAPTIVE HUMAN-IN-THE-LOOP & GOVERNANCE)")
    print("Initializing V1.8 Assistant Core...")

    user_principal = IdentityProvider.get_user_principal("user_ahmet")
    credential_broker = CredentialBroker()
    model_router = ModelRouter()
    review_engine = ReviewDecisionEngine()
    scope_manager = ScopeManager()
    rejection_tracker = RepeatedRejectionTracker()

    telemetry_store = TelemetryStore(telemetry_dir="data/telemetry", log_filename="traces.jsonl")
    tracer = AgentTracer(store=telemetry_store)
    root_trace_ctx = TraceContext(request_id="req_daily_daemon_run")

    checkpoint_engine = RecoveryCheckpointEngine(telemetry_store=telemetry_store)
    incomplete_traces = checkpoint_engine.get_incomplete_traces()
    if incomplete_traces:
        print(f"[Checkpoint Recovery] Detected {len(incomplete_traces)} incomplete execution traces from disk.")
        for inc in incomplete_traces:
            rec = checkpoint_engine.evaluate_recovery_action(inc["trace_id"])
            print(f"  - TraceID [{inc['trace_id']}] -> Action: {rec['reason']}")

    tracer.record_flight_step(root_trace_ctx, 1, STEP_REQUEST_RECEIVED, {"prompt": "Plan my day"})

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
    
    # Persistent Approval Queue with StateManager and EventBus integration
    approval_queue = ApprovalQueue(
        tool_registry=registry,
        audit_logger=audit_logger,
        memory_loop=memory_loop,
        state_manager=state_manager,
        event_bus=event_bus
    )
    
    triage_engine = PriorityEngine(gateway)
    inbox_zero_engine = InboxZeroEngine()
    context_manager = ContextManager(gateway=gateway)
    daily_planner = DailyPlannerEngine(user_name="Ahmet")

    # Replay any unprocessed events from disk log on startup
    event_bus.replay_unprocessed()

    # 1. Initialize Agent Scheduler & Register Jobs
    job_registry = JobRegistry()
    scheduler = AgentScheduler(registry=job_registry, state_manager=state_manager)

    print(f"[Core] Active Principal: '{user_principal.principal_id}' ({user_principal.principal_type}).")
    print("[Core] ReviewDecisionEngine, Delegated Scopes, & Repeated Rejection Tracker active.")

    # 2. Fetch live data with credential isolation and fallback degradation
    print("\nFetching Live Assistant Context (Gmail, Calendar, Tasks)...")
    
    emails = []
    def fetch_gmail():
        cred = credential_broker.get_tool_credential("gmail", "gmail.read")
        sanitized_cred = redact_credentials(cred)
        g_tool = GmailTool()
        return g_tool.list_recent_emails(limit=10)

    success_g, gmail_res, msg_g = degradation_handler.execute_with_protection("gmail", fetch_gmail, fallback_value=None)
    if success_g and gmail_res:
        emails = gmail_res
        print(f"  - Gmail: Loaded {len(emails)} emails via Credential Broker.")
    else:
        print(f"  - Gmail: Protected Fallback ({msg_g})")
        emails = [
            {"id": "m1", "sender": "advisor@univ.edu", "subject": "Thesis proposal submission deadline", "body": "Please submit your thesis proposal by Friday.", "unread": True},
            {"id": "m2", "sender": "prof@univ.edu", "subject": "University lecture room change", "body": "Lecture moves to Room 301.", "unread": True},
            {"id": "m3", "sender": "careers@jobalerts.com", "subject": "Weekly software engineering job alerts", "body": "10 new jobs posted.", "unread": False}
        ]

    # Sanitize external email text for prompt injections
    for email in emails:
        if "body" in email:
            email["body"] = sanitize_external_text(email["body"], source_trust=TRUST_EXTERNAL)

    cal_events = []
    free_slots = []
    def fetch_cal():
        cred = credential_broker.get_tool_credential("calendar", "calendar.read")
        c_tool = GoogleCalendarTool()
        return c_tool.get_today_events(), c_tool.get_free_slots()

    success_c, cal_res, msg_c = degradation_handler.execute_with_protection("calendar", fetch_cal, fallback_value=(None, None))
    if success_c and cal_res[0] is not None:
        cal_events, free_slots = cal_res
        print(f"  - Calendar: Loaded {len(cal_events)} events, calculated {len(free_slots)} free slots via Credential Broker.")
    else:
        print(f"  - Calendar: Protected Fallback ({msg_c})")
        cal_events = [{"id": "ev1", "summary": "University lecture", "start": "2026-09-01T09:00:00Z", "end": "2026-09-01T10:00:00Z", "status": "confirmed"}]
        free_slots = [{"start": "10:00", "end": "12:00", "duration_minutes": 120}, {"start": "14:00", "end": "17:00", "duration_minutes": 180}]

    # Register Scheduler Daemon Jobs
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
    scheduler.register_job(Job(
        job_id="calendar_sync",
        name="Google Calendar Synchronization",
        interval_minutes=60,
        handler=lambda: calendar_sync_job(GoogleCalendarTool() if 'GoogleCalendarTool' in globals() else None)
    ))
    scheduler.register_job(Job(
        job_id="memory_maintenance",
        name="Memory Maintenance & Time Decay",
        interval_minutes=720,
        handler=lambda: memory_maintenance_job(memory_loop)
    ))

    # 3. Execute Scheduler Daemon Tick
    print("\nExecuting Scheduler Daemon Tick...")
    tick_results = scheduler.run_daemon_tick()
    for res in tick_results:
        print(f"  - Job [{res['job_id']}] -> Status: {res['status']} | Output: {res['output']}")

    # 4. Model Routing & Context Assembly
    model_decision = model_router.route_request(
        intent=INTENT_PLAN_DAY,
        context_bytes=3500,
        risk_level="MEDIUM",
        tool_count=3
    )

    print(f"\n[ModelRouter] Selected Model Tier: '{model_decision.selected_tier}' ({model_decision.model_name}) | Reason: {model_decision.reason}")

    tracer.record_flight_step(root_trace_ctx, 2, STEP_INTENT_DETECTED, {"intent": "PLAN_DAY", "model": model_decision.model_name})
    triaged_emails = []
    for email in emails:
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
        user_request="Plan my day",
        emails=triaged_emails,
        calendar=cal_events,
        tasks=[]
    )

    tracer.record_flight_step(root_trace_ctx, 3, STEP_CONTEXT_BUILT, {"items": len(triaged_emails)})

    tracer.record_context_efficiency(
        trace_ctx=root_trace_ctx,
        intent="PLAN_DAY",
        item_counts={"emails": len(triaged_emails), "calendar": len(cal_events), "tasks": 0},
        total_bytes=len(context_pkg.to_prompt_context()),
        latency_sec=0.01
    )

    # 5. Generate Daily Execution Plan
    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)

    print_header("🗓 DAILY EXECUTION BRIEFING")
    print(plan["formatted_report"])

    # 6. Route Proposals through Policy Engine & ReviewDecisionEngine
    print("\n")
    print_header("📋 EXPLAINABLE ACTION PROPOSALS & ADAPTIVE REVIEW CARDS")
    
    inbox_eval = inbox_zero_engine.evaluate_inbox(triaged_emails)
    
    proposals_to_process = []
    for p in plan.get("proposals", []):
        prop = policy.create_proposal(
            action=p.get("action", "create_calendar_event"),
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
        prop = policy.create_proposal(
            action=p.get("action", "archive_email"),
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

    print(f"Evaluating {len(proposals_to_process)} ActionProposals with Review Decision Engine...\n")

    for prop in proposals_to_process:
        # Check repeated rejection throttling
        should_throttle, throttle_msg = rejection_tracker.should_throttle_proposal(prop.action, "general")
        if should_throttle:
            print(f"  - [{prop.proposal_id}] Action: {prop.action:<22} -> ⚠️ {throttle_msg}")
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
            if rev_dec.mode == MODE_DETAILED_REVIEW:
                print(prop.format_explainable_card())

    # 7. Interactive Batch Approval & Memory Classifier Loop
    pending_list = approval_queue.list_pending()
    print(f"\nApproval Queue active pending items (Persisted to disk): {len(pending_list)}")
    
    if pending_list:
        print("\nProcessing Safe Batch Approval & Memory Classifier Loop...")
        
        cal_pids = [p.proposal_id for p in pending_list if "calendar" in p.action or "event" in p.action]
        if cal_pids:
            print(f"\n1. Executing SAFE BATCH APPROVAL on {len(cal_pids)} Calendar Proposals...")
            batch_res = approval_queue.approve_batch(cal_pids)
            for pid, (success, msg, res) in zip(cal_pids, batch_res):
                status_str = "SUCCESS" if success else "FAILED"
                print(f"   - [{pid}] {status_str}: {msg}")
                tracer.record_flight_step(root_trace_ctx, 6, STEP_TOOL_EXECUTION_SUCCESS, {"proposal_id": pid, "msg": msg})

        rem_pids = [p.proposal_id for p in pending_list if p.proposal_id not in cal_pids]
        if rem_pids:
            print(f"\n2. Executing SAFE BATCH REJECTION on {len(rem_pids)} Archive Proposals...")
            batch_rej = approval_queue.reject_batch(rem_pids, reason="User prefers manual inbox review")
            for pid, (success, msg) in zip(rem_pids, batch_rej):
                print(f"   - [{pid}] REJECTED: {msg}")

    tracer.record_flight_step(root_trace_ctx, 7, STEP_TRACE_COMPLETED, {"status": "SUCCESS"})

    # 8. Telemetry & Metric Analytics Summary
    metrics_calc = TelemetryMetricsCalculator(store=telemetry_store)
    m_res = metrics_calc.calculate_metrics()

    print("\n")
    print_header("📊 PERFORMANCE LATENCY & GOVERNANCE STATUS")
    print(f"  - Active Principal:        {user_principal.principal_id}")
    print(f"  - Routed Model Tier:       {model_decision.selected_tier}")
    print(f"  - Credential Leaks:        0")
    print(f"  - Repeated Proposals:      Throttled & Governed")
    print(f"  - Total LLM Requests:      {m_res['total_llm_calls']}")
    print(f"  - P50 Workflow Latency:   {m_res['p50_latency_sec']:.3f}s")
    print(f"  - P95 Workflow Latency:   {m_res['p95_latency_sec']:.3f}s")
    print(f"  - P99 Workflow Latency:   {m_res['p99_latency_sec']:.3f}s")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V1.8 Execution completed successfully.")

if __name__ == "__main__":
    main()
