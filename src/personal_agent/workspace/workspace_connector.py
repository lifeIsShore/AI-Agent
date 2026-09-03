import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class NormalizedWorkspaceItem:
    item_id: str
    source_system: str  # gmail, calendar, tasks, drive, local, browser
    item_type: str      # email, event, task, document, file, webpage
    title: str
    content: str = ""
    author: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class GmailConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("m1", "gmail", "email", "Assignment deadline update", "Deadline moved to Friday", "prof_x@univ.edu"),
            NormalizedWorkspaceItem("m2", "gmail", "email", "Weekly Tech Newsletter", "AI developments digest", "news@digest.com")
        ]

class CalendarConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("e1", "calendar", "event", "Thesis Work Block", "Focus work in library", "user@univ.edu"),
            NormalizedWorkspaceItem("e2", "calendar", "event", "Submission Milestone", "Submit thesis proposal", "prof_x@univ.edu")
        ]

class TasksConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("t1", "tasks", "task", "Draft thesis section", "Complete methodology", "user@univ.edu")
        ]

class DriveConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("d1", "drive", "document", "Thesis_Draft_v1.docx", "Document text content", "prof_x@univ.edu")
        ]

class LocalFileConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("f1", "local", "file", "notes.txt", "Local research notes", "user@univ.edu")
        ]

class BrowserConnector:
    def get_items(self) -> List[NormalizedWorkspaceItem]:
        return [
            NormalizedWorkspaceItem("b1", "browser", "webpage", "University Portal", "Login page text", "univ.edu")
        ]

class WorkspaceConnectorRegistry:
    def __init__(self):
        self.gmail = GmailConnector()
        self.calendar = CalendarConnector()
        self.tasks = TasksConnector()
        self.drive = DriveConnector()
        self.local = LocalFileConnector()
        self.browser = BrowserConnector()

    def fetch_all_normalized_items(self) -> List[NormalizedWorkspaceItem]:
        items = []
        items.extend(self.gmail.get_items())
        items.extend(self.calendar.get_items())
        items.extend(self.tasks.get_items())
        items.extend(self.drive.get_items())
        items.extend(self.local.get_items())
        items.extend(self.browser.get_items())
        return items
