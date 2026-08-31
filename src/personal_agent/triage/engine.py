import json
from typing import Dict, Any, Tuple
from personal_agent.triage.signals import EmailSignals

class PriorityEngine:
    def __init__(self, gateway):
        self.gateway = gateway

    def evaluate(self, email_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Returns the final classification and a boolean indicating if the LLM was bypassed."""
        signals = EmailSignals(email_data)
        
        # 1. HIERARCHY TOP LEVEL: Confirmed Marketing -> IRRELEVANT
        if signals.get_marketing_score() >= 4:
            return {
                "priority": "irrelevant",
                "category": "marketing",
                "email_type": "marketing",
                "requires_action": False,
                "requires_response": False,
                "deadline": "none",
                "reason": "Deterministic rules identified this as promotional/marketing content.",
                "suggested_action": "None"
            }, True
            
        # 2. Extract facts via LLM
        extraction = self._extract_facts(email_data)
        
        # Merge deterministic signal classifications if extraction is unsure
        is_alert = signals.is_automated_alert() or extraction.get("email_type") == "automated_alert"
        is_trans = signals.is_transactional() or extraction.get("email_type") == "transactional"
        
        req_action = extraction.get("requires_action", False)
        deadline_token = str(extraction.get("deadline", "none")).lower().strip()
        
        final_priority = "normal"
        
        # 3. Apply Policy Rules
        if is_alert:
            # Automated alerts (e.g. LinkedIn job notifications) are NEVER URGENT
            # even if they say "apply today". They are at most NORMAL or IMPORTANT.
            if req_action and deadline_token in ["today", "tomorrow"]:
                final_priority = "normal"  # Job alerts are informational, not urgent
            else:
                final_priority = "normal"
                
        elif is_trans:
            # Transactional emails: check if it's a failure/declined notice vs routine info
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
  "deadline": "today|tomorrow|this_week|explicit_date|none",
  "email_type": "automated_alert|transactional|direct_communication|marketing|other",
  "category": "university|work|finance|personal|notification|other",
  "reason": "Brief summary of what the email is about and what is required.",
  "suggested_action": "Brief summary of action to take"
}}

IMPORTANT RULES:
- "automated_alert": Job alerts (LinkedIn, Indeed), system notifications, weekly digests, mailing list updates.
- "transactional": Receipts, payment updates, shipping notifications, invoices, account changes.
- "direct_communication": Emails from real individuals, professors, colleagues, direct personal requests.
- For deadline, if the email states an action must be done today or within 24 hours, output "today" or "tomorrow". Otherwise output "this_week", explicit date, or "none".
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
                "deadline": "none",
                "email_type": "other",
                "category": "other",
                "reason": f"Parsing failed: {str(e)}",
                "suggested_action": "None"
            }
