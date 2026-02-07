# Developer Guide

Internal documentation for development team.

## Architecture Overview

### Module Responsibilities

```
┌─ CLI Entry Point (__main__.py)
│
├─ Core Layer (core/)
│  ├─ IMAP Client - Email server connectivity
│  ├─ Gmail API Client - OAuth2 + Gmail API
│  ├─ Email Parser - RFC822 message parsing
│  └─ Attachment Handler - File extraction
│
├─ Search Layer (search/)
│  ├─ Query Builder - Gmail query syntax
│  ├─ Semantic Search - AI-powered matching
│  └─ Filters - Date, sender, label filtering
│
├─ Analysis Layer (analysis/)
│  ├─ Sentiment Analyzer - Emotional tone
│  ├─ Entity Extractor - People, orgs, locations
│  ├─ Classifier - Email categorization
│  └─ Privilege Detector - Attorney-client privilege
│
├─ Storage Layer (storage/)
│  ├─ Database Manager - SQLite ORM
│  ├─ File Manager - Local file organization
│  └─ Indexer - Full-text search
│
├─ Sync Layer (sync/)
│  ├─ Incremental Sync - Gmail History API
│  ├─ Task Scheduler - Cron/timer tasks
│  └─ Error Recovery - Self-healing
│
└─ Utils (utils/)
   ├─ Config - YAML configuration
   ├─ Logger - Logging setup
   └─ Progress - Progress tracking
```

## Implementation Guidelines

### Phase 2: What to Implement First

**Order of Implementation** (dependencies-first):

1. **`core/gmail_api.py`** - OAuth2 flow (foundation)
2. **`core/imap_client.py`** - IMAP connection
3. **`core/email_parser.py`** - Parse fetched messages
4. **`storage/database.py`** - Store emails
5. **`search/query_builder.py`** - Build queries
6. **`search/filters.py`** - Filter emails
7. **`analysis/*`** - Add analysis features
8. **`sync/incremental.py`** - Real-time sync
9. **`__main__.py`** - CLI interface

### Adding a New Analysis Feature

1. Create stub in `analysis/<feature>.py`
2. Add to `analysis/__init__.py` exports
3. Write tests in `tests/test_<feature>.py`
4. Implement with clear docstrings
5. Add to analysis pipeline in main
6. Update README examples

Example:

```python
# src/gmail_intelligence/analysis/my_analyzer.py
from typing import Optional

class MyAnalyzer:
    """Analyze emails for specific patterns."""

    def __init__(self, model: Optional[str] = None):
        """Initialize analyzer.

        Args:
            model: AI model to use (optional)
        """
        self.model = model or "gpt-4-mini"

    def analyze(self, email: dict) -> dict:
        """Analyze email.

        Args:
            email: Email dict with body, headers, etc

        Returns:
            Analysis results dict
        """
        # Implementation
        return {"result": "value"}
```

## Database Design

### Email Table

```sql
CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    message_id TEXT UNIQUE,
    from_address TEXT,
    subject TEXT,
    body TEXT,
    timestamp DATETIME,
    sentiment VARCHAR(20),
    is_privileged BOOLEAN,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Indexes for Performance

- `idx_emails_timestamp` - For date range queries
- `idx_emails_from` - For sender filtering
- `idx_emails_labels` - For label-based searches
- Full-text search index on body/subject

## Common Tasks

### Adding a New CLI Command

```python
# In src/gmail_intelligence/__main__.py

@app.command()
def my_command(
    param1: str = typer.Option(..., help="Description"),
    param2: int = typer.Option(10, help="Default is 10"),
):
    """Command description."""
    typer.echo(f"Running my_command with {param1}")
```

### Creating a Test for New Feature

```python
# In tests/test_new_feature.py

import pytest
from gmail_intelligence.module.feature import MyClass

@pytest.fixture
def setup():
    """Test setup."""
    return MyClass()

def test_my_feature(setup):
    """Test the feature."""
    result = setup.do_something()
    assert result is not None
```

### Adding a Dependency

1. Update `pyproject.toml` with version pin
2. Update optional groups if applicable
3. Document why it's needed
4. Test with `pip install -e ".[dev]"`

## Performance Considerations

### Email Fetching
- Batch size: 50 emails per request (configurable)
- Use IMAP search filters to reduce downloads
- Implement pagination for large result sets

### Database Queries
- Always use indexed columns in WHERE clauses
- Batch inserts for performance
- Use transactions for consistency

### AI API Calls
- Implement rate limiting (max 3 requests/sec for OpenAI)
- Cache embeddings for semantic search
- Implement retry logic with exponential backoff

### Memory Usage
- Stream large email bodies
- Use generators for large result sets
- Clean up attachments after processing

## Testing Strategy

### Test Coverage Target: 80%+

**Unit Tests** (50% of tests)
- Individual function/method behavior
- Mocked external dependencies
- Fast execution (<100ms each)

**Integration Tests** (30% of tests)
- Component interaction
- Database operations
- Real API calls (with fixtures)

**End-to-End Tests** (20% of tests)
- Full workflows
- Real Gmail API (with test account)
- Marked with `@pytest.mark.integration`

## Release Process

### Version Numbering
- Major (X.0.0): Breaking changes
- Minor (1.X.0): New features
- Patch (1.0.X): Bug fixes

### Release Checklist
- [ ] Update CHANGELOG.md
- [ ] Update version in `pyproject.toml`
- [ ] Run full test suite
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] GitHub Actions builds and publishes to PyPI

### PyPI Deployment
- Requires `PYPI_API_TOKEN` secret in GitHub
- Automatic via GitHub Actions on tag push
- Verify at: https://pypi.org/project/gmail-intelligence-platform/

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**IMAP Connection Fails**
- Check credentials
- Verify 2FA not blocking
- Try with app-specific password

**OAuth2 Token Expired**
- Refresh token automatically
- Invalidate and re-authenticate if needed

**Database Locked**
- Multiple processes writing simultaneously
- Use WAL (Write-Ahead Logging) mode
- Implement connection pooling

## Documentation Standards

### Docstring Format

```python
def function(param1: str, param2: int) -> dict:
    """One-line summary.

    Longer description explaining purpose, behavior,
    and any important implementation details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Dictionary with keys:
        - key1: Description
        - key2: Description

    Raises:
        ValueError: When param1 is empty
        ConnectionError: When API unavailable

    Example:
        >>> result = function("test", 5)
        >>> result['key1']
        'value1'

    Note:
        This function is expensive, call sparingly.
    """
```

## Resources

- [Python 3.10 Docs](https://docs.python.org/3.10/)
- [Gmail API](https://developers.google.com/gmail/api)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/)

---

**Last Updated**: 2026-02-07
**Maintainer**: Alan Redmond
