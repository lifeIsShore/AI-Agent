import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.memory.manager import MemoryManager
from personal_agent.rag.retriever import RAGRetriever

def print_header(title):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL AI AGENT — MEMORY & RAG VERIFICATION (V0.4.1)")
    
    # 1. Update RAG Vector Store with user's updated CV and documents
    retriever = RAGRetriever()
    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge'))
    print("Rebuilding RAG Knowledge Base with updated user documents...")
    retriever.rebuild(knowledge_dir)
    print("RAG Vector Store updated successfully!\n")
    
    # 2. Initialize Memory Manager
    gateway = ModelGateway(provider="ollama")
    memory_mgr = MemoryManager(gateway=gateway)
    
    # Clear store for clean test run
    for m_type in ["goal", "preference", "important_person", "decision"]:
        for item in memory_mgr.store.get_memories(memory_type=m_type):
            memory_mgr.store.delete_memory(m_type, item["id"])
            
    print_header("1. TESTING MEMORY POLICY EVALUATION")
    
    candidate_statements = [
        ("I prefer responding to university emails in the afternoon after 14:00.", "user"),
        ("My goal is to complete my M.Sc. thesis in Financial Crime Prevention at University of Mannheim.", "user"),
        ("I am unavailable this Friday afternoon from 2 PM to 4 PM.", "email"),
        ("Prof. Davis is my thesis advisor for Advanced Agentic AI.", "email")
    ]
    
    for stmt, src in candidate_statements:
        print(f"Candidate ({src}): \"{stmt}\"")
        stored = memory_mgr.process_candidate_fact(stmt, source=src)
        if stored:
            print(f"  ✅ ACCEPTED -> Type: [{stored['type']}] | Importance: [{stored['importance']}]")
            print(f"     Reason: {stored.get('policy_reason')}\n")
        else:
            print(f"  ❌ DISCARDED -> (Flagged as transient / temporary event)\n")
            
    print_header("2. ACTIVE MEMORY DUMP")
    active_memories = memory_mgr.get_context_memories()
    print(f"Total Persistent Memories Stored: {len(active_memories)}")
    for mem in active_memories:
        print(f"- [{mem['type'].upper()}] (Importance: {mem['importance']}, Source: {mem['source']}): {mem['content']}")
        
    print_header("3. RAG QUERY WITH UPDATED CV")
    query = "What is Ahmet's education background and work experience?"
    results = retriever.search(query, top_k=2)
    
    context_str = "\n".join([f"[{r['metadata']['filename']}]: {r['text']}" for r in results])
    prompt = f"Using ONLY the provided CV context, summarize Ahmet's education and experience.\n\nContext:\n{context_str}\n\nSummary:"
    
    answer = gateway.generate(prompt=prompt)
    print("CV RAG Summary:")
    print(answer)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    main()
