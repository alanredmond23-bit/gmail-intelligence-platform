"""Tests for email parser."""

import pytest
from gmail_intelligence.core.email_parser import EmailParser


def test_email_parser_init():
    """Test email parser initialization."""
    parser = EmailParser()
    assert parser is not None
