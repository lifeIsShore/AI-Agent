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
                "requires_planning": False,
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
        requires_planning = extraction.get("requires_planning", False)
        
        # 3. Apply Policy Rules based on email_type and action_type
        if email_type == "automated_alert" or signals.is_automated_alert() or email_type == "marketing":
            # Automated alerts & newsletters are NEVER planned on calendar
            final_priority = "normal"
            requires_planning = False
                
        elif email_type == "transactional" or signals.is_transactional():
            subj = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            if any(x in subj or x in body for x in ['declined', 'failed', 'action required', 'suspension', 'unauthorized', 'freeze']):
                final_priority = "urgent" if deadline_token in ["today", "tomorrow"] else "important"
                requires_planning = True
            else:
                final_priority = "normal"
                requires_planning = False
                
        else:
            # Direct communication / university / work task / personal
            if req_action:
                requires_planning = True
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
                requires_planning = False
                
        extraction["priority"] = final_priority
        extraction["requires_planning"] = requires_planning
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
  "requires_planning": true|false,
  "requires_response": true|false,
  "action_type": "reply|review|pay|schedule|attend|apply|purchase|none|other",
  "deadline": "today|tomorrow|this_week|explicit_date|none",
  "email_type": "automated_alert|transactional|direct_communication|marketing|other",
  "category": "university|work|finance|job_search|shopping|personal|service|notification|other",
  "reason": "Brief summary of what the email is about and what is required.",
  "suggested_action": "Brief summary of action to take"
}}

IMPORTANT DEFINITIONS:
- requires_planning: Set true ONLY if this email requires dedicated scheduled execution/work time on a daily calendar (e.g. professor request, thesis proposal, bank issue). Set false for job digests, impression reports, newsletters, receipts, or simple FYI alerts.
- email_type:
  * "automated_alert": Job alerts (LinkedIn, Indeed), system notifications, weekly digests.
  * "transactional": Receipts, payment updates, shipping notifications, invoices, account changes.
  * "direct_communication": Emails from real individuals, professors, colleagues, direct personal requests.
  * "marketing": Sales, discounts, promotional offers, newsletters.
"""
        try:
            response = self.gateway.generate(prompt=prompt, format="json")
            clean = response.strip()
            if clean.startswith("```json"): clean = clean[7:-3]
            elif clean.startswith("```"): clean = clean[3:-3]
            res = json.loads(clean.strip())
            if "requires_planning" not in res:
                res["requires_planning"] = res.get("requires_action", False) and res.get("email_type") == "direct_communication"
            return res
        except Exception as e:
            # Fallback heuristic extraction if LLM is offline
            subj = email_data.get('subject', '').lower()
            sender = email_data.get('sender', '').lower()
            
            is_univ = 'univ' in sender or 'university' in subj or 'edu' in sender
            is_thesis = 'thesis' in subj
            
            return {
                "requires_action": is_thesis or is_univ,
                "requires_planning": is_thesis or is_univ,
                "requires_response": is_thesis or is_univ,
                "action_type": "reply" if (is_thesis or is_univ) else "review",
                "deadline": "today" if is_thesis else ("this_week" if is_univ else "none"),
                "email_type": "direct_communication" if (is_thesis or is_univ) else "other",
                "category": "university" if is_univ else ("thesis" if is_thesis else "general"),
                "reason": f"Heuristic classification (LLM offline: {str(e)})",
                "suggested_action": "Reply to email" if (is_thesis or is_univ) else "Review email"
            }
