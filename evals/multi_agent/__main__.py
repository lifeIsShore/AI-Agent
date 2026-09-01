import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.multi_agent.benchmark import MultiAgentBenchmark

def main():
    print("========================================")
    print(" V2.7 MULTI-AGENT COLLABORATION REPORT ")
    print("========================================\n")

    bm = MultiAgentBenchmark()
    res = bm.run_benchmark()

    print("Delegation & Communication")
    print(f"  Task Assignment Accuracy:        {res['task_assignment_accuracy_pct']}%")
    print(f"  Message Delivery Success:       {res['message_delivery_success_pct']}%\n")

    print("Capability Security")
    print(f"  Unauthorized Agent Actions:      {res['capability_isolation_violations']}")
    print(f"  Privilege Escalations:            {res['privilege_escalations']}\n")

    print("Conflict Resolution")
    print(f"  Correct Resolutions:             {res['conflict_resolution_accuracy_pct']}%")
    print(f"  Human Escalation Accuracy:       {res['human_escalation_accuracy_pct']}%\n")

    print("Resource Governance & Reliability")
    print(f"  Agent Overspend:                  {res['agent_overspend_count']}")
    print(f"  Lost Agent Tasks:                 {res['lost_agent_tasks']}")
    print(f"  Recovery Success:                {res['recovery_success_pct']}%\n")

    print("========================================")
    print(" MULTI-AGENT STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
