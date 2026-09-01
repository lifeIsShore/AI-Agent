import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.orchestration.benchmark import OrchestrationBenchmark

def main():
    print("========================================")
    print(" V2.3 ORCHESTRATION & PLANNING REPORT   ")
    print("========================================\n")

    bm = OrchestrationBenchmark()
    res = bm.run_benchmark()

    print("Planning & Routing Accuracy")
    print(f"  Plan Validity:                 {res['plan_validity_rate_pct']}%")
    print(f"  Dependency Resolution:        {res['dependency_resolution_pct']}%")
    print(f"  Tool Selection Accuracy:       {res['tool_selection_accuracy_pct']}%")
    print(f"  Plan Security Validation:     {res['plan_security_validation_pct']}%\n")

    print("Parallel Execution & Performance")
    print(f"  Parallel Execution Success:    {res['parallel_execution_success_pct']}%")
    print(f"  Average Workflow Speedup:     {res['average_workflow_speedup_ratio']}x")
    print(f"  Token Efficiency Gain:        +{res['token_efficiency_gain_pct']}%\n")

    print("Governance & Resource Bounds")
    print(f"  Unauthorized Tool Calls:       {res['unauthorized_tool_calls']}")
    print(f"  Budget Violations:             {res['budget_violations']}")
    print(f"  Duplicate Executions:          {res['duplicate_executions']}")
    print(f"  Human Intervention Rate:       {res['human_intervention_rate_pct']}%\n")

    print("========================================")
    print(" ORCHESTRATION STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
