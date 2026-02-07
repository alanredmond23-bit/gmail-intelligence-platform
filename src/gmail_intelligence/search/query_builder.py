"""Build Gmail search queries."""


class QueryBuilder:
    """Build Gmail IMAP/API search queries."""

    def __init__(self):
        """Initialize query builder."""
        self.terms = []

    def with_from(self, email: str) -> "QueryBuilder":
        """Add sender filter."""
        self.terms.append(f'from:"{email}"')
        return self

    def with_to(self, email: str) -> "QueryBuilder":
        """Add recipient filter."""
        self.terms.append(f'to:"{email}"')
        return self

    def with_subject(self, subject: str) -> "QueryBuilder":
        """Add subject filter."""
        self.terms.append(f'subject:"{subject}"')
        return self

    def build(self) -> str:
        """Build final query string."""
        return " ".join(self.terms)
