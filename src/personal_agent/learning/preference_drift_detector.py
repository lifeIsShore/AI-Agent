from typing import Dict, Any, List

DRIFT_GENUINE_USER_SHIFT = "GENUINE_USER_SHIFT"
DRIFT_AGENT_MISLEARNING = "AGENT_MISLEARNING"
DRIFT_TRANSIENT_BEHAVIOR = "TRANSIENT_BEHAVIOR"

class PreferenceDriftDetector:
    def detect_preference_drift(
        self,
        preference_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Distinguishes genuine user preference shifts vs agent mislearning vs transient behavior."""
        if not preference_history:
            return {
                "drift_type": "NONE",
                "classification": "STABLE",
                "explanation": "No preference drift detected."
            }

        # Check last entry source and consistency
        last_entry = preference_history[-1]
        source = last_entry.get("source", "LEARNED")

        if source == "USER":
            return {
                "drift_type": DRIFT_GENUINE_USER_SHIFT,
                "classification": "GENUINE_USER_SHIFT",
                "explanation": "Explicit user feedback confirmed a genuine preference shift."
            }

        # Multiple conflicting learned updates indicate mislearning
        if len(preference_history) >= 3 and all(e.get("source") == "LEARNED" for e in preference_history):
            return {
                "drift_type": DRIFT_AGENT_MISLEARNING,
                "classification": "AGENT_MISLEARNING",
                "explanation": "Repeated inconsistent learned updates indicate agent mislearning."
            }

        return {
            "drift_type": DRIFT_TRANSIENT_BEHAVIOR,
            "classification": "TRANSIENT_BEHAVIOR",
            "explanation": "Occasional variation classified as transient behavior."
        }
