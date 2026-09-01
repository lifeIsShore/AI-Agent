from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ModelProfile:
    name: str
    tier: str                          # rules | local-small | local-medium | remote-large
    provider: str                      # deterministic | ollama | openai | anthropic
    is_local: bool
    context_window: int
    estimated_latency_ms: float
    cost_per_1k_tokens: float
    reasoning_score: float
    tool_use_support: bool = True

class ModelRegistry:
    def __init__(self):
        self.profiles: Dict[str, ModelProfile] = {
            "rules": ModelProfile(
                name="deterministic_rules",
                tier="rules",
                provider="deterministic",
                is_local=True,
                context_window=100000,
                estimated_latency_ms=0.1,
                cost_per_1k_tokens=0.0,
                reasoning_score=1.0,
                tool_use_support=True
            ),
            "local-small": ModelProfile(
                name="qwen2.5:1.5b",
                tier="local-small",
                provider="ollama",
                is_local=True,
                context_window=32768,
                estimated_latency_ms=150.0,
                cost_per_1k_tokens=0.0,
                reasoning_score=0.65,
                tool_use_support=True
            ),
            "local-medium": ModelProfile(
                name="qwen2.5:7b",
                tier="local-medium",
                provider="ollama",
                is_local=True,
                context_window=131072,
                estimated_latency_ms=450.0,
                cost_per_1k_tokens=0.0,
                reasoning_score=0.82,
                tool_use_support=True
            ),
            "remote-large": ModelProfile(
                name="gpt-4o",
                tier="remote-large",
                provider="openai",
                is_local=False,
                context_window=128000,
                estimated_latency_ms=950.0,
                cost_per_1k_tokens=0.005,
                reasoning_score=0.96,
                tool_use_support=True
            )
        }

    def get_profile(self, tier: str) -> Optional[ModelProfile]:
        return self.profiles.get(tier)
