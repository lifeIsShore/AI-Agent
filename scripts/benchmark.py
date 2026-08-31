import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.triage.engine import PriorityEngine

def benchmark_model(model_name: str, cases_dir: str):
    gateway = ModelGateway(provider="ollama")
    gateway.client.model = model_name
    engine = PriorityEngine(gateway)
    
    results = []
    
    print(f"\nRunning V0.2.3 Hybrid benchmark for model: {model_name}")
    print("-" * 50)
    
    cases = sorted(os.listdir(cases_dir))
    for filename in cases:
        if not filename.endswith(".json"):
            continue
            
        with open(os.path.join(cases_dir, filename), 'r') as f:
            email_data = json.load(f)
            
        start_time = time.time()
        
        try:
            parsed, bypassed = engine.evaluate(email_data)
            latency = time.time() - start_time
            
            valid_keys = {"priority", "requires_action", "deadline", "category", "suggested_action"}
            is_valid_schema = all(key in parsed for key in valid_keys)
            
            results.append({
                "case": filename,
                "latency": latency,
                "valid_schema": is_valid_schema,
                "priority_output": parsed.get("priority", "N/A"),
                "category_output": parsed.get("category", "N/A"),
                "bypassed": bypassed,
                "requires_action": parsed.get("requires_action", False)
            })
            byp_str = "[BYPASS]" if bypassed else "[LLM]"
            print(f"[{filename}] SUCCESS - {latency:.2f}s - {byp_str} - {parsed.get('priority')} ({parsed.get('category')})")
            
        except Exception as e:
            latency = time.time() - start_time
            results.append({
                "case": filename,
                "latency": latency,
                "valid_schema": False,
                "priority_output": "ERROR",
                "category_output": str(e),
                "bypassed": False,
                "requires_action": False
            })
            print(f"[{filename}] FAILED - {latency:.2f}s - {str(e)}")
            
    return results

def print_summary(results):
    print("\n\n" + "="*80)
    print("V0.2.3 HYBRID BENCHMARK RESULTS (Qwen 1.5B)")
    print("="*80)
    
    total_latency = 0
    bypassed_count = 0
    marketing_total = 0
    marketing_bypassed = 0
    urgent_total = 0
    urgent_detected = 0
    false_urgent = 0
    
    print(f"| {'Case':<40} | {'Bypass':<6} | {'Priority':<12} | {'Action':<6} | {'Latency':<8} |")
    print("|" + "-"*42 + "|" + "-"*8 + "|" + "-"*14 + "|" + "-"*8 + "|" + "-"*10 + "|")
    
    for res in results:
        case_name = res['case'].replace('.json', '')
        byp_str = "YES" if res['bypassed'] else "NO"
        action_str = "YES" if res['requires_action'] else "NO"
        
        print(f"| {case_name:<40} | {byp_str:<6} | {res['priority_output']:<12} | {action_str:<6} | {res['latency']:<7.2f}s |")
        
        total_latency += res['latency']
        if res['bypassed']: bypassed_count += 1
        
        if case_name.startswith("irrelevant") or "newsletter" in case_name:
            marketing_total += 1
            if res['bypassed']: marketing_bypassed += 1
            
        if case_name.startswith("urgent"):
            urgent_total += 1
            if res['priority_output'] == "urgent": urgent_detected += 1
            
        if not case_name.startswith("urgent") and res['priority_output'] == "urgent":
            false_urgent += 1

    total = len(results)
    avg_latency = total_latency / total if total > 0 else 0
    marketing_det_rate = (marketing_bypassed / marketing_total * 100) if marketing_total > 0 else 100
    urgent_det_rate = (urgent_detected / urgent_total * 100) if urgent_total > 0 else 100
    false_urgent_rate = (false_urgent / (total - urgent_total) * 100) if (total - urgent_total) > 0 else 0
    bypassed_rate = (bypassed_count / total * 100) if total > 0 else 0

    print("="*80)
    print("METRICS:")
    print(f"Average Latency:             {avg_latency:.2f} sec (Target: <6 sec)")
    print(f"LLM Calls Avoided:           {bypassed_rate:.1f}% (Target: >30%)")
    print(f"Obvious Marketing Detection: {marketing_det_rate:.1f}% (Target: >=95%)")
    print(f"Urgent Detection:            {urgent_det_rate:.1f}% (Target: >=90%)")
    print(f"False Urgent Rate:           {false_urgent_rate:.1f}% (Target: <5%)")

def main():
    cases_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'email_cases'))
    results = benchmark_model("qwen2.5:1.5b", cases_dir)
    print_summary(results)

if __name__ == "__main__":
    main()
