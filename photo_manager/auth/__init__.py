"""Authentication module for OneDrive and Google Photos."""

import os
import json
from pathlib import Path
from typing import Optional, Any
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from azure.identity import ClientSecretCredential, InteractiveBrowserCredential


class CredentialManager:
    """Manages credentials for both services."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize credential manager.
        
        Args:
            base_path: Path to store credentials. Defaults to ~/.photo-manager/credentials
        """
        if base_path is None:
            base_path = Path.home() / ".photo-manager" / "credentials"
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_google_credentials(self, credentials: Credentials) -> None:
        """Save Google Photos credentials."""
        cred_path = self.base_path / "google_photos.pickle"
        with open(cred_path, "wb") as f:
            pickle.dump(credentials, f)
    
    def load_google_credentials(self) -> Optional[Credentials]:
        """Load saved Google Photos credentials."""
        cred_path = self.base_path / "google_photos.pickle"
        if cred_path.exists():
            with open(cred_path, "rb") as f:
                return pickle.load(f)
        return None
    
    def save_onedrive_credentials(self, credentials: dict) -> None:
        """Save OneDrive credentials."""
        cred_path = self.base_path / "onedrive.json"
        with open(cred_path, "w") as f:
            json.dump(credentials, f, indent=2)
    
    def load_onedrive_credentials(self) -> Optional[dict]:
        """Load saved OneDrive credentials."""
        cred_path = self.base_path / "onedrive.json"
        if cred_path.exists():
            with open(cred_path, "r") as f:
                return json.load(f)
        return None


class GooglePhotosAuth:
    """Handle Google Photos OAuth 2.0 authentication."""
    
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
    
    def __init__(self, credentials_file: Optional[str] = None, cred_manager: Optional[CredentialManager] = None):
        """Initialize Google Photos auth.
        
        Args:
            credentials_file: Path to client_secret.json from Google Cloud Console
            cred_manager: CredentialManager for saving/loading credentials
        """
        self.credentials_file = credentials_file
        self.cred_manager = cred_manager or CredentialManager()
    
    def authenticate(self) -> Credentials:
        """Authenticate with Google Photos using OAuth 2.0.
        
        Returns:
            Authenticated Credentials object
        """
        # Try to load cached credentials first
        creds = self.cred_manager.load_google_credentials()
        
        if creds and creds.valid:
            return creds
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.cred_manager.save_google_credentials(creds)
            return creds
        
        # If no valid credentials, perform OAuth flow
        if not self.credentials_file:
            raise FileNotFoundError(
                "Google credentials file not found. "
                "Download client_secret.json from Google Cloud Console and pass its path."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES
        )
        creds = flow.run_local_server(port=8080)
        
        # Save for future use
        self.cred_manager.save_google_credentials(creds)
        return creds


class OneDriveAuth:
    """Handle OneDrive/SharePoint authentication."""
    
    def __init__(self, 
                 tenant_id: Optional[str] = None,
                 client_id: Optional[str] = None,
                 cred_manager: Optional[CredentialManager] = None):
        """Initialize OneDrive auth.
        
        Args:
            tenant_id: Azure tenant ID
            client_id: Azure app registration client ID
            cred_manager: CredentialManager for saving/loading credentials
        """
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.cred_manager = cred_manager or CredentialManager()
    
    def authenticate(self) -> Any:
        """Authenticate with OneDrive using interactive browser.
        
        Returns:
            Authenticated credential object
        """
        # For OneDrive, we can use interactive browser authentication
        # which handles the token refresh automatically
        credential = InteractiveBrowserCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id
        )
        return credential
