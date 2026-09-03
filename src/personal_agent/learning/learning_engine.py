from typing import Dict, Any, List, Optional
from personal_agent.learning.outcome_engine import (
    OutcomeEngine, OUTCOME_SUCCESS, OUTCOME_FAILED, OUTCOME_USER_MODIFIED, OUTCOME_USER_REJECTED, OUTCOME_USER_ACCEPTED
)
from personal_agent.learning.preference_candidate import (
    PreferenceRegistry, PreferenceCandidate, SOURCE_USER, SOURCE_LEARNED
)

class LearningEngine:
    def __init__(
        self,
        outcome_engine: Optional[OutcomeEngine] = None,
        registry: Optional[PreferenceRegistry] = None
    ):
        self.outcome_engine = outcome_engine or OutcomeEngine()
        self.registry = registry or PreferenceRegistry()

    def analyze_patterns(self) -> List[PreferenceCandidate]:
        """Analyzes ActionOutcome logs for recurring behavioral patterns."""
        outcomes = self.outcome_engine.records
        if not outcomes:
            return []

        # 1. Analyze User Schedule Modifications (e.g. 08:00 -> 15:00 shifts)
        mod_outcomes = [r for r in outcomes if r.outcome_type == OUTCOME_USER_MODIFIED]
        time_shift_counts: Dict[str, int] = {}
        for r in mod_outcomes:
            new_time = r.details.get("new_time", r.details.get("preferred_time", "afternoon"))
            key = f"preferred_work_time_{r.action_type}"
            time_shift_counts[f"{key}:{new_time}"] = time_shift_counts.get(f"{key}:{new_time}", 0) + 1

        new_candidates = []
        for key_val, count in time_shift_counts.items():
            key, val = key_val.split(":", 1)
            # Pattern Invariant: Requires >= 3 consistent observations to form a learned preference
            if count >= 3:
                conf = min(0.95, round(0.60 + (count * 0.08), 2))
                pref = self.registry.register_preference(
                    key=key,
                    value=val,
                    source=SOURCE_LEARNED,
                    confidence=conf,
                    observations_count=count,
                    evidence=f"Observed user shifting schedule to {val} {count} times."
                )
                new_candidates.append(pref)

        # 2. Analyze User Rejections of Proposals
        rejections = [r for r in outcomes if r.outcome_type == OUTCOME_USER_REJECTED]
        rejection_counts: Dict[str, int] = {}
        for r in rejections:
            key = f"proposal_acceptance_{r.action_type}"
            rejection_counts[key] = rejection_counts.get(key, 0) + 1

        for key, count in rejection_counts.items():
            existing = self.registry.get_preference(key)
            if existing and existing.source == SOURCE_LEARNED:
                existing.add_contradictory_observation(f"User rejected proposal {count} times.")

        self.registry.save_preferences()
        return new_candidates

    def explain_preference(self, key: str) -> Dict[str, Any]:
        """Answers 'Why' queries with transparent evidence, observation counts, and confidence metrics."""
        pref = self.registry.get_preference(key)
        if not pref:
            return {
                "key": key,
                "found": False,
                "explanation": f"No preference or hypothesis registered for '{key}'."
            }

        if pref.source == SOURCE_USER:
            explanation = f"You explicitly set this preference ('{pref.value}'). Explicit user preferences are 100% authoritative."
        else:
            explanation = (
                f"You haven't explicitly set this preference, but based on {pref.observations_count} previous observations "
                f"where your actions indicated '{pref.value}', this was derived as a learned preference with {int(pref.confidence * 100)}% confidence."
            )

        return {
            "key": key,
            "found": True,
            "value": pref.value,
            "source": pref.source,
            "confidence": pref.confidence,
            "confidence_pct": f"{int(pref.confidence * 100)}%",
            "observations_count": pref.observations_count,
            "status": pref.status,
            "evidence_log": pref.evidence_log,
            "explanation": explanation
        }
