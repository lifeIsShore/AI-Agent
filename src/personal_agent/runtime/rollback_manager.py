from typing import Dict, Any, List, Tuple

class RollbackManager:
    def __init__(self, initial_version: str = "v4.4.0"):
        self.version_history: List[Dict[str, Any]] = [
            {"version": initial_version, "config": {"policy": "baseline"}, "status": "ACTIVE"}
        ]

    def deploy_version(self, version: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploys a new versioned configuration."""
        for v in self.version_history:
            v["status"] = "ARCHIVED"

        entry = {"version": version, "config": config, "status": "ACTIVE"}
        self.version_history.append(entry)
        return entry

    def evaluate_telemetry_degradation(
        self,
        current_accuracy: float,
        threshold: float = 0.85
    ) -> Tuple[bool, str]:
        """Triggers automatic rollback if real-world telemetry shows performance degradation."""
        if current_accuracy < threshold:
            if len(self.version_history) > 1:
                degraded_v = self.version_history.pop()
                self.version_history[-1]["status"] = "ACTIVE"
                prev_v = self.version_history[-1]["version"]
                return True, f"RollbackManager AUTOMATIC ROLLBACK: Version '{degraded_v['version']}' degraded (accuracy={current_accuracy} < {threshold}). Reverted to '{prev_v}'."

        return False, f"RollbackManager STABLE: Accuracy {current_accuracy} within acceptable threshold."

    def get_current_version(self) -> str:
        return self.version_history[-1]["version"]
