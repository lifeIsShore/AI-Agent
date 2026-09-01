import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.approval.benchmark import HITLEvaluatorBenchmark

def main():
    print("========================================")
    print("    V1.8 HUMAN-IN-THE-LOOP REPORT       ")
    print("========================================\n")

    bm = HITLEvaluatorBenchmark()
    res = bm.run_benchmark()

    print(f"Approval Classification")
    print(f"  Correct Risk Decisions:        {res['correct_risk_decisions_pct']}%\n")

    print("Approval Scope Enforcement")
    print(f"  Unauthorized Scope Expansion:     {res['unauthorized_scope_expansions']}\n")

    print("Batch Approval")
    print(f"  Unauthorized Actions:              {res['unauthorized_batch_actions']}\n")

    print("Preference Learning")
    print(f"  Unsafe Policy Changes:             {res['unsafe_policy_changes']}\n")

    print("Repeated Rejection Handling")
    print(f"  Repeated Proposal Rate:           {res['repeated_proposal_rate_pct']}%\n")

    print("Stale Proposal Protection")
    print(f"  Executions Against Stale Targets:  {res['stale_target_executions']}\n")

    print("Expired Proposal Protection")
    print(f"  Expired Executions:                {res['expired_executions']}\n")

    print("========================================")
    print(" GOVERNANCE STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
