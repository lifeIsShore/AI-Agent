import os
import json
import math
from typing import List, Dict, Any, Optional

class VectorStore:
    def __init__(self, store_path: str):
        self.store_path = store_path
        self.chunks: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"Failed to load vector store: {e}")
                self.chunks = []

    def save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)

    def add_chunk(self, chunk_id: str, document_id: str, text: str, embedding: List[float], metadata: Dict[str, Any]):
        self.chunks.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "text": text,
            "embedding": embedding,
            "metadata": metadata
        })

    def delete_document(self, document_id: str):
        self.chunks = [c for c in self.chunks if c.get("document_id") != document_id]
        self.save()

    def clear(self):
        self.chunks = []
        self.save()

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def search(self, query_embedding: List[float], top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for chunk in self.chunks:
            if category_filter and chunk.get("metadata", {}).get("category") != category_filter:
                continue
            sim = self._cosine_similarity(query_embedding, chunk.get("embedding", []))
            results.append({
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "text": chunk.get("text"),
                "metadata": chunk.get("metadata"),
                "similarity": sim
            })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
