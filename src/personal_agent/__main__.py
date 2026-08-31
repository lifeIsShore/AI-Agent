import sys
import os
import time
from collections import Counter

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
    print_header("PERSONAL ASSISTANT (V0.3.3)")
    print("Initializing components...")
    
    gateway = ModelGateway(provider="ollama")
    engine = PriorityEngine(gateway)
    
    try:
        gmail_tool = GmailTool()
    except Exception as e:
        print(f"Failed to initialize Gmail tool. Did you set up credentials? Error: {e}")
        return
        
    print("Fetching recent emails...\n")
    # Fetch 30 emails for a comprehensive evaluation
    emails = gmail_tool.list_recent_emails(limit=30)
    
    if not emails:
        print("No emails found.")
        return
        
    print(f"Analyzing {len(emails)} emails with V0.3.3 Schema Pipeline...\n")
    
    results = []
    llm_calls = 0
    rule_bypasses = 0
    
    categories = Counter()
    action_types = Counter()
    email_types = Counter()
    
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
            
        categories[analysis.get('category', 'other')] += 1
        action_types[analysis.get('action_type', 'none')] += 1
        email_types[analysis.get('email_type', 'other')] += 1
        
        results.append(analysis)
        
    urgent = [d for d in results if d.get("priority") == "urgent"]
    important = [d for d in results if d.get("priority") == "important"]
    normal = [d for d in results if d.get("priority") == "normal"]
    irrelevant = [d for d in results if d.get("priority") == "irrelevant"]
    
    print("\n")
    print_header("📧 GMAIL REVIEW & EVALUATION REPORT")
    
    print(f"🔴 URGENT — {len(urgent)} emails")
    print("──────────────────────────────")
    for item in urgent:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"Sender:  {item.get('original_sender')}")
        print(f"Subject: {item.get('original_subject')}")
        print(f"Type:    {item.get('email_type')} | Category: {item.get('category')} | Action: {item.get('action_type')}")
        print(f"Detail:  {item.get('suggested_action')} {byp_str}\n")
            
    print(f"🟡 IMPORTANT — {len(important)} emails")
    print("──────────────────────────────")
    for item in important:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"Sender:  {item.get('original_sender')}")
        print(f"Subject: {item.get('original_subject')}")
        print(f"Type:    {item.get('email_type')} | Category: {item.get('category')} | Action: {item.get('action_type')}")
        print(f"Detail:  {item.get('suggested_action')} {byp_str}\n")
            
    print(f"🟢 NORMAL — {len(normal)} emails")
    print("──────────────────────────────")
    for item in normal[:5]: # Show top 5 normal
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"- [{item.get('category')}/{item.get('action_type')}] {item.get('original_subject')} {byp_str}")
    if len(normal) > 5:
        print(f"  ... and {len(normal) - 5} more normal emails.")
    print("\n")
        
    print(f"⚪ IRRELEVANT — {len(irrelevant)} emails")
    print("──────────────────────────────")
    for item in irrelevant[:5]:
        byp_str = "[Rules]" if item.get('bypassed') else "[LLM]"
        print(f"- [{item.get('category')}] {item.get('original_subject')} {byp_str}")
    if len(irrelevant) > 5:
        print(f"  ... and {len(irrelevant) - 5} more irrelevant emails.")
    print("\n")
    
    print_header("📊 STATISTICAL METRICS")
    total_emails = len(results)
    print(f"Total Emails Analyzed: {total_emails}")
    print(f"⏱ LLM Calls:          {llm_calls}")
    print(f"⚡ Rule Bypasses:      {rule_bypasses} ({rule_bypasses/total_emails*100:.1f}%)")
    print(f"❓ 'Other' Category:   {categories['other']} ({categories['other']/total_emails*100:.1f}%)")
    
    print("\nCategory Breakdown:")
    for cat, count in categories.most_common():
        print(f"  - {cat:<15}: {count}")
        
    print("\nAction Type Breakdown:")
    for act, count in action_types.most_common():
        print(f"  - {act:<15}: {count}")
        
    print("\nEmail Type Breakdown:")
    for et, count in email_types.most_common():
        print(f"  - {et:<15}: {count}")
        
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    main()
