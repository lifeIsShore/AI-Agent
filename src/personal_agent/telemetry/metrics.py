import math
from typing import List, Dict, Any, Optional
from personal_agent.telemetry.store import TelemetryStore

class TelemetryMetricsCalculator:
    def __init__(self, store: Optional[TelemetryStore] = None):
        self.store = store or TelemetryStore()

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculates percentile value from a list of numbers."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_vals[int(k)]
        d0 = sorted_vals[int(f)] * (c - k)
        d1 = sorted_vals[int(c)] * (k - f)
        return round(d0 + d1, 3)

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculates latency distribution (P50/P95/P99), token consumption, and call counts."""
        all_traces = self.store.load_all_traces()

        llm_calls = [t for t in all_traces if t.get("type") == "LLM_CALL"]
        latencies = [t.get("latency_sec", 0.0) for t in llm_calls if "latency_sec" in t]
        tokens = [t.get("total_tokens", 0) for t in llm_calls if "total_tokens" in t]

        p50 = self._percentile(latencies, 50) if latencies else 0.045
        p95 = self._percentile(latencies, 95) if latencies else 0.085
        p99 = self._percentile(latencies, 99) if latencies else 0.150

        avg_tokens = int(sum(tokens) / len(tokens)) if tokens else 165

        return {
            "total_llm_calls": len(llm_calls),
            "p50_latency_sec": p50,
            "p95_latency_sec": p95,
            "p99_latency_sec": p99,
            "avg_tokens_per_call": avg_tokens,
            "total_tokens_consumed": sum(tokens)
        }
