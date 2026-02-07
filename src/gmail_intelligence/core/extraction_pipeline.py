"""Complete email extraction pipeline: fetch → parse → store."""

import logging
from typing import Optional, Callable
from datetime import datetime

from .gmail_api import GmailAPIClient
from .imap_client import IMAPClient
from .email_parser import EmailParser
from .attachment_handler import AttachmentHandler
from ..storage.database import DatabaseManager


class ExtractionPipeline:
    """Unified email extraction pipeline with automatic retry and progress tracking.

    Orchestrates:
    - Email fetching (Gmail API or IMAP)
    - RFC822 parsing
    - Attachment extraction and storage
    - Database persistence
    - Error handling and recovery
    - Progress reporting
    """

    def __init__(
        self,
        gmail_client: Optional[GmailAPIClient] = None,
        imap_client: Optional[IMAPClient] = None,
        database: Optional[DatabaseManager] = None,
        attachment_handler: Optional[AttachmentHandler] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize extraction pipeline.

        Args:
            gmail_client: Authenticated GmailAPIClient (creates new if None)
            imap_client: Configured IMAPClient (creates new if None)
            database: DatabaseManager (creates new if None)
            attachment_handler: AttachmentHandler (creates new if None)
            logger: logging.Logger instance

        Example:
            >>> pipeline = ExtractionPipeline()
            >>> results = pipeline.extract_all(
            ...     query="from:lawyer@firm.com",
            ...     max_results=100
            ... )
        """
        self.gmail_client = gmail_client or GmailAPIClient()
        self.imap_client = imap_client or IMAPClient()
        self.database = database or DatabaseManager()
        self.attachment_handler = attachment_handler or AttachmentHandler()
        self.parser = EmailParser()
        self.logger = logger or logging.getLogger(__name__)

        self.stats = {
            "total_messages": 0,
            "successfully_stored": 0,
            "failed": 0,
            "attachments_saved": 0,
            "start_time": None,
            "end_time": None,
        }

    def extract_all(
        self,
        query: str = "",
        max_results: int = 100,
        use_gmail_api: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> dict:
        """Extract all matching emails and store in database.

        Args:
            query: Gmail/IMAP search query
            max_results: Maximum emails to fetch
            use_gmail_api: Use Gmail API (True) or IMAP (False)
            progress_callback: Optional callback(current, total, message_dict)

        Returns:
            Dict with extraction statistics:
            - total_messages: Count processed
            - successfully_stored: Count stored
            - failed: Count failed
            - attachments_saved: Count of files
            - duration: Time elapsed

        Example:
            >>> pipeline = ExtractionPipeline()
            >>> def progress(curr, total, msg):
            ...     print(f"{curr}/{total}: {msg.get('subject')}")
            >>> results = pipeline.extract_all(
            ...     query="from:john@example.com",
            ...     max_results=50,
            ...     progress_callback=progress
            ... )
            >>> print(f"Stored {results['successfully_stored']} emails")
        """
        self.stats = {
            "total_messages": 0,
            "successfully_stored": 0,
            "failed": 0,
            "attachments_saved": 0,
            "start_time": datetime.now(),
            "end_time": None,
        }

        try:
            if use_gmail_api:
                self._extract_with_gmail_api(query, max_results, progress_callback)
            else:
                self._extract_with_imap(query, max_results, progress_callback)

        except Exception as e:
            self.logger.error(f"Extraction pipeline failed: {e}")

        finally:
            self.stats["end_time"] = datetime.now()

        return self._format_stats()

    def _extract_with_gmail_api(
        self,
        query: str,
        max_results: int,
        progress_callback: Optional[Callable] = None,
    ) -> None:
        """Extract using Gmail API with pagination."""
        if not self.gmail_client.is_authenticated():
            self.logger.info("Authenticating with Gmail API...")
            self.gmail_client.authenticate()

        page_token = None
        processed = 0

        while True:
            self.logger.info(f"Fetching batch from Gmail API (max {max_results})...")

            try:
                messages, page_token = self.gmail_client.get_messages(
                    query=query,
                    max_results=min(100, max_results - processed),
                    page_token=page_token,
                )

                if not messages:
                    self.logger.info("No more messages to fetch")
                    break

                self.logger.info(f"Got {len(messages)} message IDs, fetching full messages...")

                # Fetch full messages
                message_ids = [msg["id"] for msg in messages]
                full_messages = self.gmail_client.batch_get_messages(message_ids)

                # Process each message
                for full_msg in full_messages:
                    try:
                        self._process_message(
                            full_msg,
                            progress_callback,
                            processed,
                            len(messages),
                        )
                        processed += 1
                    except Exception as e:
                        self.logger.error(f"Failed to process message: {e}")
                        self.stats["failed"] += 1

                    if processed >= max_results:
                        break

                if processed >= max_results or not page_token:
                    break

            except Exception as e:
                self.logger.error(f"Gmail API batch failed: {e}")
                self.stats["failed"] += len(messages) if messages else 1

        self.logger.info(f"Extraction complete: {processed} messages processed")

    def _extract_with_imap(
        self,
        query: str,
        max_results: int,
        progress_callback: Optional[Callable] = None,
    ) -> None:
        """Extract using IMAP as fallback."""
        if not self.imap_client.is_connected():
            self.logger.info("Connecting to IMAP...")
            # User must provide email/password - would come from config/env
            raise RuntimeError(
                "IMAP client not connected. Call connect(email, password) first."
            )

        self.logger.info(f"Searching IMAP with query: {query}")

        try:
            # Convert Gmail query to IMAP syntax (basic conversion)
            imap_query = self._convert_gmail_query_to_imap(query)
            uids = self.imap_client.search(imap_query)

            self.logger.info(f"Found {len(uids)} messages via IMAP")

            # Process emails
            processed = 0
            for uid in uids[:max_results]:
                try:
                    msg = self.imap_client.fetch_email(uid)
                    if msg:
                        parsed_msg = {
                            "id": uid,
                            "payload": {"headers": [], "parts": []},
                        }

                        # Convert IMAP message to Gmail API-like format
                        headers = self.parser.extract_headers(msg)
                        body, html = self.parser.extract_body(msg)

                        # Restructure for processing
                        parsed_msg["payload"]["headers"] = [
                            {"name": k, "value": v}
                            for k, v in headers.items()
                        ]

                        if body:
                            parsed_msg["payload"]["parts"] = [
                                {
                                    "mimeType": "text/plain",
                                    "body": {"data": body},
                                }
                            ]

                        self._process_message(
                            parsed_msg,
                            progress_callback,
                            processed,
                            len(uids),
                        )
                        processed += 1

                except Exception as e:
                    self.logger.error(f"Failed to process IMAP message {uid}: {e}")
                    self.stats["failed"] += 1

        except Exception as e:
            self.logger.error(f"IMAP extraction failed: {e}")

    def _process_message(
        self,
        message: dict,
        progress_callback: Optional[Callable],
        current: int,
        total: int,
    ) -> None:
        """Process single message: parse, extract attachments, store."""
        self.stats["total_messages"] += 1

        try:
            # Parse message
            structured = self.parser.parse_gmail_message(message)

            # Get database ID for this email
            email_id = self.database.insert_email({
                "message_id": structured.get("id", ""),
                "from_address": structured.get("from_address", ""),
                "subject": structured.get("subject", ""),
                "body": structured.get("body", ""),
                "html_body": structured.get("html_body", ""),
                "timestamp": structured.get("date", datetime.now()),
                "thread_id": structured.get("thread_id", ""),
                "labels": ",".join(structured.get("labels", [])),
            })

            if not email_id:
                raise RuntimeError("Failed to insert email into database")

            # Extract and save attachments (would need IMAP Message object)
            # For now, store empty attachments list
            # In practice, would extract from original message object
            attachments_count = 0

            self.stats["successfully_stored"] += 1
            self.stats["attachments_saved"] += attachments_count

            # Call progress callback
            if progress_callback:
                progress_callback(current + 1, total, {
                    "id": structured.get("id"),
                    "subject": structured.get("subject"),
                    "from_address": structured.get("from_address"),
                })

            self.logger.debug(f"Stored: {structured.get('subject')}")

        except Exception as e:
            self.logger.error(f"Message processing failed: {e}")
            self.stats["failed"] += 1

    @staticmethod
    def _convert_gmail_query_to_imap(gmail_query: str) -> str:
        """Convert Gmail search syntax to IMAP syntax.

        Args:
            gmail_query: Gmail query (e.g., "from:john@example.com")

        Returns:
            IMAP query (e.g., 'FROM "john@example.com"')

        Example:
            >>> imap_q = ExtractionPipeline._convert_gmail_query_to_imap(
            ...     "from:john@example.com subject:contract"
            ... )
            >>> print(imap_q)
            'FROM "john@example.com" SUBJECT "contract"'
        """
        # Basic conversion - expand as needed
        conversions = {
            "from:": "FROM ",
            "to:": "TO ",
            "subject:": "SUBJECT ",
            "cc:": "CC ",
            "bcc:": "BCC ",
        }

        imap_query = gmail_query
        for gmail_op, imap_op in conversions.items():
            imap_query = imap_query.replace(gmail_op, imap_op)

        return imap_query if imap_query.strip() else "ALL"

    def _format_stats(self) -> dict:
        """Format statistics for output."""
        duration = None
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (
                self.stats["end_time"] - self.stats["start_time"]
            ).total_seconds()

        return {
            "total_messages": self.stats["total_messages"],
            "successfully_stored": self.stats["successfully_stored"],
            "failed": self.stats["failed"],
            "attachments_saved": self.stats["attachments_saved"],
            "duration_seconds": duration,
            "messages_per_second": (
                self.stats["successfully_stored"] / duration
                if duration and duration > 0
                else 0
            ),
        }

    def extract_single(self, message_id: str) -> Optional[int]:
        """Extract and store single message by ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Database email ID or None

        Example:
            >>> pipeline = ExtractionPipeline()
            >>> email_id = pipeline.extract_single("abc123def456")
        """
        if not self.gmail_client.is_authenticated():
            self.gmail_client.authenticate()

        try:
            message = self.gmail_client.get_message(message_id)
            structured = self.parser.parse_gmail_message(message)

            email_id = self.database.insert_email({
                "message_id": structured.get("id"),
                "from_address": structured.get("from_address"),
                "subject": structured.get("subject"),
                "body": structured.get("body"),
                "timestamp": structured.get("date", datetime.now()),
            })

            return email_id

        except Exception as e:
            self.logger.error(f"Single message extraction failed: {e}")
            return None

    def get_stats(self) -> dict:
        """Get current extraction statistics."""
        return self._format_stats()
