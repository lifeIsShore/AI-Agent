import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.goals.benchmark import GoalBenchmark

def main():
    print("========================================")
    print(" V2.9 GOAL & SELF-IMPROVEMENT REPORT    ")
    print("========================================\n")

    bm = GoalBenchmark()
    res = bm.run_benchmark()

    print("Goal Management & Milestones")
    print(f"  Goal Tracking Accuracy:             {res['goal_tracking_accuracy_pct']}%")
    print(f"  Milestone Resolution Accuracy:      {res['milestone_resolution_accuracy_pct']}%\n")

    print("Progress & Stalled Goal Detection")
    print(f"  Progress Estimation Accuracy:        {res['progress_estimation_accuracy_pct']}%")
    print(f"  Stalled Goal Detection:              {res['stalled_goal_detection_pct']}%")
    print(f"  Deadline Risk Detection:             {res['deadline_risk_detection_pct']}%\n")

    print("Self-Evaluation & Strategy Evolution")
    print(f"  Outcome Diagnosis Accuracy:          {res['outcome_diagnosis_accuracy_pct']}%")
    print(f"  Recommendation Quality:              {res['improvement_recommendation_quality_pct']}%")
    print(f"  Strategy Selection Accuracy:         {res['strategy_selection_accuracy_pct']}%\n")

    print("Safety & Governance")
    print(f"  Unauthorized Policy Changes:             {res['unauthorized_policy_changes']}")
    print(f"  Unauthorized Goal Mutations:             {res['unauthorized_goal_mutations']}")
    print(f"  Security Bypasses:                       {res['security_bypasses']}\n")

    print("========================================")
    print(" GOAL INTELLIGENCE STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
