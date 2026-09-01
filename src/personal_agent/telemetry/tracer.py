import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from personal_agent.telemetry.trace import TraceContext
from personal_agent.telemetry.store import TelemetryStore

class AgentTracer:
    def __init__(self, store: Optional[TelemetryStore] = None):
        self.store = store or TelemetryStore()

    def record_llm_call(
        self,
        trace_ctx: TraceContext,
        model: str,
        intent: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_sec: float,
        status: str = "SUCCESS"
    ):
        """Logs LLM invocation metrics including model, tokens, and latency."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "LLM_CALL",
            "trace_id": trace_ctx.trace_id,
            "proposal_id": trace_ctx.proposal_id,
            "execution_id": trace_ctx.execution_id,
            "model": model,
            "intent": intent,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_sec": round(latency_sec, 3),
            "status": status
        }
        self.store.log_trace(record)

    def record_context_efficiency(
        self,
        trace_ctx: TraceContext,
        intent: str,
        item_counts: Dict[str, int],
        total_bytes: int,
        latency_sec: float
    ):
        """Logs context budget efficiency metrics (item counts, payload size, latency)."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "CONTEXT_EFFICIENCY",
            "trace_id": trace_ctx.trace_id,
            "intent": intent,
            "item_counts": item_counts,
            "total_bytes": total_bytes,
            "latency_sec": round(latency_sec, 3)
        }
        self.store.log_trace(record)

    def record_span(
        self,
        trace_ctx: TraceContext,
        step_name: str,
        payload: Dict[str, Any]
    ):
        """Logs a generic workflow step span with correlation trace_id."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "WORKFLOW_SPAN",
            "step": step_name,
            "trace_id": trace_ctx.trace_id,
            "proposal_id": trace_ctx.proposal_id,
            "execution_id": trace_ctx.execution_id,
            "payload": payload
        }
        self.store.log_trace(record)
