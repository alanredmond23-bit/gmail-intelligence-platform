"""IMAP client for email extraction."""

from typing import Optional


class IMAPClient:
    """IMAP client for connecting to email servers."""

    def __init__(self, host: str, port: int = 993, timeout: Optional[int] = None):
        """Initialize IMAP client.

        Args:
            host: IMAP server hostname
            port: IMAP port (default 993 for SSL)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect(self, email: str, password: str) -> bool:
        """Connect to IMAP server with credentials."""
        # TODO: Implement IMAP connection
        raise NotImplementedError

    def search(self, query: str) -> list[str]:
        """Search for emails matching query."""
        # TODO: Implement email search
        raise NotImplementedError

    def fetch_email(self, uid: str) -> dict:
        """Fetch full email message."""
        # TODO: Implement email fetching
        raise NotImplementedError
