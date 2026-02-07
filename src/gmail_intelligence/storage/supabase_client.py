"""Supabase client wrapper for email data management."""

import os
from typing import Optional, Any
from datetime import datetime

from supabase import create_client, Client
from pydantic import BaseModel


class EmailRecord(BaseModel):
    """Email record schema for Supabase."""

    message_id: str
    gmail_id: Optional[str] = None
    from_address: str
    to_addresses: Optional[str] = None
    cc_addresses: Optional[str] = None
    bcc_addresses: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    html_body: Optional[str] = None
    timestamp: datetime
    thread_id: Optional[str] = None
    labels: Optional[str] = None  # JSON array
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    is_privileged: bool = False
    privilege_confidence: Optional[float] = None


class SupabaseManager:
    """Manage emails using Supabase PostgreSQL database."""

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """Initialize Supabase client.

        Args:
            supabase_url: Supabase project URL (from env if not provided)
            supabase_key: Supabase API key (from env if not provided)

        Environment Variables:
            SUPABASE_URL: Supabase project URL
            SUPABASE_KEY: Supabase anon key
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase URL and KEY required. Set SUPABASE_URL and SUPABASE_KEY "
                "environment variables or pass them as arguments."
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def initialize(self) -> bool:
        """Initialize database schema (creates tables if not exists).

        Note: Tables should be created via Supabase dashboard or migrations.
        This method verifies the tables exist.
        """
        try:
            # Verify tables exist by attempting a simple query
            self.client.table("emails").select("id").limit(1).execute()
            self.client.table("attachments").select("id").limit(1).execute()
            self.client.table("entities").select("id").limit(1).execute()
            return True
        except Exception as e:
            raise RuntimeError(
                f"Database tables not initialized. Please create them via "
                f"Supabase dashboard. Error: {e}"
            )

    def insert_email(self, email: dict) -> Optional[int]:
        """Insert email into database.

        Args:
            email: Email data dictionary

        Returns:
            Email ID (from database)
        """
        try:
            response = self.client.table("emails").insert(email).execute()
            if response.data:
                return response.data[0].get("id")
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to insert email: {e}")

    def batch_insert_emails(self, emails: list[dict]) -> list[int]:
        """Batch insert multiple emails for performance.

        Args:
            emails: List of email dictionaries

        Returns:
            List of inserted email IDs
        """
        try:
            response = self.client.table("emails").insert(emails).execute()
            return [email.get("id") for email in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to batch insert emails: {e}")

    def get_email(self, email_id: int) -> Optional[dict]:
        """Get email by ID.

        Args:
            email_id: Email ID

        Returns:
            Email dict or None
        """
        try:
            response = self.client.table("emails").select("*").eq("id", email_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise RuntimeError(f"Failed to get email: {e}")

    def query_emails(
        self,
        where: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """Query emails with filtering.

        Args:
            where: Filter string (e.g., "from_address=eq.test@example.com")
            limit: Max results
            offset: Skip N results

        Returns:
            List of email dicts
        """
        try:
            query = self.client.table("emails").select("*")

            if where:
                # Parse simple where clause: "column=operator.value"
                # Examples: "from_address=eq.test@example.com", "timestamp=gt.2026-01-01"
                parts = where.split("=", 1)
                if len(parts) == 2:
                    column, condition = parts
                    operator, value = condition.split(".", 1)
                    query = query.filter(column, operator, value)

            response = query.limit(limit).offset(offset).execute()
            return response.data
        except Exception as e:
            raise RuntimeError(f"Failed to query emails: {e}")

    def search_emails(self, search_text: str, limit: int = 50) -> list[dict]:
        """Full-text search emails by body and subject.

        Args:
            search_text: Text to search for
            limit: Max results

        Returns:
            List of matching email dicts
        """
        try:
            # Use Supabase full-text search (requires FTS index on emails table)
            response = (
                self.client.rpc(
                    "search_emails",
                    {
                        "query": search_text,
                        "max_results": limit,
                    },
                )
                .execute()
            )
            return response.data
        except Exception as e:
            # Fallback to LIKE search if RPC not available
            try:
                response = (
                    self.client.table("emails")
                    .select("*")
                    .or_(f"body.ilike.%{search_text}%,subject.ilike.%{search_text}%")
                    .limit(limit)
                    .execute()
                )
                return response.data
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Search failed: {e}. Fallback also failed: {fallback_error}"
                )

    def update_email(self, email_id: int, updates: dict) -> bool:
        """Update email record.

        Args:
            email_id: Email ID
            updates: Dict of fields to update

        Returns:
            Success status
        """
        try:
            response = (
                self.client.table("emails")
                .update(updates)
                .eq("id", email_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            raise RuntimeError(f"Failed to update email: {e}")

    def delete_email(self, email_id: int) -> bool:
        """Delete email record.

        Args:
            email_id: Email ID

        Returns:
            Success status
        """
        try:
            response = self.client.table("emails").delete().eq("id", email_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise RuntimeError(f"Failed to delete email: {e}")

    def insert_attachment(self, email_id: int, filename: str, file_path: str) -> Optional[int]:
        """Insert attachment record.

        Args:
            email_id: Parent email ID
            filename: Attachment filename
            file_path: Path to file

        Returns:
            Attachment ID
        """
        try:
            response = (
                self.client.table("attachments")
                .insert(
                    {
                        "email_id": email_id,
                        "filename": filename,
                        "file_path": file_path,
                    }
                )
                .execute()
            )
            return response.data[0].get("id") if response.data else None
        except Exception as e:
            raise RuntimeError(f"Failed to insert attachment: {e}")

    def insert_entities(self, email_id: int, entities: list[dict]) -> list[int]:
        """Insert extracted entities for an email.

        Args:
            email_id: Parent email ID
            entities: List of entity dicts with type and value

        Returns:
            List of entity IDs
        """
        try:
            entity_records = [
                {
                    "email_id": email_id,
                    "entity_type": ent.get("type"),
                    "entity_value": ent.get("value"),
                    "confidence": ent.get("confidence"),
                }
                for ent in entities
            ]
            response = self.client.table("entities").insert(entity_records).execute()
            return [ent.get("id") for ent in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to insert entities: {e}")

    def get_stats(self) -> dict:
        """Get database statistics.

        Returns:
            Dict with count, date range, etc.
        """
        try:
            emails = self.client.table("emails").select("count").execute()
            count_response = (
                self.client.table("emails")
                .select("count")
                .execute()
            )

            return {
                "total_emails": count_response.count or 0,
                "status": "connected",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get stats: {e}")
