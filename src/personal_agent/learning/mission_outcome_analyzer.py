from typing import Dict, Any

class MissionOutcomeAnalyzer:
    def analyze_mission_outcome(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates mission completion metrics, duration, token cost, and success rate."""
        steps = mission_data.get("steps", [])
        total_steps = len(steps)
        failed_steps = sum(1 for s in steps if s.get("status") == "FAILED")
        rejections = mission_data.get("rejections", 0)

        success = (failed_steps == 0) and (rejections == 0)
        success_rate = 1.0 if success else max(0.0, 1.0 - (rejections * 0.2 + failed_steps * 0.3))

        return {
            "mission_id": mission_data.get("mission_id", "m_unknown"),
            "domain": mission_data.get("domain", "general"),
            "strategy_id": mission_data.get("strategy_id", "strat_default"),
            "success": success,
            "success_rate": round(success_rate, 3),
            "total_steps": total_steps,
            "failed_steps": failed_steps,
            "rejections": rejections,
            "duration_sec": mission_data.get("duration_sec", 0.0),
            "tokens_used": mission_data.get("tokens_used", 0)
        }
