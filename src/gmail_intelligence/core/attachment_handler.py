"""Handle email attachments."""

from pathlib import Path


class AttachmentHandler:
    """Process and store email attachments."""

    def __init__(self, storage_path: Path):
        """Initialize attachment handler.

        Args:
            storage_path: Path to store attachments
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def extract_attachments(self, message: dict) -> list[Path]:
        """Extract and save attachments from message."""
        # TODO: Implement attachment extraction
        raise NotImplementedError
