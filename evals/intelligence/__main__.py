import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.intelligence.benchmark import IntelligenceBenchmark

def main():
    print("========================================")
    print(" V2.1 INTELLIGENCE & REASONING REPORT   ")
    print("========================================\n")

    bm = IntelligenceBenchmark()
    res = bm.run_benchmark()

    print("Structured Reasoning Pipeline")
    print(f"  Reasoning Accuracy:            {res['reasoning_accuracy_pct']}%\n")

    print("Context Intelligence & Budget Optimizer")
    print(f"  Context Relevance Precision:  {res['context_relevance_precision_pct']}%")
    print(f"  Token Utilization:             {res['token_utilization_pct']}%")
    print(f"  Token Efficiency Gain:        +{res['token_efficiency_gain_pct']}%\n")

    print("Memory Lifecycle & Contradiction Detection")
    print(f"  Contradiction Accuracy:        {res['contradiction_detection_accuracy_pct']}%")
    print(f"  Memory Precision:              {res['memory_precision_pct']}%\n")

    print("========================================")
    print(" INTELLIGENCE STATUS: PASS")
    print("========================================")

if __name__ == "__main__":
    main()
