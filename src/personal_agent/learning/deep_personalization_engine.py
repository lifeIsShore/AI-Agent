import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class ContextualPreferenceRule:
    rule_id: str
    conditions: Dict[str, Any]
    action_recommendation: str
    source: str = "LEARNED"  # USER vs LEARNED
    confidence: float = 0.85

    def matches_context(self, context_facts: Dict[str, Any]) -> bool:
        for k, v in self.conditions.items():
            fact_val = context_facts.get(k)
            if fact_val is None:
                return False
            if isinstance(v, str) and isinstance(fact_val, str):
                if v.lower() not in fact_val.lower():
                    return False
            elif fact_val != v:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DeepPersonalizationEngine:
    def __init__(self):
        self.rules: List[ContextualPreferenceRule] = [
            ContextualPreferenceRule(
                rule_id="r_univ_prof",
                conditions={"task": "university_email", "sender": "prof"},
                action_recommendation="recommend_afternoon_response",
                source="USER",
                confidence=1.0
            ),
            ContextualPreferenceRule(
                rule_id="r_job_urgent",
                conditions={"task": "job_application", "urgent": True},
                action_recommendation="increase_priority_high",
                source="USER",
                confidence=1.0
            )
        ]

    def add_rule(self, rule: ContextualPreferenceRule):
        self.rules.append(rule)

    def evaluate_contextual_recommendation(
        self,
        context_facts: Dict[str, Any]
    ) -> Optional[ContextualPreferenceRule]:
        """Evaluates multi-condition rule tree ranking USER source above LEARNED source."""
        matching_rules = [r for r in self.rules if r.matches_context(context_facts)]

        if not matching_rules:
            return None

        # Sort by USER source first (rank 100%), then by confidence score
        user_rules = [r for r in matching_rules if r.source == "USER"]
        if user_rules:
            user_rules.sort(key=lambda r: r.confidence, reverse=True)
            return user_rules[0]

        matching_rules.sort(key=lambda r: r.confidence, reverse=True)
        return matching_rules[0]
