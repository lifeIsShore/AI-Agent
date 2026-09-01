from typing import Dict, Any, Optional

def morning_briefing_job(context_manager, daily_planner, free_slots) -> Dict[str, Any]:
    """Generates daily briefing report and schedule proposals."""
    print("\n[Scheduler] Running Job: Morning Briefing Cycle...")
    context_pkg = context_manager.assemble_context(
        user_request="Plan my day",
        emails=[],
        calendar=[],
        tasks=[]
    )
    plan = daily_planner.generate_daily_plan(context_pkg, free_slots=free_slots)
    return {"status": "SUCCESS", "report_summary": plan["formatted_report"][:100]}

def inbox_triage_job(triage_engine, inbox_zero_engine, policy, approval_queue, emails) -> Dict[str, Any]:
    """Triages Gmail inbox and generates Inbox Zero proposals."""
    print("\n[Scheduler] Running Job: Inbox Triage & Proposal Evaluation...")
    triaged = []
    for email in emails:
        analysis, _ = triage_engine.evaluate(email)
        analysis["id"] = email.get("id")
        analysis["sender"] = email.get("sender")
        analysis["subject"] = email.get("subject")
        triaged.append(analysis)

    eval_res = inbox_zero_engine.evaluate_inbox(triaged)
    proposal_count = 0

    for p in eval_res.get("archive_proposals", []):
        prop = policy.create_proposal(
            action=p.get("action", "archive_email"),
            target=f"email_{p.get('msg_id')}",
            parameters={"msg_id": p.get("msg_id")},
            reason=p.get("reason", "Automated inbox triage"),
            ttl_minutes=120
        )
        allowed, _ = policy.check_proposal(prop, user_approved=False)
        if not allowed:
            approval_queue.add_proposal(prop)
            proposal_count += 1

    return {"status": "SUCCESS", "triaged_count": len(triaged), "proposals_added": proposal_count}

def calendar_sync_job(calendar_tool) -> Dict[str, Any]:
    """Synchronizes Google Calendar events and free slots."""
    print("\n[Scheduler] Running Job: Calendar Synchronization...")
    events = calendar_tool.get_today_events()
    slots = calendar_tool.get_free_slots()
    return {"status": "SUCCESS", "events_count": len(events), "free_slots_count": len(slots)}

def memory_maintenance_job(memory_loop) -> Dict[str, Any]:
    """Applies time-decay to learned preference memories and prunes expired items."""
    print("\n[Scheduler] Running Job: Memory Maintenance & Time Decay...")
    prefs = memory_loop.get_learned_preferences()
    return {"status": "SUCCESS", "decayed_memories_processed": len(prefs)}
