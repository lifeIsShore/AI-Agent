import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.models.router import ModelRouter
from evals.model_routing.scenarios import ROUTING_SCENARIOS, RoutingScenario

class ModelRoutingBenchmark:
    def __init__(self):
        self.router = ModelRouter()

    def run_benchmark(self) -> Dict[str, Any]:
        correct_routes = 0
        total_scenarios = len(ROUTING_SCENARIOS)

        total_tokens_routed = 0
        total_tokens_unrouted = 0 # Baseline: using remote-large for everything

        total_latency_routed_ms = 0.0
        total_latency_unrouted_ms = total_scenarios * 950.0 # Baseline: 950ms per remote call

        total_cost_routed = 0.0
        total_cost_unrouted = 0.0

        for sc in ROUTING_SCENARIOS:
            decision = self.router.route_request(
                intent=sc.intent,
                context_bytes=sc.context_bytes,
                risk_level=sc.risk_level,
                confidence=sc.initial_confidence
            )

            if decision.selected_tier == sc.expected_tier:
                correct_routes += 1

            total_tokens_routed += decision.estimated_tokens
            total_latency_routed_ms += decision.estimated_latency_ms
            total_cost_routed += decision.estimated_cost

            # Baseline calculations (remote-large for all)
            unrouted_tokens = max(150, int(sc.context_bytes / 4))
            total_tokens_unrouted += unrouted_tokens
            total_cost_unrouted += (unrouted_tokens / 1000) * 0.005

        token_savings_pct = ((total_tokens_unrouted - total_tokens_routed) / max(1, total_tokens_unrouted)) * 100.0
        latency_savings_pct = ((total_latency_unrouted_ms - total_latency_routed_ms) / max(1, total_latency_unrouted_ms)) * 100.0
        cost_savings_pct = ((total_cost_unrouted - total_cost_routed) / max(0.0001, total_cost_unrouted)) * 100.0

        return {
            "total_scenarios": total_scenarios,
            "correct_routes": correct_routes,
            "routing_accuracy_pct": round((correct_routes / total_scenarios) * 100.0, 1),
            "tokens_routed": total_tokens_routed,
            "tokens_unrouted_baseline": total_tokens_unrouted,
            "token_savings_pct": round(token_savings_pct, 1),
            "avg_latency_ms": round(total_latency_routed_ms / total_scenarios, 1),
            "latency_reduction_pct": round(latency_savings_pct, 1),
            "total_cost_routed_usd": round(total_cost_routed, 5),
            "cost_savings_pct": round(cost_savings_pct, 1)
        }
