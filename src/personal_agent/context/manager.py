import time
from typing import List, Dict, Any, Optional
from personal_agent.context.package import ContextPackage
from personal_agent.rag.retriever import RAGRetriever
from personal_agent.memory.manager import MemoryManager

class ContextManager:
    # Context Budgets (Tailored for Qwen 1.5B 16GB RAM)
    MAX_MEMORIES = 3
    MAX_RAG_CHUNKS = 5
    MAX_EMAILS = 5

    def __init__(self, gateway):
        self.gateway = gateway
        self.rag_retriever = RAGRetriever()
        self.memory_manager = MemoryManager(gateway=gateway)

    def classify_intent(self, user_request: str) -> str:
        """Determines the core task type from the user request."""
        req_lower = user_request.lower()
        if any(x in req_lower for x in ["plan", "schedule", "today", "organize"]):
            return "plan_day"
        if any(x in req_lower for x in ["email", "inbox", "mail", "unread", "messages"]):
            return "review_inbox"
        if any(x in req_lower for x in ["cv", "resume", "thesis", "course", "degree", "document", "requirements", "university"]):
            return "query_knowledge"
        return "general_query"

    def assemble_context(
        self,
        user_request: str,
        emails: Optional[List[Dict[str, Any]]] = None,
        calendar: Optional[List[str]] = None,
        tasks: Optional[List[str]] = None
    ) -> ContextPackage:
        
        start_time = time.time()
        task_type = self.classify_intent(user_request)
        
        retrieved_knowledge = []
        retrieved_memory = []
        included_emails = []
        sources = ["User Instruction"]

        # 1. Knowledge RAG Retrieval (If request needs knowledge or planning)
        if task_type in ["query_knowledge", "plan_day", "general_query"]:
            rag_results = self.rag_retriever.search(user_request, top_k=self.MAX_RAG_CHUNKS)
            retrieved_knowledge = rag_results[:self.MAX_RAG_CHUNKS]
            for chunk in retrieved_knowledge:
                fn = chunk.get("metadata", {}).get("filename")
                if fn and fn not in sources:
                    sources.append(f"RAG: {fn}")

        # 2. Personal Memory Retrieval (Filter to Top MAX_MEMORIES by importance)
        all_memories = self.memory_manager.get_context_memories()
        # High importance first
        all_memories.sort(key=lambda x: 0 if x.get("importance") == "high" else 1)
        retrieved_memory = all_memories[:self.MAX_MEMORIES]
        if retrieved_memory:
            sources.append("Personal Memory Store")

        # 3. Live Emails Processing (Enforce MAX_EMAILS Budget)
        if emails:
            included_emails = emails[:self.MAX_EMAILS]
            sources.append("Gmail Inbox")

        # 4. Construct Context Trace
        elapsed_sec = time.time() - start_time
        prompt_text = f"{user_request} " + " ".join([m.get("content", "") for m in retrieved_memory]) + " ".join([k.get("text", "") for k in retrieved_knowledge])
        approx_tokens = len(prompt_text.split()) * 1.3
        
        trace = {
            "task_type": task_type,
            "latency_sec": round(elapsed_sec, 3),
            "approx_tokens": int(approx_tokens),
            "memory_items_used": len(retrieved_memory),
            "rag_chunks_used": len(retrieved_knowledge),
            "emails_used": len(included_emails),
            "sources": sources
        }

        return ContextPackage(
            task=task_type,
            user_request=user_request,
            memory=retrieved_memory,
            knowledge=retrieved_knowledge,
            emails=included_emails,
            calendar=calendar or [],
            tasks=tasks or [],
            sources=sources,
            trace=trace
        )
