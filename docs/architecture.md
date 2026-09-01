# Personal Agent System Architecture

The Personal Agent is a policy-controlled, locally deployed agent runtime featuring structured memory, intent-dependent context management, human-in-the-loop approval, persistent state recovery, event-driven decoupled routing, and execution telemetry.

```text
                               USER / DAEMON TRIGGER
                                         │
                                         ▼
                               ┌──────────────────┐
                               │ Context Manager  │
                               └────────┬─────────┘
                                        │
                                        ▼
                                  Agent Runtime
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
       Planner Engine             Triage Engine              Memory Loop
             │                          │                          │
             └──────────────────────────┼──────────────────────────┘
                                        ▼
                                  ActionProposal
                                        │
                                        ▼
                                  Policy Engine
                                        │
                   ┌────────────────────┴────────────────────┐
                   ▼                                         ▼
                DENIED                               PENDING_APPROVAL
                                                             │
                                                             ▼
                                                       Approval Queue
                                                             │
                                                             ▼
                                                       Tool Execution
                                                             │
                                                             ▼
                                                         Event Bus
                                                             │
                    ┌────────────────────────────────────────┼────────────────────────────────────────┐
                    ▼                                        ▼                                        ▼
               Audit Logger                             Event Store                             Telemetry Store
           (data/logs/audit.jsonl)               (data/events/events.jsonl)               (data/telemetry/traces.jsonl)
```

---

## Architectural Layers

| Layer | Responsibility | Primary Module |
| :--- | :--- | :--- |
| **Context Manager** | Filters and packages minimal required emails, calendar events, and memories based on intent. | `src/personal_agent/context/manager.py` |
| **Agent Runtime** | Manages LLM tool requests, idempotency caching, and execution dispatching. | `src/personal_agent/agent/runtime.py` |
| **Planner Engine** | Generates daily execution schedules and allocates priority tasks into calendar slots. | `src/personal_agent/planner/daily_planner.py` |
| **Policy Engine** | Security boundary evaluating `ActionProposal` risk levels, permissions, and human approval rules. | `src/personal_agent/policy/engine.py` |
| **Approval Queue** | Manages `PENDING_APPROVAL` queue, safe batch operations, explainability chains, and disk recovery. | `src/personal_agent/policy/approval.py` |
| **State Manager** | Persists proposal queues (`proposals.json`) and scheduler states (`runtime.json`). | `src/personal_agent/state/manager.py` |
| **Agent Scheduler** | Manages daemon job ticks, intervals, and task execution history. | `src/personal_agent/scheduler/scheduler.py` |
| **Event Bus & Store** | Decoupled pub/sub event router and persistent append-only event log (`events.jsonl`). | `src/personal_agent/events/bus.py` |
| **Audit Logger** | Security compliance append-only log of every proposal decision and tool output (`audit.jsonl`). | `src/personal_agent/security/audit.py` |
| **Telemetry Store** | Captures `TraceContext` execution spans, LLM token counts, and context efficiency (`traces.jsonl`). | `src/personal_agent/telemetry/tracer.py` |
