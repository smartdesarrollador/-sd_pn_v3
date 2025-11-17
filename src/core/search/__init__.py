"""
Search Module - Advanced search capabilities for Widget Sidebar

This module provides:
- FTS5Manager: Full-text search with SQLite FTS5
- IndexManager: B-Tree index management
- FuzzySearchEngine: Levenshtein-based fuzzy search
- SearchCache: LRU cache for search results
- SearchHistoryManager: Search history tracking
- AdvancedSearchEngine: Main orchestrator
"""

from .fts5_manager import FTS5Manager
from .index_manager import IndexManager
from .advanced_search_engine import AdvancedSearchEngine

__all__ = [
    'FTS5Manager',
    'IndexManager',
    'AdvancedSearchEngine',
]
