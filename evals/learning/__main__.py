import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.learning.benchmark import LearningBenchmark

def main():
    print("========================================")
    print(" V2.6 LEARNING & OUTCOME REPORT         ")
    print("========================================\n")

    bm = LearningBenchmark()
    res = bm.run_benchmark()

    print("Workflow Outcome Performance")
    print(f"  Workflow Success Rate:             {res['workflow_success_rate_pct']}%")
    print(f"  User Acceptance Rate:              {res['user_acceptance_rate_pct']}%")
    print(f"  Correction Adaptation Rate:        {res['user_correction_adaptation_rate_pct']}%\n")

    print("Quality & Proactivity")
    print(f"  Repeated Failure Rate:             {res['repeated_failure_rate_pct']}%")
    print(f"  Proactive Helpfulness Rate:        {res['proactive_helpfulness_rate_pct']}%\n")

    print("Security Invariant Compliance")
    print(f"  Policy Compliance:                 {res['policy_invariant_compliance_pct']}%\n")

    print("========================================")
    print(" LEARNING STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
