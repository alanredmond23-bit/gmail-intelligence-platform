"""Gmail Intelligence Platform - Unified email extraction and analysis."""

__version__ = "0.1.0"
__author__ = "Alan Redmond"

from . import core, search, analysis, storage, sync, utils

__all__ = [
    "core",
    "search",
    "analysis",
    "storage",
    "sync",
    "utils",
]
