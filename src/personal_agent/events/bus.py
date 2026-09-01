from typing import Dict, List, Callable, Optional
from personal_agent.events.event import AgentEvent
from personal_agent.events.store import EventStore

class EventBus:
    def __init__(self, event_store: Optional[EventStore] = None):
        self.event_store = event_store or EventStore()
        self.subscribers: Dict[str, List[Callable[[AgentEvent], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[AgentEvent], None]):
        """Registers a subscriber callback for a specific event type (or '*' for all events)."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: AgentEvent):
        """Persists event to EventStore and dispatches to registered subscribers."""
        self.event_store.append_event(event)

        # Dispatch to specific handlers
        handlers = self.subscribers.get(event.event_type, []) + self.subscribers.get("*", [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EventBus] Subscriber error handling '{event.event_type}': {e}")

        event.processed = True
        self.event_store.mark_processed(event.event_id)

    def replay_unprocessed(self):
        """Replays all unprocessed events stored in EventStore upon daemon boot."""
        unprocessed = self.event_store.get_unprocessed_events()
        if unprocessed:
            print(f"[EventBus] Replaying {len(unprocessed)} unprocessed events from EventStore...")
            for event in unprocessed:
                self.publish(event)
