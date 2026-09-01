import json
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
from personal_agent.tools.auth import GoogleAuthManager

class GoogleCalendarTool:
    def __init__(self, service: Optional[Any] = None, auth_manager: Optional[GoogleAuthManager] = None):
        if service:
            self.service = service
        else:
            self.auth_manager = auth_manager or GoogleAuthManager()
            try:
                self.service = self.auth_manager.build_service('calendar', 'v3')
            except Exception as e:
                print(f"[GoogleCalendarTool] Could not initialize live Google Calendar service: {e}")
                self.service = None

    def get_today_events(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        target_date = date.fromisoformat(date_str) if date_str else date.today()
        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)

        time_min = start_dt.isoformat() + "Z"
        time_max = end_dt.isoformat() + "Z"

        if not self.service:
            return []

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            items = events_result.get('items', [])
            return [self._normalize_event(item) for item in items]
        except Exception as e:
            print(f"[GoogleCalendarTool] Error fetching today events: {e}")
            return []

    def get_week_events(self, start_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        start_d = date.fromisoformat(start_date_str) if start_date_str else date.today()
        end_d = start_d + timedelta(days=7)

        start_dt = datetime.combine(start_d, time.min)
        end_dt = datetime.combine(end_d, time.max)

        time_min = start_dt.isoformat() + "Z"
        time_max = end_dt.isoformat() + "Z"

        if not self.service:
            return []

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            items = events_result.get('items', [])
            return [self._normalize_event(item) for item in items]
        except Exception as e:
            print(f"[GoogleCalendarTool] Error fetching week events: {e}")
            return []

    def get_free_slots(
        self,
        date_str: Optional[str] = None,
        working_hours: Tuple[int, int] = (9, 18)
    ) -> List[Dict[str, Any]]:
        target_date = date.fromisoformat(date_str) if date_str else date.today()
        start_hour, end_hour = working_hours

        work_start = datetime.combine(target_date, time(hour=start_hour, minute=0))
        work_end = datetime.combine(target_date, time(hour=end_hour, minute=0))

        events = self.get_today_events(date_str=target_date.isoformat())

        # Collect busy intervals within working hours
        busy_intervals = []
        for ev in events:
            ev_start_str = ev.get('start')
            ev_end_str = ev.get('end')
            if not ev_start_str or not ev_end_str:
                continue

            try:
                # Handle ISO format strings (with or without timezone offset)
                ev_start = datetime.fromisoformat(ev_start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                ev_end = datetime.fromisoformat(ev_end_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except ValueError:
                continue

            # Clip interval to working hours
            actual_start = max(ev_start, work_start)
            actual_end = min(ev_end, work_end)

            if actual_start < actual_end:
                busy_intervals.append((actual_start, actual_end))

        # Sort and merge busy intervals
        busy_intervals.sort(key=lambda x: x[0])
        merged_busy = []
        for interval in busy_intervals:
            if not merged_busy:
                merged_busy.append(interval)
            else:
                last_start, last_end = merged_busy[-1]
                if interval[0] <= last_end:
                    merged_busy[-1] = (last_start, max(last_end, interval[1]))
                else:
                    merged_busy.append(interval)

        # Calculate free slots
        free_slots = []
        current_cursor = work_start

        for b_start, b_end in merged_busy:
            if current_cursor < b_start:
                duration_mins = int((b_start - current_cursor).total_seconds() / 60)
                if duration_mins >= 15: # Only include slots >= 15 mins
                    free_slots.append({
                        "start": current_cursor.strftime("%H:%M"),
                        "end": b_start.strftime("%H:%M"),
                        "start_datetime": current_cursor.isoformat(),
                        "end_datetime": b_start.isoformat(),
                        "duration_minutes": duration_mins
                    })
            current_cursor = max(current_cursor, b_end)

        if current_cursor < work_end:
            duration_mins = int((work_end - current_cursor).total_seconds() / 60)
            if duration_mins >= 15:
                free_slots.append({
                    "start": current_cursor.strftime("%H:%M"),
                    "end": work_end.strftime("%H:%M"),
                    "start_datetime": current_cursor.isoformat(),
                    "end_datetime": work_end.isoformat(),
                    "duration_minutes": duration_mins
                })

        return free_slots

    def create_calendar_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Calendar service unavailable"}

        event_body = {
            'summary': summary,
            'description': description or '',
            'location': location or '',
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'}
        }

        try:
            created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()
            return {
                "status": "success",
                "event_id": created_event.get('id'),
                "htmlLink": created_event.get('htmlLink'),
                "summary": summary
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def update_calendar_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Calendar service unavailable"}

        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            if summary:
                event['summary'] = summary
            if start_time:
                event['start'] = {'dateTime': start_time, 'timeZone': 'UTC'}
            if end_time:
                event['end'] = {'dateTime': end_time, 'timeZone': 'UTC'}

            updated_event = self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            return {"status": "success", "event_id": updated_event.get('id'), "summary": updated_event.get('summary')}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def delete_calendar_event(self, event_id: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Calendar service unavailable"}

        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return {"status": "success", "deleted_event_id": event_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _normalize_event(self, item: Dict[str, Any]) -> Dict[str, Any]:
        start = item.get('start', {}).get('dateTime') or item.get('start', {}).get('date')
        end = item.get('end', {}).get('dateTime') or item.get('end', {}).get('date')
        return {
            "id": item.get('id'),
            "summary": item.get('summary', 'No Title'),
            "description": item.get('description', ''),
            "start": start,
            "end": end,
            "status": item.get('status', 'confirmed'),
            "htmlLink": item.get('htmlLink', '')
        }

# Tool wrappers for Registry / LLM Runtime
def get_today_events(date_str: Optional[str] = None) -> str:
    """Get today's calendar events."""
    tool = GoogleCalendarTool()
    events = tool.get_today_events(date_str=date_str)
    return json.dumps(events, indent=2)

def get_week_events(start_date_str: Optional[str] = None) -> str:
    """Get upcoming week's calendar events."""
    tool = GoogleCalendarTool()
    events = tool.get_week_events(start_date_str=start_date_str)
    return json.dumps(events, indent=2)

def get_free_slots(date_str: Optional[str] = None) -> str:
    """Calculate free time slots for a given day."""
    tool = GoogleCalendarTool()
    slots = tool.get_free_slots(date_str=date_str)
    return json.dumps(slots, indent=2)

def create_calendar_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None, location: Optional[str] = None) -> str:
    """Create a new calendar event."""
    tool = GoogleCalendarTool()
    res = tool.create_calendar_event(summary=summary, start_time=start_time, end_time=end_time, description=description, location=location)
    return json.dumps(res, indent=2)
