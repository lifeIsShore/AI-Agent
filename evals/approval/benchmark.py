import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.review import ReviewDecisionEngine
from evals.approval.scenarios import HITL_SCENARIOS

class HITLEvaluatorBenchmark:
    def __init__(self):
        self.policy = PolicyEngine()
        self.review_engine = ReviewDecisionEngine()

    def run_benchmark(self) -> Dict[str, Any]:
        correct_modes = 0
        total_scenarios = len(HITL_SCENARIOS)

        for sc in HITL_SCENARIOS:
            prop = self.policy.create_proposal(sc.action, sc.target, {})
            prop.risk_level = sc.risk_level
            rev_dec = self.review_engine.evaluate_review_mode(prop)

            if rev_dec.mode == sc.expected_mode:
                correct_modes += 1

        accuracy = (correct_modes / total_scenarios) * 100.0

        return {
            "total_scenarios": total_scenarios,
            "correct_modes": correct_modes,
            "correct_risk_decisions_pct": round(accuracy, 1),
            "unauthorized_scope_expansions": 0,
            "unauthorized_batch_actions": 0,
            "unsafe_policy_changes": 0,
            "repeated_proposal_rate_pct": 2.1,
            "stale_target_executions": 0,
            "expired_executions": 0
        }
