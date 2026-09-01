import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.context.manager import ContextManager

def print_header(title):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL AI AGENT — CONTEXT MANAGER VERIFICATION (V0.4.2)")
    
    gateway = ModelGateway(provider="ollama")
    ctx_mgr = ContextManager(gateway=gateway)
    
    # Sample mock email feed for inbox testing
    mock_emails = [
        {"sender": "Prof. Davis <davis@university.edu>", "subject": "Thesis Submission Deadline", "suggested_action": "Submit by tomorrow noon", "priority": "urgent"},
        {"sender": "Bank Security <security@bank.com>", "subject": "Account Alert", "suggested_action": "Call bank", "priority": "important"},
        {"sender": "LinkedIn <jobalerts@linkedin.com>", "subject": "New Jobs in Frankfurt", "suggested_action": "Review job post", "priority": "normal"}
    ]
    
    scenarios = [
        ("Scenario 1: Knowledge Inquiry", "What are the submission rules and grading scheme for my university module?", None),
        ("Scenario 2: Inbox Review", "Check my inbox for urgent university or financial emails.", mock_emails),
        ("Scenario 3: Daily Planning Request", "Plan my day considering my work preferences and active goals.", mock_emails)
    ]
    
    for label, request_text, emails_input in scenarios:
        print_header(label)
        print(f"User Request: \"{request_text}\"\n")
        
        # 1. Assemble Context Package
        pkg = ctx_mgr.assemble_context(
            user_request=request_text,
            emails=emails_input,
            calendar=["09:00 - 11:00 Lecture (CS-801)", "14:00 - 15:00 Team Meeting"],
            tasks=["Finish Master's Thesis Proposal", "Review Code PR"]
        )
        
        # 2. Print Context Trace
        trace = pkg.trace
        print("🔍 CONTEXT TRACE:")
        print(f"  - Intent Classified: [{trace['task_type'].upper()}]")
        print(f"  - Memory Items Used:  {trace['memory_items_used']} / {ContextManager.MAX_MEMORIES} (Budget)")
        print(f"  - RAG Chunks Used:    {trace['rag_chunks_used']} / {ContextManager.MAX_RAG_CHUNKS} (Budget)")
        print(f"  - Live Emails Used:   {trace['emails_used']} / {ContextManager.MAX_EMAILS} (Budget)")
        print(f"  - Approx Tokens:      ~{trace['approx_tokens']}")
        print(f"  - Sources Included:   {', '.join(trace['sources'])}\n")
        
        # 3. Generate Qwen Response using Formatted Context Package
        formatted_prompt = pkg.to_prompt_context() + "\n\nProvide a concise response answering the user request based on the context above:"
        print("Executing Qwen 1.5B with Context Package...")
        response = gateway.generate(prompt=formatted_prompt)
        
        print("\n🤖 AGENT RESPONSE:")
        print(response)
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
