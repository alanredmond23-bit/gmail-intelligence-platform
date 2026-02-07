"""Tests for search functionality."""

import pytest
from gmail_intelligence.search.query_builder import QueryBuilder


def test_query_builder():
    """Test query builder."""
    builder = QueryBuilder()
    query = builder.with_from("test@example.com").with_subject("urgent").build()
    assert 'from:"test@example.com"' in query
    assert 'subject:"urgent"' in query
