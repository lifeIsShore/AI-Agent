import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class BrowserTab:
    tab_id: str
    url: str
    title: str = "Blank"
    html_content: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BrowserSession:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        self.tabs: Dict[str, BrowserTab] = {}
        self.active_tab_id: Optional[str] = None
        self.is_active: bool = True

    def create_tab(self, url: str = "about:blank", title: str = "New Tab") -> BrowserTab:
        tab_id = f"tab_{uuid.uuid4().hex[:6]}"
        tab = BrowserTab(tab_id=tab_id, url=url, title=title)
        self.tabs[tab_id] = tab
        self.active_tab_id = tab_id
        return tab

    def navigate(self, url: str) -> BrowserTab:
        if not self.active_tab_id or self.active_tab_id not in self.tabs:
            return self.create_tab(url=url)
        
        tab = self.tabs[self.active_tab_id]
        tab.url = url
        tab.title = f"Page - {url}"
        return tab

    def get_active_tab(self) -> Optional[BrowserTab]:
        if self.active_tab_id and self.active_tab_id in self.tabs:
            return self.tabs[self.active_tab_id]
        return None

    def close_tab(self, tab_id: str) -> bool:
        if tab_id in self.tabs:
            del self.tabs[tab_id]
            if self.active_tab_id == tab_id:
                self.active_tab_id = list(self.tabs.keys())[0] if self.tabs else None
            return True
        return False

    def close_session(self):
        self.tabs.clear()
        self.active_tab_id = None
        self.is_active = False
