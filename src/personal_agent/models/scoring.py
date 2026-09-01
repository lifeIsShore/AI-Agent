from typing import Dict, Any, Optional

INTENT_GET_TIME = "GET_TIME"
INTENT_SIMPLE_QUERY = "SIMPLE_QUERY"
INTENT_REVIEW_INBOX = "REVIEW_INBOX"
INTENT_PLAN_DAY = "PLAN_DAY"
INTENT_COMPLEX_REASONING = "COMPLEX_REASONING"

INTENT_BASE_COMPLEXITY: Dict[str, float] = {
    INTENT_GET_TIME: 0.0,
    INTENT_SIMPLE_QUERY: 0.20,
    INTENT_REVIEW_INBOX: 0.35,
    INTENT_PLAN_DAY: 0.70,
    INTENT_COMPLEX_REASONING: 0.90
}

class ComplexityScorer:
    def calculate_complexity(
        self,
        intent: str,
        context_bytes: int = 0,
        risk_level: str = "LOW",
        tool_count: int = 1
    ) -> float:
        """Calculates multi-factor task complexity score between 0.0 and 1.0."""
        base_score = INTENT_BASE_COMPLEXITY.get(intent, 0.50)

        # Context Payload Size Scaling (+0.05 per 2KB)
        context_boost = min(0.20, (context_bytes / 2000) * 0.05)

        # Risk Level Scaling
        risk_boost = 0.0
        if risk_level == "HIGH":
            risk_boost = 0.10
        elif risk_level == "CRITICAL":
            risk_boost = 0.20

        # Multi-tool coordination boost
        tool_boost = min(0.10, (tool_count - 1) * 0.03)

        total_score = min(1.0, base_score + context_boost + risk_boost + tool_boost)
        return round(total_score, 3)
