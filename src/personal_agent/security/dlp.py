from typing import List, Dict, Any, Tuple
from personal_agent.security.classification import DataClassifier, SENSITIVITY_HIGHLY_SENSITIVE

class DataLossPreventionEngine:
    def __init__(self, classifier: DataClassifier = None):
        self.classifier = classifier or DataClassifier()

    def sanitize_context_payload(self, context_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Filters or redacts HIGHLY_SENSITIVE data from LLM context payloads.
        Returns sanitized context list and count of blocked sensitive data items.
        """
        sanitized_list = []
        blocked_count = 0

        for item in context_items:
            content_str = str(item.get("body", item.get("subject", item.get("content", ""))))
            sensitivity = self.classifier.classify_sensitivity(content_str, category=str(item.get("category", "")))
            item["sensitivity"] = sensitivity

            if sensitivity == SENSITIVITY_HIGHLY_SENSITIVE:
                blocked_count += 1
                # Redact body text
                item_copy = dict(item)
                item_copy["body"] = "[REDACTED_HIGHLY_SENSITIVE_DATA_DLP_BLOCKED]"
                item_copy["subject"] = "[REDACTED_HIGHLY_SENSITIVE_SUBJECT]"
                sanitized_list.append(item_copy)
            else:
                sanitized_list.append(item)

        return sanitized_list, blocked_count
