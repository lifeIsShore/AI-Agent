import os
import json
import time
import uuid
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

SOURCE_USER = "USER"
SOURCE_LEARNED = "LEARNED"

STATUS_CANDIDATE = "CANDIDATE"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_EXPIRED = "EXPIRED"

@dataclass
class PreferenceCandidate:
    preference_id: str
    key: str
    value: Any
    source: str = SOURCE_LEARNED
    confidence: float = 0.5
    observations_count: int = 1
    status: str = STATUS_CANDIDATE
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    evidence_log: List[str] = field(default_factory=list)

    def decay_confidence(self, decay_rate: float = 0.05) -> float:
        """Decays confidence for unreinforced learned preferences over time."""
        if self.source == SOURCE_USER:
            return self.confidence  # User preferences do not decay
        self.confidence = max(0.0, round(self.confidence - decay_rate, 2))
        if self.confidence < 0.3:
            self.status = STATUS_EXPIRED
        return self.confidence

    def add_observation(self, evidence: str, boost: float = 0.05) -> float:
        self.observations_count += 1
        self.evidence_log.append(f"Observation #{self.observations_count}: {evidence}")
        if self.source == SOURCE_LEARNED:
            self.confidence = min(1.0, round(self.confidence + boost, 2))
            if self.observations_count >= 3 and self.confidence >= 0.7:
                self.status = STATUS_CONFIRMED
        return self.confidence

    def add_contradictory_observation(self, evidence: str, penalty: float = 0.15) -> float:
        self.evidence_log.append(f"Contradictory Evidence: {evidence}")
        if self.source == SOURCE_LEARNED:
            self.confidence = max(0.0, round(self.confidence - penalty, 2))
            if self.confidence < 0.3:
                self.status = STATUS_EXPIRED
        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PreferenceCandidate":
        return cls(
            preference_id=data.get("preference_id", f"pref_{uuid.uuid4().hex[:8]}"),
            key=data.get("key", "unknown"),
            value=data.get("value"),
            source=data.get("source", SOURCE_LEARNED),
            confidence=data.get("confidence", 0.5),
            observations_count=data.get("observations_count", 1),
            status=data.get("status", STATUS_CANDIDATE),
            created_at=data.get("created_at", time.time()),
            expires_at=data.get("expires_at"),
            evidence_log=data.get("evidence_log", [])
        )

class PreferenceRegistry:
    def __init__(self, storage_dir: Optional[str] = None, filename: str = "preferences.json"):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
            self.filepath = os.path.join(self.storage_dir, filename)
            os.makedirs(self.storage_dir, exist_ok=True)
            self.candidates: Dict[str, PreferenceCandidate] = self.load_preferences()
        else:
            self.storage_dir = None
            self.filepath = None
            self.candidates: Dict[str, PreferenceCandidate] = {}

    def register_preference(
        self,
        key: str,
        value: Any,
        source: str = SOURCE_LEARNED,
        confidence: float = 0.5,
        observations_count: int = 1,
        evidence: Optional[str] = None
    ) -> PreferenceCandidate:
        existing = self.get_preference(key)

        # Invariant: Explicit USER preference cannot be overwritten by LEARNED preference
        if existing and existing.source == SOURCE_USER and source == SOURCE_LEARNED:
            print(f"[PreferenceRegistry INVARIANT] Rejected LEARNED update for '{key}' because USER explicit preference exists.")
            return existing

        if existing and existing.key == key and existing.value == value:
            existing.add_observation(evidence or "Reinforcing evidence observed")
            self.save_preferences()
            return existing

        pref = PreferenceCandidate(
            preference_id=f"pref_{uuid.uuid4().hex[:8]}",
            key=key,
            value=value,
            source=source,
            confidence=1.0 if source == SOURCE_USER else confidence,
            observations_count=observations_count,
            status=STATUS_CONFIRMED if source == SOURCE_USER else STATUS_CANDIDATE,
            created_at=time.time(),
            evidence_log=[evidence] if evidence else []
        )
        self.candidates[key] = pref
        self.save_preferences()
        return pref

    def get_effective_preference(self, key: str) -> Optional[PreferenceCandidate]:
        """Returns active effective preference. USER declared outranks LEARNED candidate."""
        pref = self.candidates.get(key)
        if not pref:
            return None
        if pref.status == STATUS_EXPIRED:
            return None
        # Low confidence LEARNED candidate (< 0.70) is ignored for active planning
        if pref.source == SOURCE_LEARNED and pref.confidence < 0.70:
            return None
        return pref

    def get_preference(self, key: str) -> Optional[PreferenceCandidate]:
        return self.candidates.get(key)

    def save_preferences(self) -> None:
        if not self.filepath or not self.storage_dir:
            return
        data = {k: v.to_dict() for k, v in self.candidates.items()}
        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="pref_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[PreferenceRegistry ERROR] Failed to save preferences: {e}")

    def load_preferences(self) -> Dict[str, PreferenceCandidate]:
        if not self.filepath or not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {k: PreferenceCandidate.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"[PreferenceRegistry WARNING] Failed to load preferences from '{self.filepath}': {e}. Falling back to empty registry.")
            return {}
