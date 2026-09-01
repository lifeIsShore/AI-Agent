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
    print_header("PERSONAL ASSISTANT (V0.6 — GMAIL PRODUCTIVITY & DAILY PLANNER)")
    print("Initializing V0.6 Assistant Core...")

    gateway = ModelGateway(provider="ollama")
    registry = ToolRegistry()
    registry.register_default_tools()
    
    policy = PolicyEngine()
    triage_engine = PriorityEngine(gateway)
    inbox_zero_engine = InboxZeroEngine()
    memory_manager = MemoryManager(gateway=gateway)
    context_manager = ContextManager(gateway=gateway)
    daily_planner = DailyPlannerEngine(user_name="Ahmet")

    print("[Core] Registered tools, Intent Budgets, & Security Policy Engine loaded.")

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

    # 2. Perform Structured Email Priority Triage (V0.5.1 with requires_planning)
    print("\nTriaging emails with PriorityEngine (structured requires_planning flag)...")
    triaged_emails = []
    planning_emails_count = 0
    for email in emails:
        analysis, _ = triage_engine.evaluate(email)
        analysis["id"] = email.get("id")
        analysis["sender"] = email.get("sender")
        analysis["subject"] = email.get("subject")
        triaged_emails.append(analysis)
        if analysis.get("requires_planning"):
            planning_emails_count += 1

    print(f"  - Triaged {len(triaged_emails)} emails -> {planning_emails_count} marked requires_planning=True for Calendar.")

    # 3. Assemble Intent-Dependent Context
    print("Assembling intent-dependent context package with ContextManager...")
    context_pkg = context_manager.assemble_context(
        user_request="Plan my day",
        emails=triaged_emails,
        calendar=cal_events,
        tasks=tasks
    )

    print(f"  - Intent: PLAN_DAY -> Budgets: max_emails={context_pkg.trace['budgets']['max_emails']} (planning emails only), RAG={context_pkg.trace['budgets']['max_rag_chunks']}")

    # 4. Generate Daily Execution Plan
    print("\nSynthesizing Daily Plan with DailyPlannerEngine...\n")
    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)

    print_header("🗓 DAILY EXECUTION BRIEFING")
    print(plan["formatted_report"])

    # 5. Inbox Zero Engine Proposals (V0.6)
    print("\n")
    print_header("📥 V0.6 GMAIL INBOX ZERO ENGINE")
    inbox_eval = inbox_zero_engine.evaluate_inbox(triaged_emails)
    print(f"{inbox_eval['summary']}\n")

    if inbox_eval["archive_proposals"]:
        print("Proposed Archive Actions (requires_planning = False):")
        for prop in inbox_eval["archive_proposals"][:3]:
            print(f"  - [Archive] {prop['subject']} ({prop['reason']})")
        if len(inbox_eval["archive_proposals"]) > 3:
            print(f"    ... and {len(inbox_eval['archive_proposals']) - 3} more.")
        print()

    if inbox_eval["draft_proposals"]:
        print("Proposed Reply Drafts:")
        for prop in inbox_eval["draft_proposals"]:
            print(f"  - [Draft Reply] To: {prop['to']} | Subject: {prop['subject']}")

    # 6. Security & Policy Enforcement Audit
    print("\n")
    print_header("🔒 POLICY ENGINE SECURITY LEVEL AUDIT")
    print("Tool Operation Permissions Matrix:")
    print("──────────────────────────────")
    
    test_ops = [
        ("read_recent_emails", "Read emails"),
        ("get_today_events", "Read calendar"),
        ("list_tasks", "Read tasks"),
        ("get_free_slots", "Calculate free time"),
        ("generate_daily_plan", "Suggest schedule"),
        ("archive_email", "Archive email"),
        ("trash_email", "Move email to trash"),
        ("apply_label", "Apply Gmail label"),
        ("create_draft", "Create email reply draft"),
        ("create_calendar_event", "Create calendar event"),
        ("complete_task", "Complete task")
    ]
    
    for tool_name, desc in test_ops:
        lvl = policy.get_permission_level(tool_name)
        allowed, reason = policy.check_permission(tool_name, {})
        status_str = "✅ AUTO-ALLOWED" if allowed else "⛔ REQUIRES HUMAN APPROVAL"
        print(f"  - {desc:<25} [{lvl.name:<9}] -> {status_str}")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V0.6 Execution completed successfully.")

if __name__ == "__main__":
    main()
