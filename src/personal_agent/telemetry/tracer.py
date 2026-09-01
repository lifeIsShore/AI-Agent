import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from personal_agent.telemetry.trace import TraceContext
from personal_agent.telemetry.store import TelemetryStore

# Flight Recorder Standard Sequence Steps
STEP_REQUEST_RECEIVED = "REQUEST_RECEIVED"
STEP_INTENT_DETECTED = "INTENT_DETECTED"
STEP_CONTEXT_BUILT = "CONTEXT_BUILT"
STEP_MEMORY_RETRIEVED = "MEMORY_RETRIEVED"
STEP_LLM_CALL = "LLM_CALL"
STEP_DECISION_GENERATED = "DECISION_GENERATED"
STEP_PROPOSAL_CREATED = "PROPOSAL_CREATED"
STEP_POLICY_CHECK = "POLICY_CHECK"
STEP_APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
STEP_APPROVAL_RECEIVED = "APPROVAL_RECEIVED"
STEP_TOOL_EXECUTION_STARTED = "TOOL_EXECUTION_STARTED"
STEP_TOOL_EXECUTION_SUCCESS = "TOOL_EXECUTION_SUCCESS"
STEP_TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
STEP_MEMORY_UPDATED = "MEMORY_UPDATED"
STEP_TRACE_COMPLETED = "TRACE_COMPLETED"

class AgentTracer:
    def __init__(self, store: Optional[TelemetryStore] = None):
        self.store = store or TelemetryStore()

    def record_flight_step(
        self,
        trace_ctx: TraceContext,
        sequence_index: int,
        step_type: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Logs a Flight Recorder sequence step for step-by-step decision chain reconstruction."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "FLIGHT_RECORDER_STEP",
            "seq": sequence_index,
            "step": step_type,
            "trace_id": trace_ctx.trace_id,
            "request_id": trace_ctx.request_id,
            "proposal_id": trace_ctx.proposal_id,
            "execution_id": trace_ctx.execution_id,
            "details": details or {}
        }
        self.store.log_trace(record)

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
