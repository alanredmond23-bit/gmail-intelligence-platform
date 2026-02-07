"""Parse and extract information from email messages."""

import email
import base64
from typing import Optional, dict, list
from email.message import Message
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime, parseaddr


class EmailParser:
    """Parse RFC822 email messages and extract structured data.

    Handles:
    - Header extraction (From, To, Subject, Date, etc.)
    - Body extraction (plain text and HTML)
    - Attachment listing and metadata
    - Multipart message handling
    """

    @staticmethod
    def parse_message(raw_message: bytes) -> Message:
        """Parse raw email message.

        Args:
            raw_message: Raw RFC822 email bytes

        Returns:
            email.Message object

        Raises:
            ValueError: If message is invalid
        """
        try:
            message = email.message_from_bytes(raw_message)
            return message
        except Exception as e:
            raise ValueError(f"Failed to parse message: {e}")

    @staticmethod
    def extract_headers(message: Message) -> dict:
        """Extract email headers into dictionary.

        Args:
            message: email.Message object

        Returns:
            Dict with standard headers:
            - from_address: Sender email
            - to_addresses: Recipient list
            - cc_addresses: CC recipients
            - bcc_addresses: BCC recipients
            - subject: Email subject
            - date: Sent timestamp
            - message_id: Unique message ID
            - in_reply_to: Original message ID if reply
            - references: Thread references
            - content_type: MIME type

        Example:
            >>> headers = EmailParser.extract_headers(msg)
            >>> print(headers['from_address'])
            >>> print(headers['subject'])
        """
        headers = {}

        # From
        from_header = message.get("From", "")
        if from_header:
            name, email_addr = parseaddr(from_header)
            headers["from_name"] = name
            headers["from_address"] = email_addr

        # To
        to_header = message.get("To", "")
        if to_header:
            headers["to_addresses"] = [addr for name, addr in
                                      [parseaddr(x.strip()) for x in to_header.split(",")]]

        # CC
        cc_header = message.get("Cc", "")
        if cc_header:
            headers["cc_addresses"] = [addr for name, addr in
                                      [parseaddr(x.strip()) for x in cc_header.split(",")]]

        # BCC
        bcc_header = message.get("Bcc", "")
        if bcc_header:
            headers["bcc_addresses"] = [addr for name, addr in
                                       [parseaddr(x.strip()) for x in bcc_header.split(",")]]

        # Subject
        subject = message.get("Subject", "")
        headers["subject"] = subject if subject else "(no subject)"

        # Date
        date_header = message.get("Date", "")
        if date_header:
            try:
                headers["date"] = parsedate_to_datetime(date_header)
            except Exception:
                headers["date"] = date_header

        # Message ID
        headers["message_id"] = message.get("Message-ID", "")

        # Thread references
        headers["in_reply_to"] = message.get("In-Reply-To", "")
        headers["references"] = message.get("References", "")

        # Content type
        headers["content_type"] = message.get("Content-Type", "text/plain")

        return headers

    @staticmethod
    def extract_body(message: Message) -> tuple[Optional[str], Optional[str]]:
        """Extract email body (plain text and/or HTML).

        Args:
            message: email.Message object

        Returns:
            Tuple of (plain_text_body, html_body)

        Example:
            >>> text_body, html_body = EmailParser.extract_body(msg)
            >>> if html_body:
            ...     print("Has HTML version")
        """
        text_body = None
        html_body = None

        # Handle multipart messages
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()

                # Text part
                if content_type == "text/plain" and not text_body:
                    text_body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8",
                        errors="ignore"
                    )

                # HTML part
                elif content_type == "text/html" and not html_body:
                    html_body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8",
                        errors="ignore"
                    )

        else:
            # Single-part message
            try:
                payload = message.get_payload(decode=True)
                if isinstance(payload, bytes):
                    decoded = payload.decode(
                        message.get_content_charset() or "utf-8",
                        errors="ignore"
                    )
                else:
                    decoded = payload

                content_type = message.get_content_type()
                if content_type == "text/html":
                    html_body = decoded
                else:
                    text_body = decoded
            except Exception:
                text_body = message.get_payload()

        return text_body, html_body

    @staticmethod
    def extract_attachments(message: Message) -> list[dict]:
        """Extract attachment information from message.

        Args:
            message: email.Message object

        Returns:
            List of attachment dicts with:
            - filename: Original filename
            - content_type: MIME type
            - size: Size in bytes
            - data: Base64-encoded content (optional, set include_data=True)

        Example:
            >>> attachments = EmailParser.extract_attachments(msg)
            >>> for att in attachments:
            ...     print(f"{att['filename']} ({att['size']} bytes)")
        """
        attachments = []

        if not message.is_multipart():
            return attachments

        for part in message.walk():
            # Skip main message and text/html parts
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)

            attachment = {
                "filename": filename,
                "content_type": content_type,
                "size": len(payload) if payload else 0,
            }

            attachments.append(attachment)

        return attachments

    @staticmethod
    def get_attachment_data(message: Message, filename: str) -> Optional[bytes]:
        """Get attachment data by filename.

        Args:
            message: email.Message object
            filename: Attachment filename to retrieve

        Returns:
            Bytes of attachment or None if not found
        """
        for part in message.walk():
            if part.get_filename() == filename:
                return part.get_payload(decode=True)

        return None

    @staticmethod
    def parse_gmail_message(gmail_message: dict) -> dict:
        """Parse Gmail API message format into structured data.

        Args:
            gmail_message: Message dict from Gmail API (format='full')

        Returns:
            Structured email dict with all extracted fields

        Example:
            >>> msg = client.get_message("abc123")
            >>> structured = EmailParser.parse_gmail_message(msg)
            >>> print(structured['subject'])
            >>> print(structured['from_address'])
        """
        result = {
            "id": gmail_message.get("id"),
            "thread_id": gmail_message.get("threadId"),
            "labels": gmail_message.get("labelIds", []),
            "size": int(gmail_message.get("sizeEstimate", 0)),
        }

        # Extract headers and body
        payload = gmail_message.get("payload", {})

        if "headers" in payload:
            # Parse headers
            headers_list = payload["headers"]
            headers_dict = {h["name"].lower(): h["value"] for h in headers_list}

            result["message_id"] = headers_dict.get("message-id", "")
            result["from_name"] = ""
            result["from_address"] = ""

            if "from" in headers_dict:
                name, addr = parseaddr(headers_dict["from"])
                result["from_name"] = name
                result["from_address"] = addr

            result["to_addresses"] = []
            if "to" in headers_dict:
                result["to_addresses"] = [
                    addr for name, addr in
                    [parseaddr(x.strip()) for x in headers_dict["to"].split(",")]
                ]

            result["subject"] = headers_dict.get("subject", "(no subject)")
            result["date"] = headers_dict.get("date", "")

        # Extract body
        result["body"] = ""
        result["html_body"] = ""

        if "parts" in payload:
            # Multipart message
            for part in payload.get("parts", []):
                if "parts" in part:
                    # Nested multipart
                    continue

                mime_type = part.get("mimeType", "text/plain")
                data = part.get("body", {}).get("data", "")

                if data:
                    decoded_data = base64.urlsafe_b64decode(data).decode(
                        "utf-8", errors="ignore"
                    )
                    if mime_type == "text/plain":
                        result["body"] = decoded_data
                    elif mime_type == "text/html":
                        result["html_body"] = decoded_data

        elif "body" in payload:
            # Single-part message
            data = payload["body"].get("data", "")
            if data:
                decoded = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
                result["body"] = decoded

        return result

    @staticmethod
    def clean_body(text: Optional[str]) -> str:
        """Clean up email body text.

        Args:
            text: Raw email body

        Returns:
            Cleaned text

        - Removes excessive whitespace
        - Removes quoted sections (lines starting with >)
        - Removes signature separators
        """
        if not text:
            return ""

        lines = text.split("\n")
        cleaned = []

        skip_signature = False

        for line in lines:
            # Skip signature section
            if line.startswith("--"):
                skip_signature = True
                continue

            if skip_signature:
                continue

            # Skip quoted text (reply chains)
            if line.lstrip().startswith(">"):
                continue

            # Skip excessive blank lines
            if not line.strip() and cleaned and not cleaned[-1].strip():
                continue

            cleaned.append(line)

        return "\n".join(cleaned).strip()

    @staticmethod
    def get_plain_text_for_search(message: Message) -> str:
        """Get plain text version of email for full-text search.

        Args:
            message: email.Message object

        Returns:
            Combined text from subject and body

        Example:
            >>> text = EmailParser.get_plain_text_for_search(msg)
            >>> # Use for full-text indexing
        """
        headers = EmailParser.extract_headers(message)
        text_body, _ = EmailParser.extract_body(message)

        searchable = [headers.get("subject", "")]

        if text_body:
            searchable.append(EmailParser.clean_body(text_body))

        return " ".join(searchable)
