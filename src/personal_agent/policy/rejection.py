from typing import Dict, Tuple

class RepeatedRejectionTracker:
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.rejection_counts: Dict[str, int] = {}

    def _get_key(self, action: str, category: str) -> str:
        return f"{action}:{category}"

    def record_rejection(self, action: str, category: str = "general"):
        """Increments consecutive rejection counter for an action+category pair."""
        key = self._get_key(action, category)
        self.rejection_counts[key] = self.rejection_counts.get(key, 0) + 1

    def record_approval(self, action: str, category: str = "general"):
        """Resets consecutive rejection counter upon user approval."""
        key = self._get_key(action, category)
        self.rejection_counts[key] = 0

    def should_throttle_proposal(self, action: str, category: str = "general") -> Tuple[bool, str]:
        """Returns True if an action+category pair has reached the repeated rejection threshold."""
        key = self._get_key(action, category)
        count = self.rejection_counts.get(key, 0)
        if count >= self.threshold:
            return True, f"Throttled: Action '{action}' on category '{category}' was rejected {count} consecutive times by user."
        return False, "Not throttled"
