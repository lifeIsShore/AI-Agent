import os
import json
from typing import List, Dict, Any

class TelemetryStore:
    def __init__(self, telemetry_dir: str = "data/telemetry", log_filename: str = "traces.jsonl"):
        self.telemetry_dir = telemetry_dir
        os.makedirs(self.telemetry_dir, exist_ok=True)
        self.traces_file = os.path.join(self.telemetry_dir, log_filename)

    def log_trace(self, trace_data: Dict[str, Any]):
        """Appends a trace record dictionary to the JSONL log file."""
        try:
            with open(self.traces_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[TelemetryStore] Error logging trace: {e}")

    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns recent traces logged to disk."""
        if not os.path.exists(self.traces_file):
            return []

        traces = []
        try:
            with open(self.traces_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                for line in lines[-limit:]:
                    traces.append(json.loads(line))
        except Exception as e:
            print(f"[TelemetryStore] Error reading traces: {e}")

        return traces
