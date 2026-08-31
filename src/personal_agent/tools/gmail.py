import os
import json
import base64
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailTool:
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def list_recent_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=limit).execute()
            messages = results.get('messages', [])

            normalized_emails = []
            for msg in messages:
                msg_data = self._get_email_details(msg['id'])
                if msg_data:
                    normalized_emails.append(msg_data)
                    
            return normalized_emails
        except Exception as e:
            print(f"An error occurred while fetching emails: {e}")
            return []

    def _get_email_details(self, msg_id: str) -> Dict[str, Any]:
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
                "body": body[:500] + "..." if len(body) > 500 else body, # Truncate to save tokens
                "unread": is_unread
            }
        except Exception as e:
            print(f"Error getting details for message {msg_id}: {e}")
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

def read_recent_emails(limit: int = 10) -> str:
    """Read recent emails from the user's Gmail inbox. Returns a JSON string of normalized emails."""
    tool = GmailTool()
    emails = tool.list_recent_emails(limit=limit)
    return json.dumps(emails, indent=2)
