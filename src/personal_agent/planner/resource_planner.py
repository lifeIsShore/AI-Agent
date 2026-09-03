from typing import List, Dict, Any, Tuple, Optional

class ResourceAwarePlanner:
    def __init__(self, default_task_duration_min: int = 60):
        self.default_task_duration_min = default_task_duration_min

    def get_free_time_slots(
        self,
        calendar_events: List[Dict[str, Any]],
        start_hour: int = 9,
        end_hour: int = 18
    ) -> List[Tuple[int, int]]:
        """Calculates free hour blocks between existing calendar commitments."""
        occupied_hours = set()
        for evt in calendar_events:
            start_h = evt.get("start_hour", 9)
            end_h = evt.get("end_hour", start_h + 1)
            for h in range(start_h, end_h):
                occupied_hours.add(h)

        free_slots = []
        for h in range(start_hour, end_hour):
            if h not in occupied_hours:
                free_slots.append((h, h + 1))
        return free_slots

    def allocate_task_schedules(
        self,
        tasks: List[Dict[str, Any]],
        calendar_events: List[Dict[str, Any]],
        start_hour: int = 9,
        end_hour: int = 18
    ) -> List[Dict[str, Any]]:
        """Schedules prioritized tasks into available free calendar slots without double-booking."""
        free_slots = self.get_free_time_slots(calendar_events, start_hour=start_hour, end_hour=end_hour)
        scheduled_blocks = []
        
        slot_idx = 0
        for task in tasks:
            if slot_idx >= len(free_slots):
                # No more free slots available today
                break

            slot_start, slot_end = free_slots[slot_idx]
            task_title = str(task.get("title", task.get("subject", "Task execution")))
            task_id = str(task.get("task_id", task.get("id", "t_unknown")))

            scheduled_blocks.append({
                "task_id": task_id,
                "title": task_title,
                "start_hour": slot_start,
                "end_hour": slot_end,
                "time_slot": f"{slot_start:02d}:00–{slot_end:02d}:00",
                "priority": task.get("priority", "NORMAL")
            })
            slot_idx += 1

        return scheduled_blocks
