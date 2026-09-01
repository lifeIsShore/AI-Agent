import os
import json
from typing import List, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ALL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

class GoogleAuthManager:
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path

    def get_credentials(self, scopes: Optional[List[str]] = None) -> Optional[Credentials]:
        target_scopes = scopes or ALL_SCOPES
        creds = None
        
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, target_scopes)
            except Exception as e:
                print(f"[GoogleAuth] Failed to load credentials from token path: {e}")
                creds = None
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[GoogleAuth] Token refresh failed: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_path):
                    print(f"[GoogleAuth] Credentials file not found at {self.credentials_path}")
                    return None
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, target_scopes)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"[GoogleAuth] OAuth flow failed or non-interactive: {e}")
                    return None

            if creds:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())

        return creds

    def build_service(self, service_name: str, version: str, scopes: Optional[List[str]] = None) -> Any:
        creds = self.get_credentials(scopes=scopes)
        if not creds:
            raise RuntimeError(f"Could not obtain valid Google credentials for service {service_name}.")
        return build(service_name, version, credentials=creds)
