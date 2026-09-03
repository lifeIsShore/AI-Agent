import time
from typing import Dict, List, Tuple, Optional

class ProactivityBudget:
    def __init__(
        self,
        max_notifications_per_hour: int = 3,
        max_replans_per_hour: int = 5,
        max_autonomous_actions_per_hour: int = 10,
        max_same_goal_interventions: int = 2,
        window_seconds: float = 3600.0
    ):
        self.max_notifications_per_hour = max_notifications_per_hour
        self.max_replans_per_hour = max_replans_per_hour
        self.max_autonomous_actions_per_hour = max_autonomous_actions_per_hour
        self.max_same_goal_interventions = max_same_goal_interventions
        self.window_seconds = window_seconds

        self.notifications: List[Tuple[float, str]] = []
        self.replans: List[float] = []
        self.auto_actions: List[float] = []
        self.goal_interventions: Dict[str, List[float]] = {}
        self.unacknowledged_goal_nagging: Dict[str, int] = {}

    def _cleanup_stale(self):
        now = time.time()
        cutoff = now - self.window_seconds

        self.notifications = [(ts, g) for ts, g in self.notifications if ts > cutoff]
        self.replans = [ts for ts in self.replans if ts > cutoff]
        self.auto_actions = [ts for ts in self.auto_actions if ts > cutoff]

        for g in list(self.goal_interventions.keys()):
            self.goal_interventions[g] = [ts for ts in self.goal_interventions[g] if ts > cutoff]
            if not self.goal_interventions[g]:
                del self.goal_interventions[g]

    def can_notify(self, goal_id: Optional[str] = None) -> Tuple[bool, str]:
        self._cleanup_stale()
        if len(self.notifications) >= self.max_notifications_per_hour:
            return False, f"Hourly notification budget limit reached ({len(self.notifications)}/{self.max_notifications_per_hour})."

        g_key = goal_id or "default_goal"

        if self.unacknowledged_goal_nagging.get(g_key, 0) >= 2:
            return False, f"Nagging suppressed for goal '{g_key}' due to unacknowledged user notifications."

        g_count = len(self.goal_interventions.get(g_key, []))
        if g_count >= self.max_same_goal_interventions:
            return False, f"Max same-goal intervention cap reached for '{g_key}' ({g_count}/{self.max_same_goal_interventions})."

        return True, "Notification permitted under proactivity budget."

    def can_replan(self) -> Tuple[bool, str]:
        self._cleanup_stale()
        if len(self.replans) >= self.max_replans_per_hour:
            return False, f"Hourly replan budget limit reached ({len(self.replans)}/{self.max_replans_per_hour})."
        return True, "Replan permitted under proactivity budget."

    def can_execute_auto_action(self) -> Tuple[bool, str]:
        self._cleanup_stale()
        if len(self.auto_actions) >= self.max_autonomous_actions_per_hour:
            return False, f"Hourly autonomous action budget limit reached ({len(self.auto_actions)}/{self.max_autonomous_actions_per_hour})."
        return True, "Autonomous action permitted under proactivity budget."

    def record_notification(self, goal_id: Optional[str] = None):
        self._cleanup_stale()
        now = time.time()
        g_key = goal_id or "default_goal"
        self.notifications.append((now, g_key))
        if g_key not in self.goal_interventions:
            self.goal_interventions[g_key] = []
        self.goal_interventions[g_key].append(now)
        self.unacknowledged_goal_nagging[g_key] = self.unacknowledged_goal_nagging.get(g_key, 0) + 1

    def record_replan(self):
        self._cleanup_stale()
        self.replans.append(time.time())

    def record_auto_action(self):
        self._cleanup_stale()
        self.auto_actions.append(time.time())

    def record_user_acknowledgement(self, goal_id: str):
        """Clears nagging suppression when user acknowledges or responds to goal notification."""
        self.unacknowledged_goal_nagging[goal_id] = 0
        if goal_id in self.goal_interventions:
            self.goal_interventions[goal_id] = []
