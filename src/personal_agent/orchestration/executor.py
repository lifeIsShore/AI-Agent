import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Tuple

class ParallelExecutor:
    def execute_parallel_group(
        self,
        step_tasks: List[Tuple[str, Callable[[], Any]]]
    ) -> Dict[str, Any]:
        """Executes independent tasks concurrently and measures latency vs sequential execution."""
        start_time = time.time()
        results = {}
        individual_latencies = []

        with ThreadPoolExecutor(max_workers=len(step_tasks)) as executor:
            future_to_id = {}
            for step_id, task_fn in step_tasks:
                t0 = time.time()
                future = executor.submit(task_fn)
                future_to_id[future] = (step_id, t0)

            for future in as_completed(future_to_id):
                step_id, t0 = future_to_id[future]
                lat = (time.time() - t0) * 1000.0
                individual_latencies.append(lat)
                try:
                    res = future.result()
                    results[step_id] = {"status": "SUCCESS", "output": res, "latency_ms": round(lat, 2)}
                except Exception as e:
                    results[step_id] = {"status": "FAILED", "error": str(e), "latency_ms": round(lat, 2)}

        total_parallel_lat = (time.time() - start_time) * 1000.0
        sequential_est_lat = sum(individual_latencies) if individual_latencies else 1.0

        speedup_ratio = round(sequential_est_lat / max(1.0, total_parallel_lat), 2)
        if speedup_ratio < 1.0:
            speedup_ratio = 1.0

        return {
            "results": results,
            "parallel_latency_ms": round(total_parallel_lat, 2),
            "sequential_latency_est_ms": round(sequential_est_lat, 2),
            "speedup_ratio": speedup_ratio
        }
