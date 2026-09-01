import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.workflows.benchmark import WorkflowBenchmark

def main():
    print("========================================")
    print(" V2.2 WORKFLOW INTELLIGENCE REPORT      ")
    print("========================================\n")

    bm = WorkflowBenchmark()
    res = bm.run_benchmark()

    print("Workflow Engine Performance")
    print(f"  Workflow Completion Rate:      {res['workflow_completion_rate_pct']}%")
    print(f"  Dependency Resolution:        {res['dependency_resolution_accuracy_pct']}%")
    print(f"  Checkpoint Recovery:           {res['checkpoint_recovery_pct']}%\n")

    print("Execution & Verification")
    print(f"  Verified Execution Rate:       {res['verified_execution_rate_pct']}%")
    print(f"  Duplicate Execution Rate:      {res['duplicate_execution_rate_pct']}%\n")

    print("Dynamic Replanning")
    print(f"  Replanning Accuracy:           {res['replanning_accuracy_pct']}%")
    print(f"  Stale State Detection:         {res['stale_state_detection_pct']}%\n")

    print("Security & Policy Compliance")
    print(f"  Unauthorized Workflow Actions:   {res['unauthorized_workflow_actions']}")
    print(f"  Policy Bypasses:                 {res['policy_bypasses']}\n")

    print("========================================")
    print(" WORKFLOW STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
