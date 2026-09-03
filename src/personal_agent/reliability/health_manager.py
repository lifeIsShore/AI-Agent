from typing import Dict, Any, Tuple

HEALTH_HEALTHY = "HEALTHY"
HEALTH_DEGRADED = "DEGRADED"
HEALTH_UNAVAILABLE = "UNAVAILABLE"

class SubsystemHealthManager:
    def __init__(self):
        self.subsystems: Dict[str, Dict[str, Any]] = {
            "gmail": {"status": HEALTH_HEALTHY, "details": "Operational"},
            "calendar": {"status": HEALTH_HEALTHY, "details": "Operational"},
            "drive": {"status": HEALTH_HEALTHY, "details": "Operational"},
            "browser": {"status": HEALTH_HEALTHY, "details": "Operational"},
            "memory": {"status": HEALTH_HEALTHY, "details": "Operational"},
            "event_bus": {"status": HEALTH_HEALTHY, "details": "Operational"}
        }

    def update_health(self, subsystem: str, status: str, details: str = ""):
        sub_clean = subsystem.lower()
        if sub_clean in self.subsystems:
            self.subsystems[sub_clean]["status"] = status
            self.subsystems[sub_clean]["details"] = details or f"Subsystem {status}"

    def is_subsystem_available(self, subsystem: str) -> bool:
        sub_clean = subsystem.lower()
        info = self.subsystems.get(sub_clean)
        if not info:
            return True
        return info["status"] != HEALTH_UNAVAILABLE

    def get_overall_health(self) -> Dict[str, Any]:
        statuses = [v["status"] for v in self.subsystems.values()]
        if all(s == HEALTH_HEALTHY for s in statuses):
            overall = HEALTH_HEALTHY
        elif any(s == HEALTH_UNAVAILABLE for s in statuses):
            overall = HEALTH_DEGRADED
        else:
            overall = HEALTH_DEGRADED

        return {
            "overall_status": overall,
            "subsystems": self.subsystems
        }
