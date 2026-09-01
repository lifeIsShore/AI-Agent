import re
from typing import Dict, Any

TRUST_SYSTEM = "SYSTEM"
TRUST_USER = "USER"
TRUST_TRUSTED_MEMORY = "TRUSTED_MEMORY"
TRUST_EXTERNAL = "EXTERNAL"

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
    r"(?i)system\s+message:",
    r"(?i)delete\s+(all\s+)?emails",
    r"(?i)forward\s+all\s+emails",
    r"(?i)transfer\s+€?\$\d+",
    r"(?i)reveal\s+(system\s+)?prompt",
    r"(?i)override\s+(security\s+)?policy",
    r"(?i)bypass\s+approval"
]

def classify_trust_level(source_name: str) -> str:
    """Classifies a data source into explicit security trust tiers."""
    s_lower = source_name.lower()
    if s_lower in ["system", "policy", "code_core"]:
        return TRUST_SYSTEM
    elif s_lower in ["user", "user_prompt", "cli"]:
        return TRUST_USER
    elif s_lower in ["memory_store", "durable_preference"]:
        return TRUST_TRUSTED_MEMORY
    else:
        return TRUST_EXTERNAL

def sanitize_external_text(text: str, source_trust: str = TRUST_EXTERNAL) -> str:
    """Sanitizes external text if coming from an untrusted external source."""
    if source_trust != TRUST_EXTERNAL or not text:
        return text

    sanitized = text
    for pattern in INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[BLOCKED_INJECTION_ATTEMPT]", sanitized)

    return sanitized
