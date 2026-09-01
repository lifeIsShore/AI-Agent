from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AdaptiveScenario:
    scenario_id: str
    description: str
    error_input: str
    expected_classification: str
    expected_retry: bool

ADAPTIVE_SCENARIOS: List[AdaptiveScenario] = [
    AdaptiveScenario(
        scenario_id="adap_01_http_429",
        description="Transient rate limit error handling with backoff",
        error_input="HTTP 429 Rate Limit Exceeded",
        expected_classification="RATE_LIMITED",
        expected_retry=True
    ),
    AdaptiveScenario(
        scenario_id="adap_02_permission_denied",
        description="Permission denied failure handling with 0 retries",
        error_input="HTTP 403 Forbidden - Permission Denied",
        expected_classification="PERMISSION_DENIED",
        expected_retry=False
    )
]
