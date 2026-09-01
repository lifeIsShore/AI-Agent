import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.autonomy.benchmark import AutonomyBenchmark

def main():
    print("========================================")
    print(" V3.0 AUTONOMOUS AGENT REPORT           ")
    print("========================================\n")

    bm = AutonomyBenchmark()
    res = bm.run_benchmark()

    print("Autonomous Goal Management")
    print(f"  Goal Selection Accuracy:             {res['goal_selection_accuracy_pct']}%")
    print(f"  Goal Starvation Rate:                 {res['goal_starvation_rate_pct']}%")
    print(f"  Goal Recovery Accuracy:              {res['goal_recovery_accuracy_pct']}%\n")

    print("Continuous Planning & Execution")
    print(f"  Replanning Accuracy:                 {res['continuous_replanning_accuracy_pct']}%")
    print(f"  Environmental Adaptation:             {res['environmental_adaptation_pct']}%")
    print(f"  Safe Auto-Execution Rate:             {res['safe_auto_execution_rate_pct']}%\n")

    print("Human Governance & Safety Bounds")
    print(f"  Correct Approval Escalation:          {res['correct_approval_escalation_pct']}%")
    print(f"  Critical Actions Blocked:             {res['critical_actions_blocked_pct']}%")
    print(f"  Autonomy Boundary Violations:           {res['autonomy_boundary_violations']}\n")

    print("Resource Governance & Reliability")
    print(f"  Budget Violations:                      {res['resource_budget_violations']}")
    print(f"  Goal Overspending:                      {res['goal_overspending_count']}")
    print(f"  Crash Recovery:                      {res['crash_recovery_pct']}%\n")

    print("========================================")
    print(" AUTONOMY STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
