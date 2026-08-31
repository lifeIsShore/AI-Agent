import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.rag.retriever import RAGRetriever
from personal_agent.models.gateway import ModelGateway

def print_header(title):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL AI AGENT — RAG VERIFICATION (V0.4.0)")
    
    retriever = RAGRetriever()
    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge'))
    
    print("Rebuilding Knowledge Base Vector Store...")
    retriever.rebuild(knowledge_dir)
    print("Vector Store index complete!\n")
    
    gateway = ModelGateway(provider="ollama")
    
    test_queries = [
        "What are the submission rules and penalties for the university project?",
        "Where did Ahmet complete his Master of Science degree?",
        "What local embedding model does the AI agent use?"
    ]
    
    for query in test_queries:
        print_header(f"QUESTION: {query}")
        
        # 1. Retrieve top 3 relevant chunks
        results = retriever.search(query, top_k=2)
        
        context_str = ""
        sources = []
        for i, res in enumerate(results, 1):
            source_file = res['metadata']['filename']
            category = res['metadata']['category']
            sources.append(f"{category}/{source_file}")
            context_str += f"[Source {i}: {category}/{source_file}]\n{res['text']}\n\n"
            
        print(f"Retrieved Chunks (Similarity: {results[0]['similarity']:.3f}):")
        print(context_str)
        
        # 2. Query Qwen 1.5B with Context
        prompt = f"""You are a helpful Personal Assistant. Answer the user's question accurately using ONLY the provided Context. 
Cite the source file in your answer.

Context:
{context_str}

User Question: {query}
Answer:"""

        print("Generating answer with Qwen 1.5B...")
        answer = gateway.generate(prompt=prompt)
        print("\nAGENT ANSWER:")
        print(answer)
        print("\nCITED SOURCES:", ", ".join(sources))
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
