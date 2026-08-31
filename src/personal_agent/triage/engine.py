import json
from typing import Dict, Any, Tuple
from personal_agent.triage.signals import EmailSignals

class PriorityEngine:
    def __init__(self, gateway):
        self.gateway = gateway

    def evaluate(self, email_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Returns the final classification object and a boolean indicating if the LLM was bypassed."""
        signals = EmailSignals(email_data)
        
        # 1. HIERARCHY TOP LEVEL: Confirmed Marketing -> IRRELEVANT
        if signals.get_marketing_score() >= 4:
            return {
                "priority": "irrelevant",
                "email_type": "marketing",
                "category": "marketing",
                "action_type": "none",
                "requires_action": False,
                "requires_response": False,
                "deadline": "none",
                "reason": "Deterministic rules identified this as promotional/marketing content.",
                "suggested_action": "None"
            }, True
            
        # 2. Extract facts via LLM
        extraction = self._extract_facts(email_data)
        
        # Overwrite with deterministic signal flags if LLM was unsure
        if signals.is_automated_alert() and extraction.get("email_type") == "other":
            extraction["email_type"] = "automated_alert"
        if signals.is_transactional() and extraction.get("email_type") == "other":
            extraction["email_type"] = "transactional"
            
        email_type = extraction.get("email_type", "other")
        req_action = extraction.get("requires_action", False)
        deadline_token = str(extraction.get("deadline", "none")).lower().strip()
        
        final_priority = "normal"
        
        # 3. Apply Policy Rules based on email_type and action_type
        if email_type == "automated_alert" or signals.is_automated_alert():
            # Automated alerts (e.g. LinkedIn job alerts) are NEVER URGENT
            final_priority = "normal"
                
        elif email_type == "transactional" or signals.is_transactional():
            subj = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            if any(x in subj or x in body for x in ['declined', 'failed', 'action required', 'suspension', 'unauthorized', 'freeze']):
                final_priority = "urgent" if deadline_token in ["today", "tomorrow"] else "important"
            else:
                final_priority = "normal"
                
        else:
            # Direct communication / university / work task / personal
            if req_action:
                if deadline_token in ["today", "tomorrow", "24 hours", "24h"]:
                    final_priority = "urgent"
                elif deadline_token in ["this_week", "this week"]:
                    final_priority = "important"
                elif deadline_token != "none" and deadline_token != "null":
                    final_priority = "important"
                else:
                    final_priority = "important"
            else:
                final_priority = "normal"
                
        extraction["priority"] = final_priority
        return extraction, False

    def _extract_facts(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""You are an email fact extractor.
Read the email and extract the requested facts. Do NOT determine priority.

Email:
Subject: {email_data.get('subject')}
Sender: {email_data.get('sender')}
Body: {email_data.get('body')}

Return ONLY valid JSON matching exactly this format:
{{
  "requires_action": true|false,
  "requires_response": true|false,
  "action_type": "reply|review|pay|schedule|attend|apply|purchase|none|other",
  "deadline": "today|tomorrow|this_week|explicit_date|none",
  "email_type": "automated_alert|transactional|direct_communication|marketing|other",
  "category": "university|work|finance|job_search|shopping|personal|service|notification|other",
  "reason": "Brief summary of what the email is about and what is required.",
  "suggested_action": "Brief summary of action to take"
}}

IMPORTANT DEFINITIONS:
- email_type:
  * "automated_alert": Job alerts (LinkedIn, Indeed), system notifications, weekly digests.
  * "transactional": Receipts, payment updates, shipping notifications, invoices, account changes.
  * "direct_communication": Emails from real individuals, professors, colleagues, direct personal requests.
  * "marketing": Sales, discounts, promotional offers, newsletters.

- action_type:
  * "reply": Sender expects a written reply.
  * "review": Sender expects you to review a document, code PR, or job post.
  * "pay": Sender expects a payment or bill settlement.
  * "schedule": Sender wants to schedule a meeting or appointment.
  * "attend": Invitation to an event, lecture, or webinar.
  * "apply": Invitation or link to apply for a job or program.
  * "purchase": Call to buy something.
  * "none": No action required.
  * "other": Any other action.
"""
        response = self.gateway.generate(prompt=prompt, format="json")
        try:
            clean = response.strip()
            if clean.startswith("```json"): clean = clean[7:-3]
            elif clean.startswith("```"): clean = clean[3:-3]
            return json.loads(clean.strip())
        except Exception as e:
            return {
                "requires_action": False,
                "requires_response": False,
                "action_type": "none",
                "deadline": "none",
                "email_type": "other",
                "category": "other",
                "reason": f"Parsing failed: {str(e)}",
                "suggested_action": "None"
            }
