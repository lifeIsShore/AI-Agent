import os
import json
from typing import List, Optional
from personal_agent.events.event import AgentEvent

class EventStore:
    def __init__(self, events_dir: str = "data/events", log_filename: str = "events.jsonl"):
        self.events_dir = events_dir
        os.makedirs(self.events_dir, exist_ok=True)
        self.events_file = os.path.join(self.events_dir, log_filename)

    def append_event(self, event: AgentEvent):
        """Appends an AgentEvent to the JSONL log file if not already present."""
        existing = self.load_all_events()
        if any(e.event_id == event.event_id for e in existing):
            return

        try:
            with open(self.events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[EventStore] Error appending event: {e}")

    def load_all_events(self) -> List[AgentEvent]:
        """Loads all events from disk."""
        if not os.path.exists(self.events_file):
            return []

        events = []
        try:
            with open(self.events_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(AgentEvent.from_dict(json.loads(line)))
        except Exception as e:
            print(f"[EventStore] Error loading events: {e}")

        return events

    def get_unprocessed_events(self) -> List[AgentEvent]:
        """Returns all events currently marked processed == False."""
        all_events = self.load_all_events()
        return [e for e in all_events if not e.processed]

    def mark_processed(self, event_id: str):
        """Marks an event as processed in the log file."""
        all_events = self.load_all_events()
        updated = False

        for e in all_events:
            if e.event_id == event_id:
                e.processed = True
                updated = True
                break

        if updated:
            try:
                with open(self.events_file, "w", encoding="utf-8") as f:
                    for e in all_events:
                        f.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"[EventStore] Error marking event processed: {e}")
