import re
from typing import Dict, Any

SENSITIVITY_PUBLIC = "PUBLIC"
SENSITIVITY_INTERNAL = "INTERNAL"
SENSITIVITY_PERSONAL = "PERSONAL"
SENSITIVITY_SENSITIVE = "SENSITIVE"
SENSITIVITY_HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"

HIGHLY_SENSITIVE_PATTERNS = [
    r"(?i)password",
    r"(?i)reset\s+token",
    r"(?i)bearer_",
    r"(?i)credit\s+card",
    r"(?i)social\s+security",
    r"(?i)iban\s+code",
    r"(?i)bank\s+pin",
    r"(?i)private\s+key"
]

SENSITIVE_PATTERNS = [
    r"(?i)bank\s+statement",
    r"(?i)legal\s+notice",
    r"(?i)tax\s+return",
    r"(?i)salary\s+slip",
    r"(?i)contract\s+draft"
]

class DataClassifier:
    def classify_sensitivity(self, text: str, category: str = "") -> str:
        """Classifies content sensitivity level into PUBLIC, INTERNAL, PERSONAL, SENSITIVE, or HIGHLY_SENSITIVE."""
        if not text:
            return SENSITIVITY_PUBLIC

        for pat in HIGHLY_SENSITIVE_PATTERNS:
            if re.search(pat, text):
                return SENSITIVITY_HIGHLY_SENSITIVE

        for pat in SENSITIVE_PATTERNS:
            if re.search(pat, text):
                return SENSITIVITY_SENSITIVE

        cat_lower = category.lower()
        if cat_lower in ["newsletter", "job_alert", "promotional"]:
            return SENSITIVITY_PUBLIC
        elif cat_lower in ["university", "thesis", "calendar_personal"]:
            return SENSITIVITY_PERSONAL

        return SENSITIVITY_PERSONAL
