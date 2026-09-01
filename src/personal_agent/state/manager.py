import os
import json
from typing import Dict, Any, Optional
from personal_agent.policy.proposal import ActionProposal

class StateManager:
    def __init__(self, state_dir: str = "data/state"):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self.proposals_path = os.path.join(self.state_dir, "proposals.json")
        self.runtime_path = os.path.join(self.state_dir, "runtime.json")

    def save_proposals(self, proposals: Dict[str, ActionProposal]):
        """Persists proposal dictionary to disk."""
        data = {pid: prop.to_dict() for pid, prop in proposals.items()}
        try:
            with open(self.proposals_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[StateManager] Error saving proposals: {e}")

    def load_proposals(self) -> Dict[str, ActionProposal]:
        """Loads proposals from disk."""
        if not os.path.exists(self.proposals_path):
            return {}

        try:
            with open(self.proposals_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {pid: ActionProposal.from_dict(prop_data) for pid, prop_data in data.items()}
        except Exception as e:
            print(f"[StateManager] Error loading proposals: {e}")
            return {}

    def save_runtime_state(self, state: Dict[str, Any]):
        """Persists runtime state dictionary to disk."""
        try:
            with open(self.runtime_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[StateManager] Error saving runtime state: {e}")

    def load_runtime_state(self) -> Dict[str, Any]:
        """Loads runtime state dictionary from disk."""
        if not os.path.exists(self.runtime_path):
            return {}

        try:
            with open(self.runtime_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[StateManager] Error loading runtime state: {e}")
            return {}
