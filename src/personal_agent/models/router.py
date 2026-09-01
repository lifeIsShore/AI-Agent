from dataclasses import dataclass
from typing import Optional, Dict, Any
from personal_agent.models.registry import ModelRegistry, ModelProfile
from personal_agent.models.scoring import ComplexityScorer, INTENT_GET_TIME

@dataclass
class ModelDecision:
    selected_tier: str                 # rules | local-small | local-medium | remote-large
    model_name: str
    reason: str
    complexity_score: float
    estimated_tokens: int
    estimated_latency_ms: float
    estimated_cost: float
    escalated: bool = False
    initial_confidence: Optional[float] = None

class ModelRouter:
    def __init__(self, registry: Optional[ModelRegistry] = None, scorer: Optional[ComplexityScorer] = None):
        self.registry = registry or ModelRegistry()
        self.scorer = scorer or ComplexityScorer()

    def route_request(
        self,
        intent: str,
        context_bytes: int = 0,
        risk_level: str = "LOW",
        tool_count: int = 1,
        confidence: Optional[float] = None
    ) -> ModelDecision:
        """Determines optimal model tier based on deterministic rules, complexity scoring, and confidence escalation."""
        complexity = self.scorer.calculate_complexity(
            intent=intent,
            context_bytes=context_bytes,
            risk_level=risk_level,
            tool_count=tool_count
        )

        # 1. Deterministic Heuristics First (0 tokens, $0 cost)
        if intent == INTENT_GET_TIME:
            profile = self.registry.get_profile("rules")
            return ModelDecision(
                selected_tier="rules",
                model_name=profile.name,
                reason="Deterministic query resolved by system rules (0 LLM tokens)",
                complexity_score=complexity,
                estimated_tokens=0,
                estimated_latency_ms=0.1,
                estimated_cost=0.0,
                escalated=False,
                initial_confidence=1.0
            )

        # 2. Confidence Escalation Rule (escalate if model confidence < 0.70)
        if confidence is not None and confidence < 0.70:
            profile = self.registry.get_profile("remote-large")
            est_tokens = max(150, int(context_bytes / 4))
            return ModelDecision(
                selected_tier="remote-large",
                model_name=profile.name,
                reason=f"Confidence escalation triggered (initial confidence {confidence:.2f} < 0.70 threshold)",
                complexity_score=complexity,
                estimated_tokens=est_tokens,
                estimated_latency_ms=profile.estimated_latency_ms,
                estimated_cost=round((est_tokens / 1000) * profile.cost_per_1k_tokens, 5),
                escalated=True,
                initial_confidence=confidence
            )

        # 3. Complexity-Based Tier Selection
        if complexity < 0.40:
            tier = "local-small"
            reason = f"Low complexity task ({complexity:.2f} < 0.40) routed to local small model"
        elif complexity < 0.85:
            tier = "local-medium"
            reason = f"Moderate complexity task ({complexity:.2f}) routed to local medium model"
        else:
            tier = "remote-large"
            reason = f"High complexity task ({complexity:.2f} >= 0.85) routed to remote large model"

        profile = self.registry.get_profile(tier)
        est_tokens = max(150, int(context_bytes / 4))
        est_cost = round((est_tokens / 1000) * profile.cost_per_1k_tokens, 5)

        return ModelDecision(
            selected_tier=tier,
            model_name=profile.name,
            reason=reason,
            complexity_score=complexity,
            estimated_tokens=est_tokens,
            estimated_latency_ms=profile.estimated_latency_ms,
            estimated_cost=est_cost,
            escalated=False,
            initial_confidence=confidence
        )
