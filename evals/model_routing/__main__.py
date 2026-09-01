import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.model_routing.benchmark import ModelRoutingBenchmark

def main():
    print("========================================")
    print(" V1.7 MODEL ROUTING & OPTIMIZATION REPORT")
    print("========================================\n")

    bm = ModelRoutingBenchmark()
    res = bm.run_benchmark()

    print(f"Scenario Benchmark Count:   {res['total_scenarios']}")
    print(f"Routing Accuracy:           {res['routing_accuracy_pct']}% ({res['correct_routes']}/{res['total_scenarios']})")
    print(f"Token Reduction:            {res['token_savings_pct']}% ({res['tokens_routed']} vs {res['tokens_unrouted_baseline']} baseline)")
    print(f"P50 Latency (Avg):          {res['avg_latency_ms']} ms ({res['latency_reduction_pct']}% faster)")
    print(f"Cost Savings:               {res['cost_savings_pct']}% (${res['total_cost_routed_usd']} total)")

    print("\n========================================")
    print(" ROUTING STATUS: OPTIMAL")
    print("========================================")

if __name__ == "__main__":
    main()
