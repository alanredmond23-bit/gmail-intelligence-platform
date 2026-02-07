"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_email():
    """Fixture providing a sample email for testing."""
    return {
        "id": "test-123",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test Email",
        "body": "This is a test email.",
        "timestamp": "2026-01-01T12:00:00Z",
    }
