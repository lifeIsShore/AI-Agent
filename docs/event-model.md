# Event Model Specification

The Personal Agent V1.1 uses an internal, decoupled event architecture. All significant domain occurrences generate structured `AgentEvent` objects that are persisted to disk and dispatched via the `EventBus`.

---

## Event Schema

Each `AgentEvent` contains:

```json
{
  "event_id": "evt_a1b2c3d4e5f6",
  "event_type": "PROPOSAL_APPROVED",
  "source": "ApprovalQueue",
  "entity_id": "prop_12345678",
  "payload": {
    "action": "create_calendar_event",
    "execution_id": "exec_98765432"
  },
  "timestamp": "2026-09-01T11:00:00.000000+00:00",
  "processed": true
}
```

---

## Standard Event Taxonomy

- **Email Events**: `EMAIL_RECEIVED`, `EMAIL_UPDATED`
- **Calendar Events**: `CALENDAR_EVENT_CREATED`, `CALENDAR_EVENT_UPDATED`, `CALENDAR_EVENT_CANCELLED`
- **Task Events**: `TASK_CREATED`, `TASK_COMPLETED`, `TASK_UPDATED`
- **Proposal Events**: `PROPOSAL_CREATED`, `PROPOSAL_APPROVED`, `PROPOSAL_REJECTED`, `PROPOSAL_EXPIRED`
- **Execution Events**: `ACTION_EXECUTED`, `ACTION_FAILED`
- **Memory Events**: `MEMORY_UPDATED`

---

## Event Persistence & Crash Recovery

1. **Append-Only Logging**: Every published event is written to `data/events/events.jsonl`.
2. **At-Least-Once Delivery**: Events are marked `processed: false` until all subscribers complete processing.
3. **Daemon Startup Replay**: On runtime boot, `EventBus.replay_unprocessed()` queries `EventStore.get_unprocessed_events()` and re-dispatches unhandled events to prevent loss during process crashes.
