"""Progress tracking and display."""

from rich.progress import Progress


def create_progress_bar() -> Progress:
    """Create a progress bar for CLI output."""
    return Progress()
