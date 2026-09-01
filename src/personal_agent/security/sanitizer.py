import re
from typing import Any, Dict, List

CREDENTIAL_PATTERNS = [
    (r"(?i)bearer_[a-z0-9_\-]+", "[REDACTED_BEARER_TOKEN]"),
    (r"(?i)mock_google_[a-z0-9_\-]+", "[REDACTED_GOOGLE_SECRET]"),
    (r"(?i)access_token['\"]?\s*[:=]\s*['\"]?[a-z0-9_\-]+['\"]?", "access_token: '[REDACTED_ACCESS_TOKEN]'"),
    (r"(?i)refresh_token['\"]?\s*[:=]\s*['\"]?[a-z0-9_\-]+['\"]?", "refresh_token: '[REDACTED_REFRESH_TOKEN]'"),
    (r"(?i)api_key['\"]?\s*[:=]\s*['\"]?[a-z0-9_\-]+['\"]?", "api_key: '[REDACTED_API_KEY]'"),
]

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    sanitized = text
    for pattern, replacement in CREDENTIAL_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized

def redact_credentials(data: Any) -> Any:
    """Recursively redacts credentials and secrets from strings, dicts, lists, or exception messages."""
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        sanitized_dict = {}
        for k, v in data.items():
            if k.lower() in ["access_token", "refresh_token", "api_key", "secret", "google_refresh_token", "google_client_id"]:
                sanitized_dict[k] = "[REDACTED_SECRET]"
            else:
                sanitized_dict[k] = redact_credentials(v)
        return sanitized_dict
    elif isinstance(data, list):
        return [redact_credentials(item) for item in data]
    return data
