from typing import List, Dict, Any

class InboxZeroEngine:
    def __init__(self):
        pass

    def evaluate_inbox(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyzes a list of emails and generates proposals for archiving, labeling, and drafting."""
        archive_proposals = []
        label_proposals = []
        draft_proposals = []
        
        for email in emails:
            msg_id = email.get("id")
            subject = email.get("subject", "No Subject")
            sender = email.get("sender", "Unknown")
            cat = email.get("category", "general")
            email_type = email.get("email_type", "other")
            prio = email.get("priority", "normal")
            req_resp = email.get("requires_response", False)

            # 1. Archive Proposals (Marketing, newsletters, old transactional notifications)
            if cat in ["marketing", "shopping", "notification"] or email_type in ["marketing", "automated_alert"]:
                archive_proposals.append({
                    "action": "archive_email",
                    "msg_id": msg_id,
                    "subject": subject,
                    "sender": sender,
                    "reason": f"Automated/promotional email ({cat}/{email_type})"
                })

            # 2. Label Proposals (University, Finance, Work)
            if cat in ["university", "work", "finance", "job_search"]:
                label_name = cat.capitalize()
                label_proposals.append({
                    "action": "apply_label",
                    "msg_id": msg_id,
                    "subject": subject,
                    "label_name": label_name,
                    "reason": f"Categorized as {label_name}"
                })

            # 3. Draft Proposals (Urgent/Important emails requiring response)
            if req_resp and prio in ["urgent", "important"]:
                draft_proposals.append({
                    "action": "create_draft",
                    "to": sender,
                    "subject": f"Re: {subject}",
                    "thread_id": email.get("thread_id"),
                    "suggested_body": f"Hi,\n\nThank you for reaching out regarding '{subject}'. I am reviewing this and will get back to you shortly.\n\nBest regards,\nAhmet",
                    "reason": f"Urgent/Important response required for {prio} email"
                })

        summary = f"Scanned {len(emails)} emails. Generated {len(archive_proposals)} archive proposals, {len(label_proposals)} label proposals, and {len(draft_proposals)} draft reply proposals."

        return {
            "summary": summary,
            "archive_proposals": archive_proposals,
            "label_proposals": label_proposals,
            "draft_proposals": draft_proposals,
            "total_proposals_count": len(archive_proposals) + len(label_proposals) + len(draft_proposals)
        }
