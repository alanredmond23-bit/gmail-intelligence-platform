# Contributing to Gmail Intelligence Platform

Thank you for your interest in contributing! This document provides guidelines for development, testing, and contributions.

## Development Setup

### Prerequisites
- Python 3.10+
- Git
- pip or conda

### Installation for Development

```bash
# Clone repository
git clone https://github.com/alanredmond/gmail-intelligence-platform.git
cd gmail-intelligence-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gmail_intelligence --cov-report=html

# Run specific test file
pytest tests/test_imap_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/gmail_intelligence tests/

# Check formatting
black --check src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/gmail_intelligence
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-name
```

### 2. Make Changes

- Write code following the style of existing modules
- Add docstrings to all public functions
- Include type hints
- Write tests for new functionality

### 3. Test Your Changes

```bash
# Run tests
pytest

# Check formatting and linting
black --check .
ruff check .
mypy src/
```

### 4. Commit

```bash
git add <modified-files>
git commit -m "Clear description of changes

Longer explanation if needed. Reference any related issues.
Fixes #123"
```

### 5. Push & Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear title
- Description of changes
- Reference to related issues
- Test results screenshot (if applicable)

## Code Style Guidelines

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function parameters and returns
- Maximum line length: 100 characters
- Use docstrings for all public functions

### Example Function

```python
def extract_entities(text: str, model: str = "gpt-4") -> dict[str, list[str]]:
    """Extract entities from text using specified model.

    Args:
        text: Input text to analyze
        model: Model to use (default: gpt-4)

    Returns:
        Dictionary mapping entity types to lists of found entities

    Example:
        >>> extract_entities("John works at Acme Corp")
        {'PERSON': ['John'], 'ORGANIZATION': ['Acme Corp']}
    """
    # Implementation here
    pass
```

### Module Organization

```python
# Imports (standard library, then third-party, then local)
import asyncio
from pathlib import Path
from typing import Optional

import openai
from pydantic import BaseModel

from gmail_intelligence.utils import logger

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Classes
class MyClass:
    """Class documentation."""
    pass

# Functions
def my_function() -> str:
    """Function documentation."""
    pass
```

## Testing Guidelines

### Test Structure

```python
import pytest
from gmail_intelligence.core.imap_client import IMAPClient

@pytest.fixture
def imap_client():
    """Fixture for IMAP client."""
    return IMAPClient("imap.gmail.com")

def test_imap_client_connect(imap_client):
    """Test IMAP connection."""
    assert imap_client.host == "imap.gmail.com"

@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await async_function()
    assert result is not None
```

### Test Requirements
- One test file per module
- Test file names: `test_<module_name>.py`
- Fixtures in `conftest.py`
- Minimum 80% code coverage
- All tests passing before merge

## Commit Message Guidelines

```
Type: Short description (50 chars max)

Longer explanation of the change (wrapped at 72 chars).
Explain what, why, and how.

Fixes #123
Relates to #456
```

**Types**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting, missing semicolons, etc
- `refactor:` Code refactoring without feature changes
- `test:` Adding tests
- `chore:` Build, dependencies, etc

## Pull Request Process

1. Ensure all tests pass locally: `pytest`
2. Ensure code quality: `black` and `ruff`
3. Update documentation if needed
4. Add entry to CHANGELOG.md
5. Link related issues in PR description
6. Request review from maintainers
7. Address review comments
8. Squash commits if requested

## Reporting Issues

### Bug Reports
Include:
- Python version
- Reproduction steps
- Expected vs actual behavior
- Error traceback (if applicable)
- System information (OS, Gmail type, etc)

### Feature Requests
Include:
- Use case / motivation
- Proposed solution
- Alternatives considered
- Additional context

## Questions?

- Open an Issue for bugs and features
- Start a Discussion for questions
- Check existing issues/discussions first

---

**Thank you for contributing!** 🎉
