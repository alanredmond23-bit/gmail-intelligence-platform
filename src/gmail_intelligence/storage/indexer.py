"""Full-text search indexing."""


class IndexManager:
    """Create and manage full-text search indexes."""

    def index_emails(self, emails: list[dict]) -> bool:
        """Create search index for emails."""
        # TODO: Implement indexing
        raise NotImplementedError

    def search_index(self, query: str) -> list[dict]:
        """Search using full-text index."""
        # TODO: Implement index search
        raise NotImplementedError
