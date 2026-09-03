from typing import Dict, Any

class MemoryConflictResolver:
    def resolve_conflict(
        self,
        existing_memory: Dict[str, Any],
        incoming_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolves conflicting memory assertions ensuring newer explicit USER preferences supersede older assertions."""
        ex_source = existing_memory.get("source", "LEARNED")
        inc_source = incoming_memory.get("source", "LEARNED")

        # Invariant 1: USER explicit preference always supersedes LEARNED assertion
        if inc_source == "USER" and ex_source == "LEARNED":
            res = dict(incoming_memory)
            res["supersedes"] = existing_memory.get("id")
            res["resolution"] = "USER_SUPERSEDES_LEARNED"
            return res

        if ex_source == "USER" and inc_source == "LEARNED":
            res = dict(existing_memory)
            res["resolution"] = "RETAIN_EXISTING_USER"
            return res

        # Invariant 2: Newer USER explicit preference supersedes older USER preference
        if inc_source == "USER" and ex_source == "USER":
            res = dict(incoming_memory)
            res["supersedes"] = existing_memory.get("id")
            res["resolution"] = "NEWER_USER_SUPERSEDES_OLDER_USER"
            return res

        # Default fallback: higher confidence wins
        if incoming_memory.get("confidence", 0.0) > existing_memory.get("confidence", 0.0):
            res = dict(incoming_memory)
            res["supersedes"] = existing_memory.get("id")
            res["resolution"] = "HIGHER_CONFIDENCE_WIN"
            return res

        res = dict(existing_memory)
        res["resolution"] = "RETAIN_EXISTING"
        return res
