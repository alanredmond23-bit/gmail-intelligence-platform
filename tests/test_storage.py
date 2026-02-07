"""Tests for storage functionality."""

import pytest
from pathlib import Path
from gmail_intelligence.storage.file_manager import FileManager


def test_file_manager_init(tmp_path):
    """Test file manager initialization."""
    manager = FileManager(tmp_path)
    assert manager.base_path == tmp_path
    assert tmp_path.exists()
