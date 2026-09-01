import time
from typing import List, Dict, Any, Optional
from personal_agent.context.package import ContextPackage
from personal_agent.rag.retriever import RAGRetriever
from personal_agent.memory.manager import MemoryManager

class ContextManager:
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

    def get_intent_budgets(self, task_type: str) -> Dict[str, Any]:
        """Returns dynamic context budgets based on the task intent."""
        if task_type == "review_inbox":
            return {
                "max_emails": 15,
                "max_memories": 2,
                "max_rag_chunks": 0,
                "include_calendar": False,
                "include_tasks": False,
                "only_planning_emails": False
            }
        elif task_type == "query_knowledge":
            return {
                "max_emails": 0,
                "max_memories": 3,
                "max_rag_chunks": 5,
                "include_calendar": False,
                "include_tasks": False,
                "only_planning_emails": False
            }
        elif task_type == "plan_day":
            return {
                "max_emails": 5,
                "max_memories": 3,
                "max_rag_chunks": 2,
                "include_calendar": True,
                "include_tasks": True,
                "only_planning_emails": True
            }
        else: # general_query
            return {
                "max_emails": 3,
                "max_memories": 3,
                "max_rag_chunks": 3,
                "include_calendar": True,
                "include_tasks": True,
                "only_planning_emails": False
            }

    def assemble_context(
        self,
        user_request: str,
        emails: Optional[List[Dict[str, Any]]] = None,
        calendar: Optional[List[Any]] = None,
        tasks: Optional[List[Any]] = None
    ) -> ContextPackage:
        
        start_time = time.time()
        task_type = self.classify_intent(user_request)
        budgets = self.get_intent_budgets(task_type)
        
        retrieved_knowledge = []
        retrieved_memory = []
        included_emails = []
        included_calendar = []
        included_tasks = []
        sources = ["User Instruction"]

        # 1. Knowledge RAG Retrieval (Filtered by Budget)
        max_rag = budgets.get("max_rag_chunks", 0)
        if max_rag > 0:
            rag_results = self.rag_retriever.search(user_request, top_k=max_rag)
            retrieved_knowledge = rag_results[:max_rag]
            for chunk in retrieved_knowledge:
                fn = chunk.get("metadata", {}).get("filename")
                if fn and f"RAG: {fn}" not in sources:
                    sources.append(f"RAG: {fn}")

        # 2. Personal Memory Retrieval (Filtered by Budget)
        max_mem = budgets.get("max_memories", 0)
        if max_mem > 0:
            all_memories = self.memory_manager.get_context_memories()
            all_memories.sort(key=lambda x: 0 if x.get("importance") == "high" else 1)
            retrieved_memory = all_memories[:max_mem]
            if retrieved_memory:
                sources.append("Personal Memory Store")

        # 3. Live Data Processing (Filtered by Intent & Budget)
        max_em = budgets.get("max_emails", 0)
        if emails and max_em > 0:
            candidate_emails = emails
            if budgets.get("only_planning_emails", False):
                candidate_emails = [
                    e for e in emails 
                    if e.get("requires_action", False) and e.get("requires_planning", False)
                ]
            included_emails = candidate_emails[:max_em]
            if included_emails:
                sources.append("Gmail Inbox")

        if calendar and budgets.get("include_calendar", False):
            included_calendar = calendar
            sources.append("Google Calendar")

        if tasks and budgets.get("include_tasks", False):
            included_tasks = tasks
            sources.append("Google Tasks")

        # 4. Construct Context Trace
        elapsed_sec = time.time() - start_time
        prompt_text = f"{user_request} " + " ".join([m.get("content", "") for m in retrieved_memory]) + " ".join([k.get("text", "") for k in retrieved_knowledge])
        approx_tokens = len(prompt_text.split()) * 1.3
        
        trace = {
            "task_type": task_type,
            "budgets": budgets,
            "latency_sec": round(elapsed_sec, 3),
            "approx_tokens": int(approx_tokens),
            "memory_items_used": len(retrieved_memory),
            "rag_chunks_used": len(retrieved_knowledge),
            "emails_used": len(included_emails),
            "calendar_events_used": len(included_calendar),
            "tasks_used": len(included_tasks),
            "sources": sources
        }

        return ContextPackage(
            task=task_type,
            user_request=user_request,
            memory=retrieved_memory,
            knowledge=retrieved_knowledge,
            emails=included_emails,
            calendar=included_calendar,
            tasks=included_tasks,
            sources=sources,
            trace=trace
        )
