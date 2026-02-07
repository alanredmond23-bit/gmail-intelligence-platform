"""Database management - Supabase PostgreSQL backend."""

import os
from typing import Optional

from .supabase_client import SupabaseManager


class DatabaseManager:
    """Manage email storage using Supabase PostgreSQL.

    This manager provides a unified interface for all database operations,
    automatically handling connection pooling and query optimization.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """Initialize database manager.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key

        Environment Variables:
            SUPABASE_URL: Supabase project URL
            SUPABASE_KEY: Supabase anon key

        Example:
            >>> manager = DatabaseManager()
            >>> manager.initialize()
            >>> email_id = manager.insert_email({"from_address": "...", ...})
        """
        self.supabase = SupabaseManager(supabase_url, supabase_key)

    def initialize(self) -> bool:
        """Initialize database schema.

        Returns:
            True if initialization successful
        """
        return self.supabase.initialize()

    def insert_email(self, email: dict) -> Optional[int]:
        """Insert email into database.

        Args:
            email: Email dict with fields:
                - message_id: Gmail message ID (unique)
                - from_address: Sender email
                - subject: Email subject
                - body: Email body text
                - timestamp: Sent date
                - (optional) sentiment, is_privileged, labels, etc.

        Returns:
            Email ID from database
        """
        return self.supabase.insert_email(email)

    def batch_insert_emails(self, emails: list[dict]) -> list[int]:
        """Batch insert multiple emails for performance.

        Args:
            emails: List of email dictionaries

        Returns:
            List of inserted email IDs
        """
        return self.supabase.batch_insert_emails(emails)

    def get_email(self, email_id: int) -> Optional[dict]:
        """Get email by ID.

        Args:
            email_id: Email ID

        Returns:
            Email dict or None if not found
        """
        return self.supabase.get_email(email_id)

    def query_emails(
        self,
        where: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """Query emails with filtering.

        Args:
            where: Filter clause (e.g., "from_address=eq.test@example.com")
            limit: Max results (default 100)
            offset: Skip N results (default 0)

        Returns:
            List of email dictionaries

        Example:
            >>> emails = db.query_emails(where="sentiment=eq.positive", limit=50)
            >>> emails = db.query_emails(limit=10)  # Get first 10
        """
        return self.supabase.query_emails(where, limit, offset)

    def search_emails(self, search_text: str, limit: int = 50) -> list[dict]:
        """Full-text search emails by body and subject.

        Args:
            search_text: Text to search for
            limit: Max results (default 50)

        Returns:
            List of matching emails

        Example:
            >>> results = db.search_emails("bankruptcy lawsuit", limit=20)
        """
        return self.supabase.search_emails(search_text, limit)

    def update_email(self, email_id: int, updates: dict) -> bool:
        """Update email record.

        Args:
            email_id: Email ID
            updates: Dict of fields to update

        Returns:
            True if successful

        Example:
            >>> db.update_email(123, {"sentiment": "negative", "is_privileged": True})
        """
        return self.supabase.update_email(email_id, updates)

    def delete_email(self, email_id: int) -> bool:
        """Delete email record.

        Args:
            email_id: Email ID

        Returns:
            True if successful
        """
        return self.supabase.delete_email(email_id)

    def insert_attachment(
        self,
        email_id: int,
        filename: str,
        file_path: str,
    ) -> Optional[int]:
        """Insert attachment record.

        Args:
            email_id: Parent email ID
            filename: Attachment filename
            file_path: Path to file on disk

        Returns:
            Attachment ID
        """
        return self.supabase.insert_attachment(email_id, filename, file_path)

    def insert_entities(self, email_id: int, entities: list[dict]) -> list[int]:
        """Insert extracted entities for an email.

        Args:
            email_id: Parent email ID
            entities: List of dicts with:
                - type: Entity type (PERSON, ORGANIZATION, LOCATION, etc)
                - value: Entity value
                - confidence: Confidence score (0-1)

        Returns:
            List of entity IDs

        Example:
            >>> entities = [
            ...     {"type": "PERSON", "value": "John Smith", "confidence": 0.95},
            ...     {"type": "ORGANIZATION", "value": "Acme Corp", "confidence": 0.88},
            ... ]
            >>> db.insert_entities(123, entities)
        """
        return self.supabase.insert_entities(email_id, entities)

    def get_stats(self) -> dict:
        """Get database statistics.

        Returns:
            Dict with:
                - total_emails: Count of stored emails
                - status: Connection status
        """
        return self.supabase.get_stats()
