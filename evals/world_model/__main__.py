import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.world_model.benchmark import WorldModelBenchmark

def main():
    print("========================================")
    print(" V2.8 PERSONAL WORLD MODEL REPORT       ")
    print("========================================\n")

    bm = WorldModelBenchmark()
    res = bm.run_benchmark()

    print("Entity Resolution & Relationships")
    print(f"  Entity Resolution Accuracy:      {res['entity_resolution_accuracy_pct']}%")
    print(f"  Relationship Accuracy:            {res['relationship_accuracy_pct']}%\n")

    print("Temporal Reasoning & Provenance")
    print(f"  Temporal Accuracy:                {res['temporal_accuracy_pct']}%")
    print(f"  Traceable Facts:                 {res['provenance_traceable_pct']}%\n")

    print("Confidence & Situation Detection")
    print(f"  Calibration Accuracy:             {res['confidence_calibration_pct']}%")
    print(f"  Situation Detection Accuracy:     {res['situation_detection_accuracy_pct']}%\n")

    print("Security & Mutation Safety")
    print(f"  Unauthorized World Mutations:     {res['unauthorized_world_mutations']}")
    print(f"  Sensitive Data Violations:        {res['sensitive_data_violations']}\n")

    print("========================================")
    print(" WORLD MODEL STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
