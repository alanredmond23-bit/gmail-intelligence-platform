"""Manage local file storage of emails."""

from pathlib import Path


class FileManager:
    """Organize emails into folders and files."""

    def __init__(self, base_path: Path):
        """Initialize file manager.

        Args:
            base_path: Base directory for email storage
        """
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_email(self, email: dict, folder: str = "") -> Path:
        """Save email to file.

        Returns:
            Path to saved file
        """
        # TODO: Implement email file saving
        raise NotImplementedError
