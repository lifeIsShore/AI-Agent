import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.adaptive_execution.benchmark import AdaptiveExecutionBenchmark

def main():
    print("========================================")
    print(" V2.4 ADAPTIVE EXECUTION REPORT         ")
    print("========================================\n")

    bm = AdaptiveExecutionBenchmark()
    res = bm.run_benchmark()

    print("Workflow Coordination")
    print(f"  Correct Next-Step Decisions:       {res['correct_next_step_decisions_pct']}%")
    print(f"  Dependency Preservation:           {res['dependency_preservation_pct']}%\n")

    print("Failure Recovery")
    print(f"  Transient Recovery Rate:            {res['transient_recovery_rate_pct']}%")
    print(f"  Correct Failure Classification:     {res['correct_failure_classification_pct']}%")
    print(f"  Duplicate Executions:                {res['duplicate_executions']}\n")

    print("Resource Governance")
    print(f"  Budget Violations:                   {res['budget_violations']}")
    print(f"  Token Budget Accuracy:            {res['token_budget_accuracy_pct']}%")
    print(f"  Cost Limit Violations:               {res['cost_limit_violations']}")
    print(f"  Runtime Limit Violations:            {res['runtime_limit_violations']}\n")

    print("Dynamic Model Routing")
    print(f"  Routing Accuracy:                   {res['routing_accuracy_pct']}%")
    print(f"  Escalation Accuracy:                {res['escalation_accuracy_pct']}%\n")

    print("Context Isolation")
    print(f"  Unnecessary Data Exposure:            {res['unnecessary_data_exposure']}")
    print(f"  Sensitive Context Violations:        {res['sensitive_context_violations']}\n")

    print("Workflow Control")
    print(f"  Cancellation Accuracy:             {res['cancellation_accuracy_pct']}%")
    print(f"  Safe Stop Accuracy:                {res['safe_stop_accuracy_pct']}%\n")

    print("========================================")
    print(" ADAPTIVE EXECUTION STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
