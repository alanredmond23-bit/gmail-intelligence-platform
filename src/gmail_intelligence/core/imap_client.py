"""IMAP client for direct email server access."""

import imaplib
import email
from typing import Optional, list
from email.message import Message


class IMAPClient:
    """IMAP client for connecting to Gmail via IMAP.

    Provides methods for:
    - IMAP server connection and authentication
    - Email search using IMAP syntax
    - Fetching individual emails
    - Folder/label listing
    - UID-based operations
    """

    def __init__(
        self,
        host: str = "imap.gmail.com",
        port: int = 993,
        timeout: Optional[int] = 30,
    ):
        """Initialize IMAP client.

        Args:
            host: IMAP server hostname (default: imap.gmail.com)
            port: IMAP port (default: 993 for SSL)
            timeout: Connection timeout in seconds

        Example:
            >>> client = IMAPClient()
            >>> client.connect("your-email@gmail.com", "app-password")
            >>> emails = client.search("from:john@example.com")
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.imap = None
        self.email_address = None

    def connect(self, email_address: str, password: str) -> bool:
        """Connect to IMAP server.

        Args:
            email_address: Gmail email address
            password: Gmail password or app-specific password

        Returns:
            True if connection successful

        Raises:
            RuntimeError: If connection fails

        Note:
            For Gmail, use an app-specific password if 2FA is enabled.
            Generate at: https://myaccount.google.com/apppasswords
        """
        try:
            self.imap = imaplib.IMAP4_SSL(self.host, self.port, timeout=self.timeout)
            status, response = self.imap.login(email_address, password)

            if status == "OK":
                self.email_address = email_address
                return True
            else:
                raise RuntimeError(f"Login failed: {response}")

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"IMAP connection failed: {e}")

    def disconnect(self) -> bool:
        """Disconnect from IMAP server."""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                return True
            except Exception:
                pass
        return False

    def list_folders(self) -> list[str]:
        """List all folders (labels) in Gmail.

        Returns:
            List of folder names

        Example:
            >>> folders = client.list_folders()
            >>> print(folders)
            ['INBOX', 'Drafts', 'Sent Mail', 'Spam', ...]
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, mailboxes = self.imap.list()
            folders = []

            for mailbox in mailboxes:
                # Parse mailbox name from response
                # Format: (flags) "/" name or (flags) "delimiter" name
                if isinstance(mailbox, bytes):
                    mailbox = mailbox.decode("utf-8", errors="ignore")

                # Extract folder name (last part after quotes)
                parts = mailbox.rsplit('"', 1)
                if len(parts) == 2:
                    folder = parts[1].strip()
                    folders.append(folder)

            return folders

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to list folders: {e}")

    def select_folder(self, folder_name: str = "INBOX") -> bool:
        """Select a folder to work with.

        Args:
            folder_name: Folder name to select (default: INBOX)

        Returns:
            True if successful

        Raises:
            RuntimeError: If folder doesn't exist
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.select(folder_name)
            return status == "OK"

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to select folder '{folder_name}': {e}")

    def search(self, query: str) -> list[str]:
        """Search for emails in current folder using IMAP syntax.

        Args:
            query: IMAP search query

        Returns:
            List of email UIDs

        Example:
            >>> client.select_folder("INBOX")
            >>> uids = client.search('FROM "john@example.com"')
            >>> uids = client.search('SUBJECT "contract"')
            >>> uids = client.search('SINCE 01-Jan-2026')
            >>> uids = client.search('ALL')  # All emails

        Raises:
            RuntimeError: If search fails
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.search(None, query)

            if status == "OK":
                uid_list = response[0].decode("utf-8").split()
                return uid_list
            else:
                raise RuntimeError(f"Search failed: {response}")

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Search error: {e}")

    def fetch_email(self, uid: str) -> Optional[Message]:
        """Fetch full email message by UID.

        Args:
            uid: Email UID from search results

        Returns:
            email.Message object or None

        Example:
            >>> msg = client.fetch_email("12345")
            >>> print(msg['From'])
            >>> print(msg['Subject'])
            >>> print(msg.get_payload())
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.fetch(uid, "(RFC822)")

            if status == "OK" and response:
                email_body = response[0][1]
                message = email.message_from_bytes(email_body)
                return message
            else:
                return None

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to fetch email {uid}: {e}")

    def fetch_multiple(self, uids: list[str]) -> list[Message]:
        """Fetch multiple emails efficiently.

        Args:
            uids: List of email UIDs

        Returns:
            List of email.Message objects

        Example:
            >>> uids = client.search('SINCE 01-Feb-2026')
            >>> messages = client.fetch_multiple(uids)
            >>> for msg in messages:
            ...     print(f"{msg['From']} - {msg['Subject']}")
        """
        messages = []

        for uid in uids:
            try:
                msg = self.fetch_email(uid)
                if msg:
                    messages.append(msg)
            except Exception:
                continue

        return messages

    def get_email_headers(self, uid: str) -> Optional[dict]:
        """Get email headers only (faster than full fetch).

        Args:
            uid: Email UID

        Returns:
            Dict of headers or None

        Example:
            >>> headers = client.get_email_headers("12345")
            >>> print(headers.get('From'))
            >>> print(headers.get('Subject'))
            >>> print(headers.get('Date'))
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.fetch(uid, "(BODY.PEEK[HEADER])")

            if status == "OK" and response:
                header_data = response[0][1]
                message = email.message_from_bytes(header_data)

                headers = {}
                for key in message.keys():
                    headers[key] = message[key]

                return headers
            else:
                return None

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to get headers for {uid}: {e}")

    def add_flag(self, uid: str, flag: str) -> bool:
        """Add flag to email (e.g., \\Seen, \\Flagged).

        Args:
            uid: Email UID
            flag: Flag to add

        Returns:
            True if successful

        Common flags:
            \\Seen - Marked as read
            \\Flagged - Starred
            \\Answered - Replied to
            \\Deleted - Marked for deletion
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.store(uid, "+FLAGS", flag)
            return status == "OK"

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to add flag: {e}")

    def remove_flag(self, uid: str, flag: str) -> bool:
        """Remove flag from email.

        Args:
            uid: Email UID
            flag: Flag to remove

        Returns:
            True if successful
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.store(uid, "-FLAGS", flag)
            return status == "OK"

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to remove flag: {e}")

    def get_folder_stats(self, folder_name: str = "INBOX") -> dict:
        """Get statistics for a folder.

        Args:
            folder_name: Folder name to check

        Returns:
            Dict with exists, recent, unseen counts

        Example:
            >>> stats = client.get_folder_stats("INBOX")
            >>> print(f"Total: {stats['exists']}, Unread: {stats['unseen']}")
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            self.select_folder(folder_name)
            status, response = self.imap.status(
                folder_name, "(MESSAGES RECENT UNSEEN)"
            )

            if status == "OK":
                # Parse response: "INBOX (MESSAGES 100 RECENT 5 UNSEEN 10)"
                result = {}
                resp_str = response[0].decode("utf-8")

                for key in ["MESSAGES", "RECENT", "UNSEEN"]:
                    if key in resp_str:
                        val = resp_str.split(f"{key} ")[1].split()[0]
                        result[key.lower()] = int(val)

                return result
            else:
                return {}

        except Exception as e:
            raise RuntimeError(f"Failed to get folder stats: {e}")

    def expunge(self) -> bool:
        """Permanently delete emails marked for deletion.

        Returns:
            True if successful

        Warning:
            This permanently deletes marked emails!
        """
        if not self.imap:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            status, response = self.imap.expunge()
            return status == "OK"

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to expunge: {e}")

    def is_connected(self) -> bool:
        """Check if client is connected.

        Returns:
            True if connected
        """
        return self.imap is not None
