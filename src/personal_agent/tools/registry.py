from typing import Callable, Dict, Any, List
from personal_agent.tools.gmail import (
    read_recent_emails, archive_email, trash_email, mark_read, apply_label, create_draft
)
from personal_agent.tools.calendar import get_today_events, get_week_events, get_free_slots
from personal_agent.tools.tasks import list_tasks, get_task

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, schema: Dict[str, Any], func: Callable):
        self._tools[name] = func
        self._schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": schema.get("description", ""),
                "parameters": schema.get("parameters", {"type": "object", "properties": {}})
            }
        })

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    def register_default_tools(self):
        """Registers default V0.5 & V0.6 tools for Gmail, Calendar, and Tasks."""
        self.register(
            name="read_recent_emails",
            schema={"description": "Read recent emails from Gmail inbox", "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
            func=read_recent_emails
        )
        self.register(
            name="archive_email",
            schema={"description": "Archive an email message (remove from inbox)", "parameters": {"type": "object", "properties": {"msg_id": {"type": "string"}}}},
            func=archive_email
        )
        self.register(
            name="trash_email",
            schema={"description": "Move an email message to trash", "parameters": {"type": "object", "properties": {"msg_id": {"type": "string"}}}},
            func=trash_email
        )
        self.register(
            name="mark_read",
            schema={"description": "Mark an email message as read", "parameters": {"type": "object", "properties": {"msg_id": {"type": "string"}}}},
            func=mark_read
        )
        self.register(
            name="apply_label",
            schema={"description": "Apply a label to an email message", "parameters": {"type": "object", "properties": {"msg_id": {"type": "string"}, "label_name": {"type": "string"}}}},
            func=apply_label
        )
        self.register(
            name="create_draft",
            schema={"description": "Create an email reply draft", "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}}},
            func=create_draft
        )
        self.register(
            name="get_today_events",
            schema={"description": "Get today's calendar events", "parameters": {"type": "object", "properties": {"date_str": {"type": "string"}}}},
            func=get_today_events
        )
        self.register(
            name="get_week_events",
            schema={"description": "Get week's calendar events", "parameters": {"type": "object", "properties": {"start_date_str": {"type": "string"}}}},
            func=get_week_events
        )
        self.register(
            name="get_free_slots",
            schema={"description": "Calculate free calendar time slots for a day", "parameters": {"type": "object", "properties": {"date_str": {"type": "string"}}}},
            func=get_free_slots
        )
        self.register(
            name="list_tasks",
            schema={"description": "List active Google tasks", "parameters": {"type": "object", "properties": {"tasklist_id": {"type": "string"}}}},
            func=list_tasks
        )
        self.register(
            name="get_task",
            schema={"description": "Get details of a specific task", "parameters": {"type": "object", "properties": {"task_id": {"type": "string"}}}},
            func=get_task
        )
