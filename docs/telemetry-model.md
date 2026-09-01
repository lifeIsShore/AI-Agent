# Telemetry & Observability Model Specification

The Telemetry Engine provides full execution observability across LLM calls, context selection, policy decisions, and tool executions.

---

## Correlation Identity (`TraceContext`)

Every agent request initializes or inherits a `TraceContext`:

```json
{
  "trace_id": "trace_f1e2d3c4b5a6",
  "request_id": "req_001",
  "event_id": "evt_999",
  "proposal_id": "prop_12345678",
  "execution_id": "exec_98765432",
  "start_time": "2026-09-01T11:00:00.000000+00:00"
}
```

- **`trace_id`**: Connects all operations across a single user prompt or scheduled run.
- **`proposal_id`**: Identifies the policy action proposal generated during the workflow.
- **`execution_id`**: Identifies the specific tool execution attempt.

---

## Metric Telemetry Logs (`data/telemetry/traces.jsonl`)

### 1. LLM Call Metrics
Tracks LLM invocation overhead and token counts:
```json
{
  "timestamp": "2026-09-01T11:00:05.123456+00:00",
  "type": "LLM_CALL",
  "trace_id": "trace_f1e2d3c4b5a6",
  "model": "ollama",
  "intent": "CHAT",
  "prompt_tokens": 125,
  "completion_tokens": 42,
  "total_tokens": 167,
  "latency_sec": 1.245,
  "status": "SUCCESS"
}
```

### 2. Context Budget Efficiency
Measures intent-dependent context packaging efficiency:
```json
{
  "timestamp": "2026-09-01T11:00:04.000000+00:00",
  "type": "CONTEXT_EFFICIENCY",
  "trace_id": "trace_f1e2d3c4b5a6",
  "intent": "PLAN_DAY",
  "item_counts": {"emails": 3, "calendar": 5, "tasks": 2},
  "total_bytes": 1420,
  "latency_sec": 0.015
}
```
