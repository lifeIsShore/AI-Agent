from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from personal_agent.context.package import ContextPackage

class DailyPlannerEngine:
    def __init__(self, user_name: str = "Ahmet"):
        self.user_name = user_name

    def generate_daily_plan(
        self,
        context: ContextPackage,
        free_slots: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generates a structured daily execution plan and proposals based on context."""
        
        events = context.calendar
        tasks = context.tasks
        emails = context.emails
        memories = context.memory

        # 1. Analyze Memory Preferences
        prefer_univ_afternoon = False
        for mem in memories:
            content_lower = mem.get("content", "").lower()
            if "university" in content_lower and ("afternoon" in content_lower or "14:00" in content_lower or "2pm" in content_lower):
                prefer_univ_afternoon = True

        # 2. Categorize Priorities (🔴 URGENT, 🟡 IMPORTANT, 🟢 NORMAL)
        priorities = []
        
        # From Emails (Only emails with requires_action == True AND requires_planning == True are scheduled!)
        for email in emails:
            req_act = email.get("requires_action", False)
            req_plan = email.get("requires_planning", False)
            
            # Skip emails that don't require actual calendar planning (newsletters, job digests, receipts, simple alerts)
            if not (req_act and req_plan):
                continue

            prio = email.get("priority", "normal")
            subj = email.get("subject", "Email")
            category = email.get("category", "general")
            sender = email.get("sender", "Unknown")
            action = email.get("suggested_action", f"Reply to {sender}")

            if prio == "urgent":
                priorities.append({
                    "priority": "urgent",
                    "emoji": "🔴",
                    "title": f"Reply: {subj}",
                    "type": "email",
                    "category": category,
                    "raw": email
                })
            elif prio == "important":
                priorities.append({
                    "priority": "important",
                    "emoji": "🟡",
                    "title": f"Reply to {category} email: {subj}",
                    "type": "email",
                    "category": category,
                    "raw": email
                })
            else:
                priorities.append({
                    "priority": "normal",
                    "emoji": "🟢",
                    "title": f"Task: {subj}",
                    "type": "email",
                    "category": category,
                    "raw": email
                })

        # From Tasks
        for t in tasks:
            title = t.get("title", "Task")
            notes = t.get("notes", "")
            title_lower = title.lower()
            
            if "urgent" in title_lower or "thesis" in title_lower or "deadline" in title_lower:
                prio_tag = "urgent"
                emoji = "🔴"
            elif "important" in title_lower or "university" in title_lower:
                prio_tag = "important"
                emoji = "🟡"
            else:
                prio_tag = "normal"
                emoji = "🟢"

            priorities.append({
                "priority": prio_tag,
                "emoji": emoji,
                "title": title,
                "type": "task",
                "category": "task",
                "raw": t
            })

        # Fallback priorities if empty
        if not priorities:
            priorities = [
                {"priority": "urgent", "emoji": "🔴", "title": "Thesis proposal", "type": "task", "category": "thesis"},
                {"priority": "important", "emoji": "🟡", "title": "Reply to university email", "type": "email", "category": "university"},
                {"priority": "normal", "emoji": "🟢", "title": "Review job alerts", "type": "task", "category": "general"}
            ]

        # 3. Assemble Timeline (Existing Events + Scheduled Free Slots)
        schedule = []
        
        # Existing Calendar Events
        for ev in events:
            if isinstance(ev, dict):
                s_str = ev.get("start", "")
                e_str = ev.get("end", "")
                summary = ev.get("summary", "Event")
                
                start_time_fmt = self._format_time_str(s_str)
                end_time_fmt = self._format_time_str(e_str)
                
                schedule.append({
                    "time": f"{start_time_fmt}–{end_time_fmt}",
                    "title": summary,
                    "type": "fixed_event",
                    "start_time": start_time_fmt,
                    "end_time": end_time_fmt
                })

        # Process free slots for scheduling priority items
        avail_slots = free_slots or [
            {"start": "10:00", "end": "12:00", "duration_minutes": 120},
            {"start": "12:00", "end": "13:00", "duration_minutes": 60},
            {"start": "14:00", "end": "15:00", "duration_minutes": 60},
            {"start": "15:00", "end": "17:00", "duration_minutes": 120}
        ]

        proposals = []
        slot_idx = 0

        # Separate items considering memory preference
        morning_items = []
        afternoon_items = []

        for item in priorities:
            cat = item.get("category", "")
            if prefer_univ_afternoon and (cat == "university" or "university" in item["title"].lower()):
                afternoon_items.append(item)
            else:
                morning_items.append(item)

        ordered_items = morning_items + afternoon_items

        for slot in avail_slots:
            slot_start = slot.get("start", "09:00")
            slot_end = slot.get("end", "10:00")
            
            # Check if this slot is 12:00-13:00 -> reserve for Lunch if not booked
            if slot_start == "12:00":
                schedule.append({
                    "time": f"{slot_start}–{slot_end}",
                    "title": "Lunch",
                    "type": "break",
                    "start_time": slot_start,
                    "end_time": slot_end
                })
                continue

            # Assign from items
            if slot_idx < len(ordered_items):
                target_item = ordered_items[slot_idx]
                
                # Check afternoon preference constraint
                slot_hour = int(slot_start.split(":")[0])
                if prefer_univ_afternoon and target_item in afternoon_items and slot_hour < 14:
                    # Skip morning slots for university afternoon preference items
                    continue
                    
                schedule.append({
                    "time": f"{slot_start}–{slot_end}",
                    "title": target_item["title"],
                    "type": "planned_task",
                    "start_time": slot_start,
                    "end_time": slot_end
                })

                proposals.append({
                    "proposal_id": f"prop_{slot_idx + 1}",
                    "action": "create_event",
                    "summary": target_item["title"],
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "reason": f"Allocated into free slot ({slot_start}–{slot_end})" + (" [Applied Memory: University emails after 14:00]" if slot_hour >= 14 and target_item in afternoon_items else "")
                })

                slot_idx += 1

        # Sort schedule by start time
        schedule.sort(key=lambda x: x.get("start_time", "00:00"))

        # 4. Generate Formatted Output Report
        report_lines = [
            f"Good morning {self.user_name}.\n",
            "Today:\n"
        ]
        
        for item in schedule:
            report_lines.append(f"{item['time']:<12} {item['title']}")
            
        report_lines.append("\nPriority:")
        for item in priorities:
            report_lines.append(f"{item['emoji']} {item['title']}")

        if proposals:
            report_lines.append("\nPlanning Proposals:")
            for prop in proposals:
                report_lines.append(f"👉 Proposal: Schedule '{prop['summary']}' from {prop['start_time']} to {prop['end_time']}? ({prop['reason']})")

        formatted_report = "\n".join(report_lines)

        return {
            "greeting": f"Good morning {self.user_name}.",
            "schedule": schedule,
            "priorities": priorities,
            "proposals": proposals,
            "formatted_report": formatted_report,
            "memory_applied": prefer_univ_afternoon
        }

    def _format_time_str(self, time_val: str) -> str:
        if not time_val:
            return "00:00"
        if "T" in time_val:
            try:
                dt = datetime.fromisoformat(time_val.replace('Z', '+00:00'))
                return dt.strftime("%H:%M")
            except ValueError:
                pass
        return str(time_val)[:5]
