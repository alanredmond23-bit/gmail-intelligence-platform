"""Tests for IMAP client."""

import pytest
from gmail_intelligence.core.imap_client import IMAPClient


def test_imap_client_init():
    """Test IMAP client initialization."""
    client = IMAPClient("imap.gmail.com")
    assert client.host == "imap.gmail.com"
    assert client.port == 993
