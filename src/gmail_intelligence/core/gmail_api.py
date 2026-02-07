"""Gmail API client for OAuth2 authentication and email access."""

import os
import json
import pickle
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.gapic_v1 import client_info as grpc_client_info
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAPIClient:
    """Gmail API client with OAuth2 authentication.

    Provides methods for:
    - OAuth2 authentication and token management
    - Fetching emails with pagination
    - Managing labels
    - Accessing Gmail History API for incremental sync
    """

    # Gmail API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """Initialize Gmail API client.

        Args:
            credentials_path: Path to OAuth2 credentials JSON from Google Cloud Console
            token_path: Path to store cached OAuth2 token
            client_id: Google OAuth2 client ID (optional, can be in credentials file)
            client_secret: Google OAuth2 client secret (optional, can be in credentials file)

        Environment Variables:
            GMAIL_CREDENTIALS_FILE: Path to credentials JSON
            GMAIL_TOKEN_FILE: Path to token cache
            GMAIL_CLIENT_ID: OAuth2 client ID
            GMAIL_CLIENT_SECRET: OAuth2 client secret

        Note:
            First call to authenticate() will open browser for consent screen.
            Subsequent calls use cached token from token_path.
        """
        self.credentials_path = Path(
            credentials_path or os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
        ).expanduser()

        self.token_path = Path(
            token_path or os.getenv("GMAIL_TOKEN_FILE", "token.json")
        ).expanduser()

        self.client_id = client_id or os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GMAIL_CLIENT_SECRET")

        self.credentials: Optional[Credentials] = None
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with Gmail API.

        Uses OAuth2 flow with browser-based consent.
        Token is cached to avoid re-authentication.

        Returns:
            True if authentication successful

        Raises:
            FileNotFoundError: If credentials.json not found
            Exception: If authentication fails
        """
        try:
            # Try to load cached token first
            if self.token_path.exists():
                with open(self.token_path, "rb") as f:
                    self.credentials = pickle.load(f)

                # Refresh if expired
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_token()

                self.service = build("gmail", "v1", credentials=self.credentials)
                return True

            # If no cached token, need credentials file for OAuth2 flow
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    f"Credentials file not found at {self.credentials_path}. "
                    "Get credentials from Google Cloud Console > OAuth 2.0 ID > Download JSON"
                )

            # Run OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), self.SCOPES
            )

            self.credentials = flow.run_local_server(port=0)

            # Save token for next time
            self._save_token()

            self.service = build("gmail", "v1", credentials=self.credentials)
            return True

        except Exception as e:
            raise RuntimeError(f"Gmail authentication failed: {e}")

    def _save_token(self):
        """Save credentials to token cache."""
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "wb") as f:
                pickle.dump(self.credentials, f)
        except Exception as e:
            raise RuntimeError(f"Failed to save token: {e}")

    def get_messages(
        self,
        query: str = "",
        max_results: int = 10,
        page_token: Optional[str] = None,
    ) -> tuple[list[dict], Optional[str]]:
        """Get messages matching query.

        Args:
            query: Gmail search query (e.g., "from:john@example.com subject:contract")
            max_results: Max messages per page (1-500, default 10)
            page_token: Token for pagination

        Returns:
            Tuple of (messages list, next_page_token)

        Example:
            >>> messages, next_token = client.get_messages(
            ...     query="from:lawyer@firm.com",
            ...     max_results=50
            ... )
            >>> print(f"Got {len(messages)} messages")

        Raises:
            RuntimeError: If API call fails
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=min(max_results, 500),
                pageToken=page_token,
            ).execute()

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")

            return messages, next_page_token

        except HttpError as e:
            raise RuntimeError(f"Failed to get messages: {e}")

    def get_message(self, message_id: str, format: str = "full") -> Optional[dict]:
        """Get full message by ID.

        Args:
            message_id: Gmail message ID
            format: "full" (default), "raw", or "minimal"

        Returns:
            Message dict or None

        Example:
            >>> msg = client.get_message("abc123def456")
            >>> print(msg['payload']['headers'])

        Raises:
            RuntimeError: If API call fails
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format=format,
            ).execute()

            return message

        except HttpError as e:
            raise RuntimeError(f"Failed to get message {message_id}: {e}")

    def batch_get_messages(self, message_ids: list[str]) -> list[dict]:
        """Fetch multiple messages efficiently.

        Args:
            message_ids: List of Gmail message IDs

        Returns:
            List of message dicts

        Example:
            >>> ids = ["msg1", "msg2", "msg3"]
            >>> messages = client.batch_get_messages(ids)
        """
        batch = self.service.new_batch_http_request()
        messages = []

        def callback(request_id, response, exception):
            if exception:
                print(f"Error fetching message {request_id}: {exception}")
            else:
                messages.append(response)

        for msg_id in message_ids:
            batch.add(
                self.service.users().messages().get(
                    userId="me",
                    id=msg_id,
                    format="full",
                ),
                callback=callback,
            )

        batch.execute()
        return messages

    def create_label(self, label_name: str) -> str:
        """Create new Gmail label.

        Args:
            label_name: Label name (e.g., "LEGAL 2026" or "Legal/Bankruptcy")

        Returns:
            Label ID

        Example:
            >>> label_id = client.create_label("Legal/Discovery")

        Raises:
            RuntimeError: If creation fails or label exists
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            label_body = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }

            created_label = self.service.users().labels().create(
                userId="me",
                body=label_body,
            ).execute()

            return created_label["id"]

        except HttpError as e:
            if "already exists" in str(e):
                # Get ID of existing label
                return self.get_label_id(label_name)
            raise RuntimeError(f"Failed to create label: {e}")

    def get_label_id(self, label_name: str) -> Optional[str]:
        """Get label ID by name.

        Args:
            label_name: Label name to find

        Returns:
            Label ID or None if not found
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            for label in labels:
                if label["name"] == label_name:
                    return label["id"]

            return None

        except HttpError as e:
            raise RuntimeError(f"Failed to get label ID: {e}")

    def apply_label(self, message_id: str, label_id: str) -> bool:
        """Apply label to message.

        Args:
            message_id: Gmail message ID
            label_id: Label ID to apply

        Returns:
            True if successful

        Example:
            >>> label_id = client.create_label("Legal/Bankruptcy")
            >>> client.apply_label("msg123", label_id)
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"addLabelIds": [label_id]},
            ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to apply label: {e}")

    def remove_label(self, message_id: str, label_id: str) -> bool:
        """Remove label from message.

        Args:
            message_id: Gmail message ID
            label_id: Label ID to remove

        Returns:
            True if successful
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": [label_id]},
            ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to remove label: {e}")

    def get_history(
        self,
        start_history_id: str,
        max_results: int = 100,
    ) -> tuple[list[dict], Optional[str]]:
        """Get message changes using Gmail History API.

        Used for incremental sync instead of fetching all emails.

        Args:
            start_history_id: History ID to start from
            max_results: Max results per page (1-1000)

        Returns:
            Tuple of (history list, next_history_id)

        Example:
            >>> history, next_id = client.get_history("12345")
            >>> for event in history:
            ...     if "messagesAdded" in event:
            ...         print(f"New message: {event['messagesAdded']}")
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            results = self.service.users().history().list(
                userId="me",
                startHistoryId=start_history_id,
                maxResults=max_results,
            ).execute()

            history = results.get("history", [])
            next_history_id = results.get("historyId")

            return history, next_history_id

        except HttpError as e:
            raise RuntimeError(f"Failed to get history: {e}")

    def get_profile(self) -> dict:
        """Get authenticated user's Gmail profile.

        Returns:
            Profile dict with emailAddress, messagesTotal, threadsTotal, etc.

        Example:
            >>> profile = client.get_profile()
            >>> print(f"Email: {profile['emailAddress']}")
            >>> print(f"Total messages: {profile['messagesTotal']}")
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            profile = self.service.users().getProfile(userId="me").execute()
            return profile

        except HttpError as e:
            raise RuntimeError(f"Failed to get profile: {e}")

    def is_authenticated(self) -> bool:
        """Check if client is authenticated and service is ready.

        Returns:
            True if authenticated
        """
        return self.service is not None and self.credentials is not None
