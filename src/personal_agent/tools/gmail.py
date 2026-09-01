import os
import json
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from personal_agent.tools.auth import GoogleAuthManager

GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailTool:
    def __init__(self, service: Optional[Any] = None, auth_manager: Optional[GoogleAuthManager] = None):
        if service:
            self.service = service
        else:
            self.auth_manager = auth_manager or GoogleAuthManager()
            try:
                self.service = self.auth_manager.build_service('gmail', 'v1', scopes=GMAIL_SCOPES)
            except Exception as e:
                print(f"[GmailTool] Could not initialize live Gmail service: {e}")
                self.service = None

    def list_recent_emails(self, limit: int = 10, label_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not self.service:
            return []

        labels = label_ids or ['INBOX']
        try:
            results = self.service.users().messages().list(userId='me', labelIds=labels, maxResults=limit).execute()
            messages = results.get('messages', [])

            normalized_emails = []
            for msg in messages:
                msg_data = self._get_email_details(msg['id'])
                if msg_data:
                    normalized_emails.append(msg_data)
                    
            return normalized_emails
        except Exception as e:
            print(f"[GmailTool] Error fetching emails: {e}")
            return []

    def get_email_details(self, msg_id: str) -> Dict[str, Any]:
        return self._get_email_details(msg_id)

    def archive_email(self, msg_id: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return {"status": "success", "action": "archive", "msg_id": msg_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def trash_email(self, msg_id: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            self.service.users().messages().trash(userId='me', id=msg_id).execute()
            return {"status": "success", "action": "trash", "msg_id": msg_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def mark_read(self, msg_id: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return {"status": "success", "action": "mark_read", "msg_id": msg_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def mark_unread(self, msg_id: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return {"status": "success", "action": "mark_unread", "msg_id": msg_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def apply_label(self, msg_id: str, label_name: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            label_id = self._get_or_create_label_id(label_name)
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return {"status": "success", "action": "apply_label", "msg_id": msg_id, "label": label_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def create_label(self, label_name: str) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            label_id = self._get_or_create_label_id(label_name)
            return {"status": "success", "action": "create_label", "label_id": label_id, "label_name": label_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def create_draft(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Gmail service unavailable"}

        try:
            mime_msg = MIMEText(body)
            mime_msg['to'] = to
            mime_msg['subject'] = subject
            raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()

            message_body: Dict[str, Any] = {'raw': raw}
            if thread_id:
                message_body['threadId'] = thread_id

            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message_body}
            ).execute()

            return {
                "status": "success",
                "draft_id": draft.get('id'),
                "to": to,
                "subject": subject
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_or_create_label_id(self, label_name: str) -> str:
        # Fetch existing labels
        labels_result = self.service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        for lbl in labels:
            if lbl.get('name', '').lower() == label_name.lower():
                return lbl.get('id')

        # Create new label if not found
        new_lbl = self.service.users().labels().create(
            userId='me',
            body={'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        ).execute()
        return new_lbl.get('id')

    def _get_email_details(self, msg_id: str) -> Dict[str, Any]:
        if not self.service:
            return {}

        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), "No Subject")
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), "Unknown Sender")
            date = next((header['value'] for header in headers if header['name'].lower() == 'date'), "Unknown Date")
            
            body = self._extract_body(payload)
            labels = message.get('labelIds', [])
            is_unread = 'UNREAD' in labels
            
            return {
                "id": message.get("id"),
                "thread_id": message.get("threadId"),
                "sender": sender,
                "subject": subject,
                "date": date,
                "snippet": message.get("snippet", ""),
                "body": body[:500] + "..." if len(body) > 500 else body,
                "unread": is_unread,
                "labels": labels
            }
        except Exception as e:
            print(f"[GmailTool] Error getting details for message {msg_id}: {e}")
            return {}

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    body += self._extract_body(part)
        else:
            data = payload.get('body', {}).get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
        return body.strip()

# Wrappers for Tool Registry
def read_recent_emails(limit: int = 10) -> str:
    """Read recent emails from Gmail inbox."""
    tool = GmailTool()
    emails = tool.list_recent_emails(limit=limit)
    return json.dumps(emails, indent=2)

def archive_email(msg_id: str) -> str:
    """Archive an email by removing it from INBOX."""
    tool = GmailTool()
    res = tool.archive_email(msg_id=msg_id)
    return json.dumps(res, indent=2)

def trash_email(msg_id: str) -> str:
    """Move an email to trash."""
    tool = GmailTool()
    res = tool.trash_email(msg_id=msg_id)
    return json.dumps(res, indent=2)

def mark_read(msg_id: str) -> str:
    """Mark an email as read."""
    tool = GmailTool()
    res = tool.mark_read(msg_id=msg_id)
    return json.dumps(res, indent=2)

def apply_label(msg_id: str, label_name: str) -> str:
    """Apply a label to an email message."""
    tool = GmailTool()
    res = tool.apply_label(msg_id=msg_id, label_name=label_name)
    return json.dumps(res, indent=2)

def create_draft(to: str, subject: str, body: str, thread_id: Optional[str] = None) -> str:
    """Create an email reply/draft."""
    tool = GmailTool()
    res = tool.create_draft(to=to, subject=subject, body=body, thread_id=thread_id)
    return json.dumps(res, indent=2)
