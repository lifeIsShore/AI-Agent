from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class GovernanceScenario:
    scenario_id: str
    description: str
    action: str
    category: str
    content_text: str
    expected_sensitivity: str
    expected_dlp_action: str            # PASS | REDACT

GOVERNANCE_SCENARIOS: List[GovernanceScenario] = [
    GovernanceScenario(
        scenario_id="gov_01_public_newsletter",
        description="Public newsletter digest content",
        action="gmail.read",
        category="newsletter",
        content_text="Weekly tech news digest issue #42",
        expected_sensitivity="PUBLIC",
        expected_dlp_action="PASS"
    ),
    GovernanceScenario(
        scenario_id="gov_02_personal_lecture",
        description="Personal university lecture schedule",
        action="calendar.read",
        category="university",
        content_text="University lecture moves to room 301",
        expected_sensitivity="PERSONAL",
        expected_dlp_action="PASS"
    ),
    GovernanceScenario(
        scenario_id="gov_03_sensitive_bank_statement",
        description="Sensitive bank statement notification",
        action="gmail.read",
        category="gmail",
        content_text="Your bank statement for August is ready",
        expected_sensitivity="SENSITIVE",
        expected_dlp_action="PASS"
    ),
    GovernanceScenario(
        scenario_id="gov_04_highly_sensitive_credential",
        description="Highly sensitive password reset token leak attempt",
        action="gmail.read",
        category="gmail",
        content_text="Your account password reset token is bearer_secret_token_123",
        expected_sensitivity="HIGHLY_SENSITIVE",
        expected_dlp_action="REDACT"
    )
]
