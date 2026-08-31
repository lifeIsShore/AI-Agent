import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.gmail import GmailTool
from personal_agent.triage.engine import PriorityEngine

def print_header(title):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"       {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    print_header("PERSONAL ASSISTANT (V0.3)")
    print("Initializing components...")
    
    gateway = ModelGateway(provider="ollama")
    engine = PriorityEngine(gateway)
    
    try:
        gmail_tool = GmailTool()
    except Exception as e:
        print(f"Failed to initialize Gmail tool. Did you set up credentials? Error: {e}")
        return
        
    print("Fetching recent emails...\n")
    # Fetch 15 emails for a safe batch size
    emails = gmail_tool.list_recent_emails(limit=15)
    
    if not emails:
        print("No emails found.")
        return
        
    print(f"Analyzing {len(emails)} emails with Hybrid Triage Pipeline...\n")
    
    results = []
    llm_calls = 0
    rule_bypasses = 0
    
    for i, email in enumerate(emails, 1):
        print(f"Processing email {i}/{len(emails)}...")
        analysis, bypassed = engine.evaluate(email)
        
        analysis['original_sender'] = email.get('sender', 'Unknown Sender')
        analysis['original_subject'] = email.get('subject', 'No Subject')
        analysis['bypassed'] = bypassed
        
        if bypassed:
            rule_bypasses += 1
        else:
            llm_calls += 1
            
        results.append(analysis)
        
    urgent = [d for d in results if d.get("priority") == "urgent"]
    important = [d for d in results if d.get("priority") == "important"]
    normal = [d for d in results if d.get("priority") == "normal"]
    irrelevant = [d for d in results if d.get("priority") == "irrelevant"]
    
    print("\n")
    print_header("📧 GMAIL REVIEW")
    
    print(f"🔴 URGENT — {len(urgent)} emails")
    print("──────────────────────────────")
    for item in urgent:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"Sender:  {item.get('original_sender')}")
        print(f"Subject: {item.get('original_subject')}")
        print(f"Action:  {item.get('suggested_action')} {byp_str}\n")
            
    print(f"🟡 IMPORTANT — {len(important)} emails")
    print("──────────────────────────────")
    for item in important:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"Sender:  {item.get('original_sender')}")
        print(f"Subject: {item.get('original_subject')}")
        print(f"Action:  {item.get('suggested_action')} {byp_str}\n")
            
    print(f"🟢 NORMAL — {len(normal)} emails")
    print("──────────────────────────────")
    for item in normal:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        # Minimal output for normal
        print(f"- {item.get('original_subject')} {byp_str}")
    print("\n")
        
    print(f"⚪ IRRELEVANT — {len(irrelevant)} emails")
    print("──────────────────────────────")
    for item in irrelevant:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        # Minimal output for irrelevant
        print(f"- {item.get('original_subject')} {byp_str}")
    print("\n")
    
    print(f"⏱ LLM calls: {llm_calls}")
    print(f"⚡ Rule bypasses: {rule_bypasses}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    main()
