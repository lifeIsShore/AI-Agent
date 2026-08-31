import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from personal_agent.models.gateway import ModelGateway

def main():
    gateway = ModelGateway(provider="ollama")
    
    email_content = "Dear Ahmet, the deadline for submitting your thesis proposal has been moved to tomorrow at 12:00."
    
    prompt = f"""You are a personal assistant. Read the following email and extract structured information.

Email:
"{email_content}"

Return a valid JSON object strictly matching this format, with no extra text:
{{
  "priority": "urgent|important|normal|irrelevant",
  "requires_response": true|false,
  "reason": "string",
  "suggested_action": "string",
  "draft_required": true|false
}}
"""
    
    print("Sending classification request to Qwen 1.5B...")
    response = gateway.generate(prompt=prompt, format="json")
    
    print("\nResult:")
    print(response)

if __name__ == "__main__":
    main()
