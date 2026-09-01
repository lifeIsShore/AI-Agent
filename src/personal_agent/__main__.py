import sys
import os
import json
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.registry import ToolRegistry
from personal_agent.tools.gmail import GmailTool
from personal_agent.tools.calendar import GoogleCalendarTool
from personal_agent.tools.tasks import GoogleTasksTool
from personal_agent.policy.engine import PolicyEngine, PermissionLevel
from personal_agent.policy.proposal import ActionProposal, STATUS_PENDING_APPROVAL, STATUS_AUTO_APPROVED
from personal_agent.policy.approval import ApprovalQueue
from personal_agent.security.audit import AuditLogger
from personal_agent.state.manager import StateManager
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
    print_header("PERSONAL ASSISTANT (V1.0 — PERSISTENT AGENT RUNTIME)")
    print("Initializing V1.0 Persistent Assistant Runtime...")

    gateway = ModelGateway(provider="ollama")
    registry = ToolRegistry()
    registry.register_default_tools()
    
    state_manager = StateManager(state_dir="data/state")
    policy = PolicyEngine()
    audit_logger = AuditLogger()
    memory_manager = MemoryManager(gateway=gateway)
    memory_loop = MemoryLearningLoop(memory_manager=memory_manager)
    
    # Persistent Approval Queue auto-restores pending state from data/state/proposals.json
    approval_queue = ApprovalQueue(
        tool_registry=registry,
        audit_logger=audit_logger,
        memory_loop=memory_loop,
        state_manager=state_manager
    )
    
    triage_engine = PriorityEngine(gateway)
    inbox_zero_engine = InboxZeroEngine()
    context_manager = ContextManager(gateway=gateway)
    daily_planner = DailyPlannerEngine(user_name="Ahmet")

    # 1. Initialize Agent Scheduler & Register Jobs
    job_registry = JobRegistry()
    scheduler = AgentScheduler(registry=job_registry, state_manager=state_manager)

    print("[Core] Persistent State Store (data/state/), Approval Queue, & Job Scheduler loaded.")

    # 2. Fetch live data with graceful fallbacks
    print("\nFetching Live Assistant Context (Gmail, Calendar, Tasks)...")
    
    # Gmail
    emails = []
    try:
        gmail_tool = GmailTool()
        emails = gmail_tool.list_recent_emails(limit=10)
        print(f"  - Gmail: Loaded {len(emails)} emails.")
    except Exception as e:
        print(f"  - Gmail: Using sample data (Notice: {e})")
        emails = [
            {"id": "m1", "sender": "advisor@univ.edu", "subject": "Thesis proposal submission deadline", "body": "Please submit your thesis proposal by Friday.", "unread": True},
            {"id": "m2", "sender": "prof@univ.edu", "subject": "University lecture room change", "body": "Lecture moves to Room 301.", "unread": True},
            {"id": "m3", "sender": "careers@jobalerts.com", "subject": "Weekly software engineering job alerts", "body": "10 new jobs posted.", "unread": False}
        ]

    # Calendar
    cal_events = []
    free_slots = []
    try:
        cal_tool = GoogleCalendarTool()
        cal_events = cal_tool.get_today_events()
        free_slots = cal_tool.get_free_slots()
        print(f"  - Calendar: Loaded {len(cal_events)} events, calculated {len(free_slots)} free slots.")
    except Exception as e:
        print("  - Calendar: Using sample day schedule.")

    if not cal_events:
        cal_events = [
            {"id": "ev1", "summary": "University lecture", "start": "2026-09-01T09:00:00Z", "end": "2026-09-01T10:00:00Z", "status": "confirmed"}
        ]
    if not free_slots:
        free_slots = [
            {"start": "10:00", "end": "12:00", "duration_minutes": 120},
            {"start": "12:00", "end": "13:00", "duration_minutes": 60},
            {"start": "14:00", "end": "15:00", "duration_minutes": 60},
            {"start": "15:00", "end": "17:00", "duration_minutes": 120}
        ]

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
        handler=lambda: calendar_sync_job(GoogleCalendarTool() if 'GoogleCalendarTool' in globals() else cal_tool)
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

    # 4. Triaging & Context Assembly
    triaged_emails = []
    for email in emails:
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

    # 5. Generate Daily Execution Plan
    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)

    print_header("🗓 DAILY EXECUTION BRIEFING")
    print(plan["formatted_report"])

    # 6. Route Proposals through Policy Engine into ApprovalQueue
    print("\n")
    print_header("📋 EXPLAINABLE ACTION PROPOSALS & APPROVAL QUEUE")
    
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

    print(f"Evaluating {len(proposals_to_process)} ActionProposals with Policy Engine...\n")

    for prop in proposals_to_process:
        allowed, reason = policy.check_proposal(prop, user_approved=False)
        if allowed:
            print(f"  - [{prop.proposal_id}] Action: {prop.action:<22} -> ✅ AUTO_APPROVED ({reason})")
        else:
            approval_queue.add_proposal(prop)
            print(f"  - [{prop.proposal_id}] Action: {prop.action:<22} -> ⏳ PENDING_APPROVAL (TTL Expires: {prop.expires_at[:19]})")

    # 7. Interactive Batch Approval & Memory Classifier Demo
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

        rem_pids = [p.proposal_id for p in pending_list if p.proposal_id not in cal_pids]
        if rem_pids:
            print(f"\n2. Executing SAFE BATCH REJECTION on {len(rem_pids)} Archive Proposals...")
            batch_rej = approval_queue.reject_batch(rem_pids, reason="User prefers manual inbox review")
            for pid, (success, msg) in zip(rem_pids, batch_rej):
                print(f"   - [{pid}] REJECTED: {msg}")

    # 8. Persistent Audit & State Summary
    print("\n")
    print_header("📜 AUDIT LOG RECENT RECORDS (data/logs/audit.jsonl)")
    recent_audit_logs = audit_logger.get_recent_logs(limit=5)
    for log in recent_audit_logs:
        print(f"[{log['timestamp'][:19]}] ID: {log['proposal_id']} | Action: {log['action']} | Decision: {log['policy_decision']} | Status: {log['execution_status']}")

    print("\n")
    print_header("🧠 PERSISTENT STATE STORE (data/state/runtime.json)")
    saved_runtime = state_manager.load_runtime_state()
    if saved_runtime:
        print(f"  - Last Daemon Tick: {saved_runtime.get('last_tick')[:19]}")
        print(f"  - Registered Daemon Jobs: {len(saved_runtime.get('jobs', []))}")
        for j in saved_runtime.get('jobs', []):
            print(f"    * Job [{j['job_id']}] '{j['name']}': Next Run -> {j['next_run'][:19]}")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V1.0 Execution completed successfully.")

if __name__ == "__main__":
    main()
