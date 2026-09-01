from typing import List, Dict, Any, Optional

class FakeGmail:
    def __init__(self, sample_emails: Optional[List[Dict[str, Any]]] = None, failure_mode: Optional[str] = None):
        self.emails = sample_emails or []
        self.failure_mode = failure_mode
        self.call_count = 0

    def list_recent_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        self.call_count += 1
        if self.failure_mode == "500_error":
            raise RuntimeError("FakeGmail 500 Internal Server Error")
        elif self.failure_mode == "429_rate_limit":
            raise RuntimeError("FakeGmail 429 Rate Limit Exceeded")
        elif self.failure_mode == "timeout":
            raise TimeoutError("FakeGmail Network Connection Timeout")
        return self.emails[:limit]

class FakeCalendar:
    def __init__(self, sample_events: Optional[List[Dict[str, Any]]] = None, failure_mode: Optional[str] = None):
        self.events = sample_events or []
        self.failure_mode = failure_mode
        self.call_count = 0

    def get_today_events(self) -> List[Dict[str, Any]]:
        self.call_count += 1
        if self.failure_mode == "500_error":
            raise RuntimeError("FakeCalendar 500 Internal Server Error")
        elif self.failure_mode == "timeout":
            raise TimeoutError("FakeCalendar Connection Timeout")
        return self.events

    def get_free_slots(self) -> List[Dict[str, Any]]:
        if self.failure_mode == "500_error":
            raise RuntimeError("FakeCalendar 500 Internal Server Error")
        return [
            {"start": "10:00", "end": "12:00", "duration_minutes": 120},
            {"start": "14:00", "end": "17:00", "duration_minutes": 180}
        ]

class FakeLLM:
    def __init__(self, failure_mode: Optional[str] = None):
        self.failure_mode = failure_mode
        self.call_count = 0

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        self.call_count += 1
        if self.failure_mode == "malformed_json":
            return {"role": "assistant", "content": "{ invalid json response ..."}
        elif self.failure_mode == "timeout":
            raise TimeoutError("LLM Gateway Request Timeout")
        return {"role": "assistant", "content": "Parsed structured response"}
