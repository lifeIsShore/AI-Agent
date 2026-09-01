import json
from typing import Dict, Any, Tuple

class MemoryPolicy:
    def __init__(self, gateway):
        self.gateway = gateway

    def evaluate_candidate(self, text: str, source: str = "user") -> Tuple[bool, Dict[str, Any]]:
        """Evaluates whether candidate text is worth storing as a long-term memory."""
        text_lower = text.lower()
        
        # 1. Deterministic Rejections (Transient Events)
        transient_signals = ["unavailable", "out of office", "meeting at", "appointment", "this friday", "tomorrow at"]
        if any(x in text_lower for x in transient_signals):
            return False, {
                "should_store": False,
                "reason": "Deterministic signal detected a temporary event or calendar appointment."
            }
            
        # 2. Deterministic Acceptances (Preferences / People / Goals)
        if any(x in text_lower for x in ["prefer", "always", "never", "like to", "dislike"]):
            return True, {
                "should_store": True,
                "memory_type": "preference",
                "content": text,
                "importance": "high",
                "reason": "Deterministic match for user preference."
            }
            
        if any(x in text_lower for x in ["goal", "thesis", "target", "aim to"]):
            return True, {
                "should_store": True,
                "memory_type": "goal",
                "content": text,
                "importance": "high",
                "reason": "Deterministic match for personal goal."
            }
            
        if any(x in text_lower for x in ["advisor", "boss", "manager", "professor", "supervisor"]):
            return True, {
                "should_store": True,
                "memory_type": "important_person",
                "content": text,
                "importance": "medium",
                "reason": "Deterministic match for key contact."
            }

        # 3. LLM Fallback for ambiguous text
        prompt = f"""You are a Personal Memory Policy Evaluator.
Analyze the statement: "{text}"

Is this statement a long-term personal preference, goal, key decision, or important person fact?
Or is it a temporary operational update?

Return ONLY valid JSON matching this format:
{{
  "should_store": true|false,
  "memory_type": "goal|preference|important_person|decision|other",
  "content": "{text}",
  "importance": "low|medium|high",
  "reason": "Brief explanation"
}}
"""
        try:
            response = self.gateway.generate(prompt=prompt, format="json")
            clean = response.strip()
            if clean.startswith("```json"): clean = clean[7:-3]
            elif clean.startswith("```"): clean = clean[3:-3]
            data = json.loads(clean.strip())
            return data.get("should_store", False), data
        except Exception as e:
            return False, {"should_store": False, "reason": f"Evaluation error: {e}"}
