from typing import Dict, Any

class EmailSignals:
    def __init__(self, email_data: Dict[str, Any]):
        self.email = email_data
        self.subject = email_data.get('subject', '').lower()
        self.sender = email_data.get('sender', '').lower()
        self.body = email_data.get('body', '').lower()

    def get_marketing_score(self) -> int:
        score = 0
        
        # Unsubscribe / automated marketing footers
        if any(x in self.body for x in ['unsubscribe', 'opt out', 'manage your preferences', 'view in browser', 'opt-out']):
            score += 2
            
        # Senders
        if any(x in self.sender for x in ['news@', 'marketing@', 'offers@', 'promotions@', 'deals@']):
            score += 2
            
        if 'newsletter' in self.sender or 'newsletter' in self.subject:
            score += 2
            
        # Promotional language in subject
        if any(x in self.subject for x in ['sale', '% off', 'discount', 'exclusive offer', 'free trial', 'last chance', 'fırsat']):
            score += 2
            
        # Bulk mailing headers/footers
        if 'mailing list' in self.body or ('sent to' in self.body and 'because you' in self.body):
            score += 1
            
        return score

    def is_automated_alert(self) -> bool:
        """Detect automated notification or alert senders (e.g. LinkedIn job alerts)."""
        alert_senders = ['jobalerts-noreply@linkedin.com', 'alert@', 'jobalerts', 'notifications@', 'no-reply@', 'noreply@']
        if any(x in self.sender for x in alert_senders):
            return True
        if any(x in self.subject for x in ['job alert', 'digest', 'weekly summary', 'new jobs for you']):
            return True
        return False

    def is_transactional(self) -> bool:
        """Detect receipts, order confirmations, security updates, payment updates."""
        transactional_keywords = ['payment method updated', 'order confirmed', 'sipariş', 'receipt', 'invoice', 'delivered', 'package']
        if any(x in self.subject for x in transactional_keywords) or any(x in self.body for x in transactional_keywords):
            return True
        return False
