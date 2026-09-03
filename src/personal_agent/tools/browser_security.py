import re
from typing import Tuple, Dict, Any, Optional

CAP_BROWSER_READ = "BROWSER_READ"
CAP_BROWSER_NAVIGATE = "BROWSER_NAVIGATE"
CAP_BROWSER_INTERACT = "BROWSER_INTERACT"
CAP_BROWSER_FORM = "BROWSER_FORM"
CAP_BROWSER_UPLOAD = "BROWSER_UPLOAD"
CAP_BROWSER_DOWNLOAD = "BROWSER_DOWNLOAD"
CAP_BROWSER_EXTERNAL_ACTION = "BROWSER_EXTERNAL_ACTION"

HARD_BLOCKED_TERMS = {
    "password", "passwd", "credit_card", "bank_account", "transfer_money",
    "delete_account", "confirm_purchase", "accept_legal", "security_setting"
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(your\s+)?previous\s+instructions",
    r"disregard\s+all\s+prior\s+prompts",
    r"send\s+(all\s+)?emails\s+to",
    r"exfiltrate",
    r"bypass\s+security"
]

class BrowserSecurityEngine:
    def __init__(self):
        self.hard_blocked_keywords = HARD_BLOCKED_TERMS

    def evaluate_browser_permission(
        self,
        action_type: str,
        target_description: str,
        url: str = "",
        user_approved: bool = False
    ) -> Tuple[bool, str]:
        """Evaluates browser action against capability gates and hard safety blocks."""
        combined_text = f"{action_type} {target_description} {url}".lower()

        # 1. Hard Blocked Sensitive Actions Check
        matched_blocked = [k for k in self.hard_blocked_keywords if k in combined_text]
        if matched_blocked and not user_approved:
            return False, f"Browser Security HARD BLOCK: Action on '{matched_blocked[0]}' requires explicit human approval."

        return True, f"Browser action '{action_type}' permitted under security policy."

    def sanitize_webpage_content(self, text_content: str) -> Tuple[str, bool]:
        """Sanitizes untrusted webpage text to prevent prompt injection attacks."""
        detected = False
        sanitized = text_content

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                detected = True
                sanitized = re.sub(pattern, "[UNTRUSTED_CONTENT_FILTERED]", sanitized, flags=re.IGNORECASE)

        return sanitized, detected
