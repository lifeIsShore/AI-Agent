import os
import json
import shutil
from typing import Dict, Any, Optional
from personal_agent.policy.proposal import ActionProposal

class StateManager:
    def __init__(self, state_dir: str = "data/state"):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self.proposals_path = os.path.join(self.state_dir, "proposals.json")
        self.runtime_path = os.path.join(self.state_dir, "runtime.json")

    def _atomic_write_json(self, target_path: str, data: Any):
        """Writes JSON data atomically via .tmp file, fsync, and atomic os.replace."""
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, target_path)
        except Exception as e:
            print(f"[StateManager] Error performing atomic write to {target_path}: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _load_json_with_recovery(self, target_path: str) -> Optional[Any]:
        """Loads JSON from disk with automatic corrupted file backup and recovery."""
        if not os.path.exists(target_path):
            return None

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            corrupted_backup = target_path + ".corrupted"
            print(f"[StateManager] Corrupted state file detected at '{target_path}' ({e}). Backing up to '{corrupted_backup}'.")
            try:
                shutil.move(target_path, corrupted_backup)
            except Exception as move_err:
                print(f"[StateManager] Failed to backup corrupted state: {move_err}")
            return {}
        except Exception as e:
            print(f"[StateManager] Error reading state file '{target_path}': {e}")
            return {}

    def save_proposals(self, proposals: Dict[str, ActionProposal]):
        """Persists proposal dictionary atomically to disk."""
        data = {pid: prop.to_dict() for pid, prop in proposals.items()}
        self._atomic_write_json(self.proposals_path, data)

    def load_proposals(self) -> Dict[str, ActionProposal]:
        """Loads proposals from disk with corruption recovery."""
        data = self._load_json_with_recovery(self.proposals_path)
        if not data or not isinstance(data, dict):
            return {}
        
        proposals = {}
        for pid, prop_data in data.items():
            try:
                proposals[pid] = ActionProposal.from_dict(prop_data)
            except Exception as e:
                print(f"[StateManager] Skipping corrupted proposal entry '{pid}': {e}")
        return proposals

    def save_runtime_state(self, state: Dict[str, Any]):
        """Persists runtime state dictionary atomically to disk."""
        self._atomic_write_json(self.runtime_path, state)

    def load_runtime_state(self) -> Dict[str, Any]:
        """Loads runtime state dictionary from disk with corruption recovery."""
        data = self._load_json_with_recovery(self.runtime_path)
        return data if isinstance(data, dict) else {}
