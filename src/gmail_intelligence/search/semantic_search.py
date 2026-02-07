"""Semantic and fuzzy email search."""

from typing import Optional


class SemanticSearch:
    """Perform semantic and fuzzy matching on emails."""

    def __init__(self, model: Optional[str] = None):
        """Initialize semantic search engine.

        Args:
            model: AI model to use for embeddings (default: OpenAI)
        """
        self.model = model or "text-embedding-3-small"

    def search(self, purpose: str, emails: list[dict]) -> list[dict]:
        """Search emails by purpose using semantic matching."""
        # TODO: Implement semantic search
        raise NotImplementedError
