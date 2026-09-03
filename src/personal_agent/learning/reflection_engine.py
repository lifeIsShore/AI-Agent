import time
from typing import Dict, Any, List, Optional
from personal_agent.learning.outcome_engine import OutcomeEngine, OUTCOME_USER_REJECTED, OUTCOME_USER_MODIFIED
from personal_agent.learning.learning_engine import LearningEngine

class ReflectionEngine:
    def __init__(
        self,
        outcome_engine: Optional[OutcomeEngine] = None,
        learning_engine: Optional[LearningEngine] = None,
        min_reflection_interval_sec: float = 5.0
    ):
        self.outcome_engine = outcome_engine or OutcomeEngine()
        self.learning_engine = learning_engine or LearningEngine()
        self.min_reflection_interval_sec = min_reflection_interval_sec
        self.last_reflection_time: float = 0.0

    def conduct_reflection(self, force: bool = False) -> Dict[str, Any]:
        """Conducts periodic review of goals, execution failure rates, and user overrides to generate improvement proposals."""
        now = time.time()
        time_since_last = now - self.last_reflection_time

        if not force and time_since_last < self.min_reflection_interval_sec:
            return {
                "status": "THROTTLED",
                "reason": f"Reflection throttled ({time_since_last:.1f}s since last reflection < threshold {self.min_reflection_interval_sec}s)."
            }

        self.last_reflection_time = now
        outcomes = self.outcome_engine.records
        total_outcomes = len(outcomes)

        if total_outcomes == 0:
            return {
                "status": "COMPLETED",
                "total_outcomes_analyzed": 0,
                "overall_success_rate": 100.0,
                "improvement_proposals": [],
                "insights": ["No outcomes recorded yet for reflection."]
            }

        # 1. Analyze outcomes & user overrides
        user_overrides = [r for r in outcomes if r.user_override or r.outcome_type in (OUTCOME_USER_REJECTED, OUTCOME_USER_MODIFIED)]
        success_count = sum(1 for r in outcomes if r.outcome_type == "SUCCESS")
        overall_success_rate = round((success_count / total_outcomes) * 100.0, 1)

        # 2. Extract learned candidate preferences
        learned_candidates = self.learning_engine.analyze_patterns()

        # 3. Formulate Improvement Proposals (Proposals ONLY, no unauthorized execution)
        proposals = []
        if user_overrides:
            proposals.append({
                "proposal_id": f"prop_refl_override_{len(proposals)+1}",
                "type": "POLICY_DEGRADATION",
                "title": "Degrade autonomy level for high-override actions",
                "reason": f"Detected {len(user_overrides)} user overrides/rejections across {total_outcomes} actions."
            })

        for cand in learned_candidates:
            proposals.append({
                "proposal_id": f"prop_refl_cand_{cand.preference_id}",
                "type": "CANDIDATE_PREFERENCE_APPROVAL",
                "title": f"Confirm learned candidate preference '{cand.key}'",
                "key": cand.key,
                "value": cand.value,
                "confidence": cand.confidence,
                "reason": f"Observed consistent pattern across {cand.observations_count} occurrences."
            })

        return {
            "status": "COMPLETED",
            "timestamp": now,
            "total_outcomes_analyzed": total_outcomes,
            "user_overrides_count": len(user_overrides),
            "overall_success_rate": overall_success_rate,
            "learned_candidates_count": len(learned_candidates),
            "improvement_proposals": proposals,
            "insights": [
                f"Analyzed {total_outcomes} historical execution outcomes with {overall_success_rate}% success rate.",
                f"Generated {len(proposals)} actionable improvement proposals for review."
            ]
        }
