import os
import json
import time
import uuid
import tempfile
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

class AgentLifecycleState(str, Enum):
    STARTING = "STARTING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    SHUTTING_DOWN = "SHUTTING_DOWN"

@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str
    state: str
    active_goal_id: Optional[str] = None
    active_workflows: List[str] = field(default_factory=list)
    last_event_id: Optional[str] = None
    sequence: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeCheckpoint":
        return cls(
            checkpoint_id=data.get("checkpoint_id", f"chk_{uuid.uuid4().hex[:8]}"),
            state=data.get("state", AgentLifecycleState.STARTING.value),
            active_goal_id=data.get("active_goal_id"),
            active_workflows=data.get("active_workflows", []),
            last_event_id=data.get("last_event_id"),
            sequence=data.get("sequence", 0),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {})
        )

class LifecycleManager:
    def __init__(self, storage_dir: str = "data/runtime", filename: str = "checkpoint.json"):
        self.storage_dir = os.path.abspath(storage_dir)
        self.filepath = os.path.join(self.storage_dir, filename)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._sequence = 0

    def save_checkpoint(
        self,
        state: str,
        active_goal_id: Optional[str] = None,
        active_workflows: Optional[List[str]] = None,
        last_event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RuntimeCheckpoint:
        self._sequence += 1
        chk = RuntimeCheckpoint(
            checkpoint_id=f"chk_{uuid.uuid4().hex[:8]}",
            state=state,
            active_goal_id=active_goal_id,
            active_workflows=active_workflows or [],
            last_event_id=last_event_id,
            sequence=self._sequence,
            timestamp=time.time(),
            metadata=metadata or {}
        )

        # Atomic write to disk using temp file + os.replace
        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="chk_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(chk.to_dict(), f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Failed to atomically write state checkpoint: {e}")

        return chk

    def load_checkpoint(self) -> RuntimeCheckpoint:
        """Loads runtime checkpoint from disk. Falls back safely if missing or corrupted."""
        if not os.path.exists(self.filepath):
            return RuntimeCheckpoint(
                checkpoint_id=f"chk_default_{uuid.uuid4().hex[:6]}",
                state=AgentLifecycleState.STARTING.value,
                metadata={"reason": "no_checkpoint_file"}
            )

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chk = RuntimeCheckpoint.from_dict(data)
            self._sequence = chk.sequence
            return chk
        except Exception as e:
            print(f"[LifecycleManager WARNING] Corrupted or unreadable checkpoint at '{self.filepath}': {e}. Falling back to safe default STARTING state.")
            return RuntimeCheckpoint(
                checkpoint_id=f"chk_fallback_{uuid.uuid4().hex[:6]}",
                state=AgentLifecycleState.STARTING.value,
                metadata={"reason": "corrupted_checkpoint_fallback", "error": str(e)}
            )

    def clear_checkpoint(self) -> None:
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
            except OSError:
                pass
