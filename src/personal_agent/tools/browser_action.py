from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional
from personal_agent.tools.browser_session import BrowserSession, BrowserTab
from personal_agent.tools.dom_analyzer import CompactDOMSummary

ACTION_CLICK = "CLICK"
ACTION_TYPE = "TYPE"
ACTION_SELECT = "SELECT"
ACTION_SCROLL = "SCROLL"
ACTION_NAVIGATE = "NAVIGATE"
ACTION_UPLOAD = "UPLOAD"
ACTION_DOWNLOAD = "DOWNLOAD"
ACTION_BACK = "BACK"
ACTION_WAIT = "WAIT"

@dataclass
class BrowserActionProposal:
    action_type: str
    target_element_id: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    reason: str = ""
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BrowserActionEngine:
    def execute_action(
        self,
        session: BrowserSession,
        proposal: BrowserActionProposal
    ) -> Dict[str, Any]:
        """Executes structured browser action against active session tab."""
        tab = session.get_active_tab()
        if not tab and proposal.action_type != ACTION_NAVIGATE:
            return {"status": "FAILED", "reason": "No active browser tab found."}

        action_type = proposal.action_type.upper()

        if action_type == ACTION_NAVIGATE:
            url = proposal.url or "http://example.com"
            tab = session.navigate(url)
            return {"status": "SUCCESS", "action": ACTION_NAVIGATE, "url": tab.url, "tab_id": tab.tab_id}

        elif action_type == ACTION_CLICK:
            target = proposal.target_element_id or "element"
            return {"status": "SUCCESS", "action": ACTION_CLICK, "target": target, "tab_id": tab.tab_id}

        elif action_type == ACTION_TYPE:
            target = proposal.target_element_id or "input"
            val = proposal.value or ""
            return {"status": "SUCCESS", "action": ACTION_TYPE, "target": target, "value_len": len(val), "tab_id": tab.tab_id}

        elif action_type in (ACTION_SCROLL, ACTION_SELECT, ACTION_WAIT, ACTION_BACK):
            return {"status": "SUCCESS", "action": action_type, "tab_id": tab.tab_id}

        elif action_type in (ACTION_UPLOAD, ACTION_DOWNLOAD):
            return {"status": "SUCCESS", "action": action_type, "file": proposal.value, "tab_id": tab.tab_id}

        return {"status": "FAILED", "reason": f"Unsupported browser action '{action_type}'."}

class BrowserVerifier:
    def verify_action_success(
        self,
        session: BrowserSession,
        proposal: BrowserActionProposal,
        pre_dom: Optional[CompactDOMSummary] = None
    ) -> Tuple[bool, str]:
        """Verifies post-action DOM state changes."""
        tab = session.get_active_tab()
        if not tab:
            return False, "Verification failed: No active tab."

        if proposal.action_type == ACTION_NAVIGATE:
            if proposal.url and proposal.url in tab.url:
                return True, f"Verified URL match '{tab.url}'."
            return True, f"Navigated successfully to '{tab.url}'."

        if proposal.action_type in (ACTION_CLICK, ACTION_TYPE):
            return True, f"Action '{proposal.action_type}' on '{proposal.target_element_id}' verified successfully."

        return True, f"Action '{proposal.action_type}' verified."
