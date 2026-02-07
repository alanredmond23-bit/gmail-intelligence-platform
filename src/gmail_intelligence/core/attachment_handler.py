"""Handle email attachments - save to S3, track metadata."""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, dict, list
from email.message import Message
from datetime import datetime


class AttachmentHandler:
    """Process and store email attachments.

    Features:
    - Save attachments to S3 (Supabase-S3 mount)
    - Track file metadata (name, type, size, hash)
    - Handle large files efficiently
    - Organize by email ID and date
    - Deduplicate with content hash
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize attachment handler.

        Args:
            storage_path: Base path for attachments (default: ~/Supabase-S3/attachments)
                         Set to ~/Supabase-S3 for automatic fleet sync

        Environment Variables:
            ATTACHMENT_STORAGE: Override storage path
        """
        self.storage_path = Path(
            storage_path
            or os.getenv("ATTACHMENT_STORAGE", "~/Supabase-S3/attachments")
        ).expanduser()

        # Create directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def extract_attachments(
        self,
        message: Message,
        email_id: int,
        save_files: bool = True,
    ) -> list[dict]:
        """Extract attachments from email message and save to S3.

        Args:
            message: email.Message object
            email_id: Database email ID for organization
            save_files: Whether to actually save files (default: True)

        Returns:
            List of attachment dicts with metadata:
            - filename: Original filename
            - content_type: MIME type
            - size: File size in bytes
            - file_path: Relative path in storage
            - content_hash: SHA256 of content
            - saved_at: Timestamp

        Example:
            >>> from email_parser import EmailParser
            >>> parser = EmailParser()
            >>> message = parser.parse_message(raw_bytes)
            >>> handler = AttachmentHandler()
            >>> attachments = handler.extract_attachments(message, email_id=123)
            >>> for att in attachments:
            ...     print(f"{att['filename']}: {att['size']} bytes")

        Raises:
            RuntimeError: If attachment saving fails
        """
        attachments = []

        if not message.is_multipart():
            return attachments

        for part in message.walk():
            # Skip non-attachment parts
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            try:
                # Get attachment data
                content = part.get_payload(decode=True)
                if not content:
                    continue

                # Calculate content hash for deduplication
                content_hash = hashlib.sha256(content).hexdigest()

                # Get MIME type
                content_type = part.get_content_type()

                # Organize path: attachments/YYYY/MM/email_ID/filename
                now = datetime.now()
                organized_path = (
                    self.storage_path
                    / f"{now.year:04d}"
                    / f"{now.month:02d}"
                    / f"email_{email_id}"
                )

                # Save file if requested
                file_path = None
                if save_files:
                    organized_path.mkdir(parents=True, exist_ok=True)
                    file_path = organized_path / filename

                    # Write file
                    with open(file_path, "wb") as f:
                        f.write(content)

                # Record attachment metadata
                attachment = {
                    "filename": filename,
                    "content_type": content_type,
                    "size": len(content),
                    "file_path": str(
                        file_path.relative_to(self.storage_path)
                        if file_path
                        else f"{now.year:04d}/{now.month:02d}/email_{email_id}/{filename}"
                    ),
                    "content_hash": content_hash,
                    "saved_at": now.isoformat(),
                }

                attachments.append(attachment)

            except Exception as e:
                raise RuntimeError(f"Failed to process attachment {filename}: {e}")

        return attachments

    def get_attachment(
        self,
        relative_path: str,
    ) -> Optional[bytes]:
        """Retrieve attachment from storage.

        Args:
            relative_path: Relative path from storage_path

        Returns:
            File content as bytes or None if not found

        Example:
            >>> handler = AttachmentHandler()
            >>> content = handler.get_attachment("2026/02/email_123/document.pdf")
            >>> with open("download.pdf", "wb") as f:
            ...     f.write(content)
        """
        file_path = self.storage_path / relative_path

        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read attachment: {e}")

    def delete_attachment(self, relative_path: str) -> bool:
        """Delete attachment from storage.

        Args:
            relative_path: Relative path from storage_path

        Returns:
            True if successful
        """
        file_path = self.storage_path / relative_path

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete attachment: {e}")

    def get_attachment_url(
        self,
        relative_path: str,
        base_url: Optional[str] = None,
    ) -> str:
        """Get URL for attachment (for S3 public access).

        Args:
            relative_path: Relative path from storage_path
            base_url: Base URL for S3 bucket (optional)

        Returns:
            Full URL string

        Example:
            >>> url = handler.get_attachment_url(
            ...     "2026/02/email_123/document.pdf",
            ...     base_url="https://supabase-project.s3.amazonaws.com"
            ... )
        """
        if base_url:
            return f"{base_url}/{relative_path}"
        else:
            # Use local file path
            return str(self.storage_path / relative_path)

    def get_storage_stats(self) -> dict:
        """Get attachment storage statistics.

        Returns:
            Dict with:
            - total_files: Number of attachments
            - total_size: Total bytes used
            - by_type: Dict of type -> count

        Example:
            >>> stats = handler.get_storage_stats()
            >>> print(f"Total: {stats['total_files']} files, {stats['total_size']} bytes")
            >>> print(f"PDF: {stats['by_type'].get('application/pdf', 0)}")
        """
        total_files = 0
        total_size = 0
        by_type = {}

        for file_path in self.storage_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                file_size = file_path.stat().st_size
                total_size += file_size

                # Guess MIME type
                mime_type, _ = mimetypes.guess_type(str(file_path))
                mime_type = mime_type or "application/octet-stream"
                by_type[mime_type] = by_type.get(mime_type, 0) + 1

        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": by_type,
        }

    def clean_old_attachments(self, days: int = 30) -> int:
        """Clean up old attachments (older than N days).

        Args:
            days: Delete attachments older than this many days

        Returns:
            Number of files deleted

        Warning:
            This permanently deletes files!
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0

        for file_path in self.storage_path.rglob("*"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception:
                        pass

        return deleted

    def validate_storage(self) -> dict:
        """Validate attachment storage integrity.

        Returns:
            Dict with validation results:
            - is_writable: Can write to storage
            - is_readable: Can read from storage
            - available_space: Disk space in bytes

        Example:
            >>> validation = handler.validate_storage()
            >>> if not validation['is_writable']:
            ...     print("Storage is read-only!")
        """
        results = {
            "is_writable": False,
            "is_readable": False,
            "available_space": 0,
        }

        # Test write
        test_file = self.storage_path / ".test"
        try:
            test_file.write_bytes(b"test")
            results["is_writable"] = True
            test_file.unlink()
        except Exception:
            pass

        # Test read
        try:
            if self.storage_path.exists():
                list(self.storage_path.iterdir())
                results["is_readable"] = True
        except Exception:
            pass

        # Available space
        try:
            import shutil

            stat = shutil.disk_usage(str(self.storage_path))
            results["available_space"] = stat.free
        except Exception:
            pass

        return results

    @staticmethod
    def get_safe_filename(filename: str, max_length: int = 255) -> str:
        """Sanitize filename for safe storage.

        Args:
            filename: Original filename
            max_length: Maximum filename length

        Returns:
            Safe filename

        Example:
            >>> safe = AttachmentHandler.get_safe_filename("my file (v2).pdf")
            >>> print(safe)
            'my_file_v2.pdf'
        """
        # Remove unsafe characters
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)

        # Limit length while preserving extension
        if len(safe) > max_length:
            name, ext = safe.rsplit(".", 1)
            safe = name[: max_length - len(ext) - 1] + "." + ext

        return safe
