from typing import Dict, Any, List

class MemoryDecayEngine:
    def apply_decay(
        self,
        memories: List[Dict[str, Any]],
        days_passed: int = 30,
        decay_rate: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Calculates confidence decay over time for old/unused memories."""
        updated: List[Dict[str, Any]] = []

        for m in memories:
            m_copy = dict(m)
            source = m_copy.get("source", "LEARNED")
            conf = m_copy.get("confidence", 0.85)

            if source == "USER":
                # Explicit USER preferences do NOT decay automatically
                m_copy["confidence"] = conf
                m_copy["decay_status"] = "PROTECTED_USER"
            elif m_copy.get("temporary", False):
                m_copy["confidence"] = 0.0
                m_copy["decay_status"] = "EXPIRED"
            else:
                new_conf = max(0.1, conf - (days_passed * decay_rate))
                m_copy["confidence"] = round(new_conf, 3)
                m_copy["decay_status"] = "DECAYED" if new_conf < conf else "STABLE"

            updated.append(m_copy)

        return updated
