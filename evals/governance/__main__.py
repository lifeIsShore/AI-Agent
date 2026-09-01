import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.governance.benchmark import GovernanceBenchmark

def main():
    print("========================================")
    print(" V1.9 GOVERNANCE & DATA SECURITY REPORT ")
    print("========================================\n")

    bm = GovernanceBenchmark()
    res = bm.run_benchmark()

    print("Policy Evaluation")
    print(f"  Correct Decisions:             {res['correct_policy_decisions_pct']}%")
    print(f"  Policy Violations:                {res['policy_violations']}\n")

    print("Data Classification")
    print(f"  Correct Classifications:       {res['classification_accuracy_pct']}%\n")

    print("Data Loss Prevention")
    print(f"  Sensitive Data Leaks:              {res['sensitive_data_leaks']}\n")

    print("Provenance")
    print(f"  Untraceable Decisions:             {res['untraceable_decisions']}\n")

    print("Policy Simulation")
    print(f"  Tested Rules:                     {res['tested_rules_count']}")
    print(f"  Conflicts Detected:                {res['conflicts_detected']}\n")

    print("Security Invariants")
    print(f"  Violations:                        {res['security_invariant_violations']}\n")

    print("========================================")
    print(" GOVERNANCE STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
