import uuid
from typing import Dict, Any, List

class MemoryConsolidator:
    def consolidate_observations(
        self,
        observations: List[Dict[str, Any]],
        threshold: int = 5
    ) -> List[Dict[str, Any]]:
        """Periodically converts repeated observations into durable knowledge."""
        if not observations:
            return []

        counts: Dict[str, int] = {}
        sample_map: Dict[str, Dict[str, Any]] = {}

        for obs in observations:
            pattern_key = f"{obs.get('domain', 'general')}:{obs.get('pattern', 'default')}"
            counts[pattern_key] = counts.get(pattern_key, 0) + 1
            if pattern_key not in sample_map:
                sample_map[pattern_key] = obs

        consolidated: List[Dict[str, Any]] = []
        for pattern_key, count in counts.items():
            if count >= threshold:
                sample = sample_map[pattern_key]
                consolidated.append({
                    "durable_id": f"dur_{uuid.uuid4().hex[:8]}",
                    "domain": sample.get("domain", "general"),
                    "pattern": sample.get("pattern", "default"),
                    "durable_fact": f"User consistently exhibits pattern '{sample.get('pattern', 'default')}' ({count} observations).",
                    "observation_count": count,
                    "confidence": min(1.0, 0.7 + (count * 0.05)),
                    "status": "DURABLE"
                })

        return consolidated
