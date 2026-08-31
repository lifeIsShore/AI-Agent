import json

class EmailClassifier:
    def __init__(self, gateway):
        self.gateway = gateway

    def _get_deterministic_flags(self, email_data):
        flags = []
        sender = email_data.get('sender', '').lower()
        body = email_data.get('body', '').lower()
        subject = email_data.get('subject', '').lower()

        if 'noreply' in sender or 'no-reply' in sender or 'news@' in sender or 'marketing' in sender or 'newsletter' in sender:
            flags.append("Sender appears to be an automated system, newsletter, or marketing list.")
        
        if 'unsubscribe' in body or 'view in browser' in body:
            flags.append("Email contains an unsubscribe link (likely a newsletter or promotional material).")
            
        if 'urgent' in subject or 'action required' in subject:
            flags.append("Subject explicitly mentions urgent or action required.")
            
        return flags

    def classify(self, email_data):
        flags = self._get_deterministic_flags(email_data)
        
        context_hints = ""
        if flags:
            context_hints = "DETERMINISTIC SYSTEM FLAGS (Highly Reliable):\n" + "\n".join([f"- {flag}" for flag in flags]) + "\n\n(Take these flags into heavy account when determining priority.)\n"

        prompt = f"""You are an email triage classifier.

Your job is NOT to be overly cautious.
Most emails are NOT urgent.

URGENT:
Only use urgent when:
- action is required within 24 hours, OR
- a missed response could cause serious consequences, OR
- the sender explicitly indicates an immediate deadline.

IMPORTANT:
Use important when:
- a response/action is needed but not immediately,
- it relates to university, work, finances, appointments,
- or it is personally relevant.

NORMAL:
Use normal when:
- the email contains useful information,
- but no action is currently required.

IRRELEVANT:
Use irrelevant for:
- newsletters,
- advertisements,
- promotional messages,
- generic announcements,
- automated notifications that require no action.

IMPORTANT RULES:
Do not classify an email as urgent merely because it mentions:
- university
- deadlines
- meetings
- important people
- words such as "please"

When uncertain between urgent and important, choose important.
When uncertain between important and normal, choose normal.
When uncertain between normal and irrelevant, choose irrelevant.

{context_hints}
Email to Classify:
Subject: {email_data.get('subject')}
Sender: {email_data.get('sender')}
Body: {email_data.get('body')}

Return ONLY valid JSON matching exactly this format:
{{
  "requires_action": true|false,
  "requires_response": true|false,
  "deadline": "YYYY-MM-DDTHH:MM:SS or null",
  "priority": "urgent|important|normal|irrelevant",
  "category": "university|work|finance|personal|marketing|other",
  "reason": "string",
  "suggested_action": "string"
}}
"""
        response = self.gateway.generate(prompt=prompt, format="json")
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:-3]
                
            return json.loads(clean_response.strip())
        except Exception as e:
            return {
                "requires_action": False,
                "requires_response": False,
                "deadline": None,
                "priority": "normal",
                "category": "other",
                "reason": f"Parsing failed: {str(e)}",
                "suggested_action": "None"
            }
