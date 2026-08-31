import os
import glob
from typing import List, Dict, Any, Optional
from personal_agent.rag.embeddings import OllamaEmbeddings
from personal_agent.rag.vector_store import VectorStore
from personal_agent.rag.ingest import DocumentChunker

class RAGRetriever:
    def __init__(self, store_path: str = "data/knowledge/vector_store.json"):
        self.embeddings = OllamaEmbeddings()
        self.vector_store = VectorStore(store_path)

    def ingest_document(self, file_path: str, category: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        filename = os.path.basename(file_path)
        document_id = f"{category}/{filename}"
        
        # Remove old chunks for this document if re-ingesting
        self.vector_store.delete_document(document_id)
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        chunks = DocumentChunker.chunk_text(text)
        print(f"Ingesting '{filename}' ({category}): {len(chunks)} chunks...")
        
        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{document_id}#chunk-{idx}"
            emb = self.embeddings.get_embedding(chunk_text)
            metadata = {
                "category": category,
                "filename": filename,
                "chunk_index": idx,
                "source_path": file_path
            }
            self.vector_store.add_chunk(chunk_id, document_id, chunk_text, emb, metadata)
            
        self.vector_store.save()

    def rebuild(self, knowledge_dir: str = "data/knowledge"):
        self.vector_store.clear()
        pattern = os.path.join(knowledge_dir, "**", "*.*")
        files = glob.glob(pattern, recursive=True)
        
        for file_path in files:
            if file_path.endswith("vector_store.json") or not (file_path.endswith(".md") or file_path.endswith(".txt")):
                continue
                
            rel_path = os.path.relpath(file_path, knowledge_dir)
            parts = rel_path.split(os.sep)
            category = parts[0] if len(parts) > 1 else "general"
            self.ingest_document(file_path, category)

    def search(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query_emb = self.embeddings.get_embedding(query)
        return self.vector_store.search(query_emb, top_k=top_k, category_filter=category_filter)

    def delete(self, document_id: str):
        self.vector_store.delete_document(document_id)
