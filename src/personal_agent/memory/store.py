import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

MEMORY_TYPES = ["goal", "preference", "important_person", "decision", "other"]

class MemoryStore:
    def __init__(self, data_dir: str = "data/memory"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_file_path(self, memory_type: str) -> str:
        filename = f"{memory_type}s.json" if not memory_type.endswith("s") else f"{memory_type}.json"
        if memory_type == "important_person":
            filename = "important_people.json"
        return os.path.join(self.data_dir, filename)

    def _load_memories(self, memory_type: str) -> List[Dict[str, Any]]:
        path = self._get_file_path(memory_type)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {memory_type} memories: {e}")
                return []
        return []

    def _save_memories(self, memory_type: str, items: List[Dict[str, Any]]):
        path = self._get_file_path(memory_type)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    def add_memory(
        self,
        memory_type: str,
        content: str,
        source: str = "user",
        importance: str = "medium",
        confidence: float = 1.0,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        now_str = datetime.now(timezone.utc).isoformat()
        item_id = f"mem_{uuid.uuid4().hex[:8]}"
        
        memory_item = {
            "id": item_id,
            "type": memory_type,
            "content": content,
            "created_at": now_str,
            "updated_at": now_str,
            "source": source,
            "confidence": confidence,
            "importance": importance,
            "expires_at": expires_at,
            "metadata": metadata or {}
        }
        
        items = self._load_memories(memory_type)
        items.append(memory_item)
        self._save_memories(memory_type, items)
        return memory_item

    def get_memories(self, memory_type: Optional[str] = None, importance: Optional[str] = None) -> List[Dict[str, Any]]:
        self.expire_memories()
        
        types_to_fetch = [memory_type] if memory_type else ["goal", "preference", "important_person", "decision"]
        all_items = []
        
        for m_type in types_to_fetch:
            items = self._load_memories(m_type)
            for item in items:
                if importance and item.get("importance") != importance:
                    continue
                all_items.append(item)
                
        return all_items

    def delete_memory(self, memory_type: str, memory_id: str) -> bool:
        items = self._load_memories(memory_type)
        filtered = [i for i in items if i.get("id") != memory_id]
        if len(filtered) < len(items):
            self._save_memories(memory_type, filtered)
            return True
        return False

    def expire_memories(self):
        """Clean up memories past their expires_at date."""
        now = datetime.now(timezone.utc)
        for m_type in ["goal", "preference", "important_person", "decision"]:
            items = self._load_memories(m_type)
            active = []
            for item in items:
                exp = item.get("expires_at")
                if exp and exp != "none":
                    try:
                        exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
                        if exp_dt < now:
                            continue  # Expired
                    except ValueError:
                        pass
                active.append(item)
            if len(active) < len(items):
                self._save_memories(m_type, active)
