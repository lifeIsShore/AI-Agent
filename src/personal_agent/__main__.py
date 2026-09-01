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
from personal_agent.policy.proposal import ActionProposal
from personal_agent.security.audit import AuditLogger
from personal_agent.triage.engine import PriorityEngine
from personal_agent.triage.inbox_zero import InboxZeroEngine
from personal_agent.context.manager import ContextManager
from personal_agent.memory.manager import MemoryManager
from personal_agent.planner.daily_planner import DailyPlannerEngine

def print_header(title: str):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL ASSISTANT (V0.7 — ACTION PROPOSALS & AUDIT ARCHITECTURE)")
    print("Initializing V0.7 Assistant Core...")

    gateway = ModelGateway(provider="ollama")
    registry = ToolRegistry()
    registry.register_default_tools()
    
    policy = PolicyEngine()
    audit_logger = AuditLogger()
    triage_engine = PriorityEngine(gateway)
    inbox_zero_engine = InboxZeroEngine()
    memory_manager = MemoryManager(gateway=gateway)
    context_manager = ContextManager(gateway=gateway)
    daily_planner = DailyPlannerEngine(user_name="Ahmet")

    print("[Core] ActionProposal models, Policy Security Boundary, & AuditLogger initialized.")

    # 1. Fetch live data with graceful fallbacks
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

    # Tasks
    tasks = []
    try:
        tasks_tool = GoogleTasksTool()
        tasks = tasks_tool.list_tasks()
        print(f"  - Tasks: Loaded {len(tasks)} tasks.")
    except Exception as e:
        print("  - Tasks: Using sample active task list.")

    if not tasks:
        tasks = [
            {"id": "t1", "title": "Thesis proposal work", "status": "needsAction"},
            {"id": "t2", "title": "Review job alerts", "status": "needsAction"}
        ]

    # 2. Triaging & Context Assembly
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
        tasks=tasks
    )

    # 3. Generate Daily Execution Plan
    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)

    print_header("🗓 DAILY EXECUTION BRIEFING")
    print(plan["formatted_report"])

    # 4. Process Proposals through ActionProposal -> PolicyEngine -> AuditLogger
    print("\n")
    print_header("📋 ACTION PROPOSAL & AUDIT LOGGING PIPELINE")
    
    inbox_eval = inbox_zero_engine.evaluate_inbox(triaged_emails)
    
    proposals_to_process = []
    
    # Calendar proposals
    for p in plan.get("proposals", []):
        prop = policy.create_proposal(
            action=p.get("action", "create_calendar_event"),
            target="primary_calendar",
            parameters={"summary": p.get("summary"), "start_time": p.get("start_time"), "end_time": p.get("end_time")},
            reason=p.get("reason", "Daily planner schedule block")
        )
        proposals_to_process.append(prop)

    # Inbox Zero proposals
    for p in inbox_eval.get("archive_proposals", [])[:3]:
        prop = policy.create_proposal(
            action=p.get("action", "archive_email"),
            target=f"email_{p.get('msg_id')}",
            parameters={"msg_id": p.get("msg_id")},
            reason=p.get("reason", "Inbox Zero archive recommendation")
        )
        proposals_to_process.append(prop)

    print(f"Processing {len(proposals_to_process)} structured ActionProposals through Policy Engine...\n")

    for prop in proposals_to_process:
        allowed, reason = policy.check_proposal(prop, user_approved=False)
        status_str = "✅ AUTO-APPROVED" if allowed else "⛔ BLOCKED (NEEDS APPROVAL)"
        
        # Log to Audit Logger
        audit_logger.log_proposal(
            proposal=prop,
            policy_decision=reason,
            user_approved=False,
            execution_status="APPROVED" if allowed else "BLOCKED",
            execution_result="Simulated proposal evaluation",
            latency_sec=0.01
        )

        print(f"Proposal [{prop.proposal_id}]")
        print(f"  - Action:     {prop.action}")
        print(f"  - Target:     {prop.target}")
        print(f"  - Risk Level: {prop.risk_level} | Permission: {prop.required_permission}")
        print(f"  - Status:     {status_str}")
        print(f"  - Reason:     {prop.reason}\n")

    # 5. Display Persistent Audit Summary
    print_header("📜 AUDIT LOG RECENT RECORDS (data/logs/audit.jsonl)")
    recent_audit_logs = audit_logger.get_recent_logs(limit=5)
    for log in recent_audit_logs:
        print(f"[{log['timestamp'][:19]}] ID: {log['proposal_id']} | Action: {log['action']} | Risk: {log['risk_level']} | Status: {log['execution_status']}")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V0.7 Execution completed successfully.")

if __name__ == "__main__":
    main()
