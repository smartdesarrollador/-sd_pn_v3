"""
Advanced Search Engine - Main orchestrator for all search capabilities

Coordinates:
- FTS5 full-text search
- Index-based filtering
- Result ranking and aggregation
"""

import logging
from typing import List, Dict, Optional, Tuple
import time

from .fts5_manager import FTS5Manager
from .index_manager import IndexManager

logger = logging.getLogger(__name__)


class AdvancedSearchEngine:
    """
    Main search engine orchestrator

    Provides unified interface for all search modes:
    - 'smart': FTS5 with intelligent fallbacks
    - 'fts5': Pure FTS5 search
    - 'exact': Exact substring matching
    """

    def __init__(self, db_manager):
        """
        Initialize Advanced Search Engine

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.fts5 = FTS5Manager(db_manager)
        self.index_manager = IndexManager(db_manager)

        logger.info("AdvancedSearchEngine initialized")

    def search(
        self,
        query: str,
        mode: str = 'smart',
        filters: Optional[Dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Main search method

        Args:
            query: Search query string
            mode: Search mode ('smart', 'fts5', 'exact')
            filters: Optional filters dictionary
                {
                    'item_types': ['CODE', 'URL'],
                    'categories': [1, 2, 3],
                    'is_favorite': True,
                    'is_sensitive': False,
                    'date_from': '2025-01-01',
                    'date_to': '2025-12-31',
                    'min_use_count': 5
                }
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            Dictionary with search results and metadata:
            {
                'results': [...],
                'count': 50,
                'execution_time_ms': 12.5,
                'mode_used': 'fts5',
                'query': 'git push'
            }

        Examples:
            # Smart search (recommended)
            result = engine.search("git push", mode='smart')

            # FTS5 with filters
            result = engine.search(
                "docker",
                mode='fts5',
                filters={'item_types': ['CODE'], 'is_favorite': True}
            )

            # Exact substring
            result = engine.search("git st", mode='exact')
        """
        start_time = time.time()

        if not query or not query.strip():
            return {
                'results': [],
                'count': 0,
                'execution_time_ms': 0.0,
                'mode_used': mode,
                'query': query,
                'error': 'Empty query'
            }

        query = query.strip()

        # Default filters
        if filters is None:
            filters = {}

        try:
            if mode == 'smart':
                results, exec_time = self._search_smart(query, filters, limit, offset)
                mode_used = 'smart'

            elif mode == 'fts5':
                results, exec_time = self._search_fts5(query, filters, limit, offset)
                mode_used = 'fts5'

            elif mode == 'exact':
                results, exec_time = self._search_exact(query, filters, limit, offset)
                mode_used = 'exact'

            else:
                raise ValueError(f"Unknown search mode: {mode}")

            total_time = (time.time() - start_time) * 1000

            return {
                'results': results,
                'count': len(results),
                'execution_time_ms': total_time,
                'mode_used': mode_used,
                'query': query
            }

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)

            return {
                'results': [],
                'count': 0,
                'execution_time_ms': 0.0,
                'mode_used': mode,
                'query': query,
                'error': str(e)
            }

    def _search_smart(
        self,
        query: str,
        filters: Dict,
        limit: int,
        offset: int
    ) -> Tuple[List[Dict], float]:
        """
        Smart search: Try FTS5 first, fallback to exact if needed

        Args:
            query: Search query
            filters: Filter dictionary
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of (results, execution_time_ms)
        """
        # Try FTS5 first
        results, exec_time = self._search_fts5(query, filters, limit, offset)

        # If FTS5 returns no results, try exact search
        if not results:
            logger.info(f"FTS5 returned no results, falling back to exact search")
            results, exec_time = self._search_exact(query, filters, limit, offset)

        return results, exec_time

    def _search_fts5(
        self,
        query: str,
        filters: Dict,
        limit: int,
        offset: int
    ) -> Tuple[List[Dict], float]:
        """
        FTS5 search with filters

        Args:
            query: FTS5 query (supports operators)
            filters: Filter dictionary
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of (results, execution_time_ms)
        """
        # Extract filter values
        item_types = filters.get('item_types')
        categories = filters.get('categories')
        is_favorite = filters.get('is_favorite')
        is_sensitive = filters.get('is_sensitive')
        min_use_count = filters.get('min_use_count')

        # Handle date_range (new format) or legacy date_from/date_to
        date_from = None
        date_to = None
        if filters.get('date_range'):
            date_range = filters['date_range']
            date_from = date_range.get('date_from')
            date_to = date_range.get('date_to')
            # Note: FTS5 manager doesn't support 'fields' yet, defaults to created_at
        else:
            # Legacy format
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')

        # Use FTS5 with filters
        results, exec_time = self.fts5.search_with_filters(
            query=query,
            item_types=item_types,
            categories=categories,
            is_favorite=is_favorite,
            is_sensitive=is_sensitive,
            date_from=date_from,
            date_to=date_to,
            min_use_count=min_use_count,
            limit=limit
        )

        return results, exec_time

    def _search_exact(
        self,
        query: str,
        filters: Dict,
        limit: int,
        offset: int
    ) -> Tuple[List[Dict], float]:
        """
        Exact substring search using LIKE

        Args:
            query: Exact text to find
            filters: Filter dictionary
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of (results, execution_time_ms)
        """
        start_time = time.time()

        conn = self.db.connect()
        cursor = conn.cursor()

        # Build WHERE clauses
        where_clauses = ["i.is_active = 1"]
        params = []

        # Text search in label, content, tags
        search_pattern = f"%{query}%"
        where_clauses.append("""
            (LOWER(i.label) LIKE LOWER(?)
             OR LOWER(i.content) LIKE LOWER(?)
             OR LOWER(i.tags) LIKE LOWER(?))
        """)
        params.extend([search_pattern, search_pattern, search_pattern])

        # Apply filters
        if filters.get('item_types'):
            placeholders = ','.join('?' * len(filters['item_types']))
            where_clauses.append(f"i.type IN ({placeholders})")
            params.extend(filters['item_types'])

        if filters.get('categories'):
            placeholders = ','.join('?' * len(filters['categories']))
            where_clauses.append(f"i.category_id IN ({placeholders})")
            params.extend(filters['categories'])

        if filters.get('is_favorite') is not None:
            where_clauses.append("i.is_favorite = ?")
            params.append(1 if filters['is_favorite'] else 0)

        if filters.get('is_sensitive') is not None:
            where_clauses.append("i.is_sensitive = ?")
            params.append(1 if filters['is_sensitive'] else 0)

        # Handle date range filters (new format)
        if filters.get('date_range'):
            date_range = filters['date_range']
            date_from = date_range.get('date_from')
            date_to = date_range.get('date_to')
            fields = date_range.get('fields', ['created_at'])

            # Build date filter for each selected field
            date_conditions = []
            for field in fields:
                # Each field must match the date range
                field_conditions = []
                if date_from:
                    field_conditions.append(f"DATE(i.{field}) >= ?")
                    params.append(date_from)
                if date_to:
                    field_conditions.append(f"DATE(i.{field}) <= ?")
                    params.append(date_to)

                if field_conditions:
                    date_conditions.append(f"({' AND '.join(field_conditions)})")

            # Combine with OR (item matches if ANY of the date fields match)
            if date_conditions:
                where_clauses.append(f"({' OR '.join(date_conditions)})")

        if filters.get('min_use_count') is not None:
            where_clauses.append("i.use_count >= ?")
            params.append(filters['min_use_count'])

        where_sql = " AND ".join(where_clauses)

        try:
            results = cursor.execute(f"""
                SELECT
                    i.id,
                    i.category_id,
                    i.label,
                    i.content,
                    i.type,
                    i.tags,
                    i.description,
                    i.is_favorite,
                    i.is_sensitive,
                    i.use_count,
                    i.last_used,
                    i.created_at,
                    c.name as category_name,
                    c.icon as category_icon,
                    0 as rank_score
                FROM items i
                LEFT JOIN categories c ON i.category_id = c.id
                WHERE {where_sql}
                ORDER BY i.use_count DESC, i.last_used DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset]).fetchall()

            execution_time = (time.time() - start_time) * 1000

            # Convert to dicts
            columns = [
                'id', 'category_id', 'label', 'content', 'type', 'tags', 'description',
                'is_favorite', 'is_sensitive', 'use_count', 'last_used', 'created_at',
                'category_name', 'category_icon', 'rank_score'
            ]

            results_list = []
            for row in results:
                result_dict = dict(zip(columns, row))
                results_list.append(result_dict)

            logger.info(f"Exact search: '{query}' -> {len(results_list)} results in {execution_time:.2f}ms")

            return results_list, execution_time

        except Exception as e:
            logger.error(f"Exact search error: {e}")
            return [], 0.0

    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions

        Args:
            prefix: Text prefix (min 2 characters)
            limit: Maximum suggestions

        Returns:
            List of suggestion strings

        Example:
            suggestions = engine.autocomplete("git pu")
            # Returns: ["git push", "git pull"]
        """
        return self.fts5.search_autocomplete(prefix, limit=limit)

    def search_with_highlighting(
        self,
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> Dict:
        """
        Search with highlighted snippets

        Args:
            query: Search query
            filters: Optional filters
            limit: Maximum results

        Returns:
            Search result dictionary with highlighted snippets

        Example:
            result = engine.search_with_highlighting("git push")
            # result['results'][0]['label_snippet'] = '<mark>git</mark> <mark>push</mark>'
        """
        start_time = time.time()

        results, exec_time = self.fts5.search_with_highlighting(
            query=query,
            context_length=100,
            limit=limit
        )

        total_time = (time.time() - start_time) * 1000

        return {
            'results': results,
            'count': len(results),
            'execution_time_ms': total_time,
            'mode_used': 'fts5_highlighting',
            'query': query
        }

    def optimize_indexes(self):
        """
        Optimize all search indexes

        Should be run periodically or after bulk operations
        """
        logger.info("Optimizing search indexes...")

        # Optimize FTS5
        self.fts5.optimize_index()

        # Analyze B-Tree indexes
        self.index_manager.analyze_performance()

        logger.info("Search indexes optimized")

    def rebuild_indexes(self):
        """
        Rebuild all search indexes

        Use for maintenance or after major schema changes
        """
        logger.info("Rebuilding all search indexes...")

        # Rebuild FTS5
        self.fts5.rebuild_index()

        # Rebuild B-Tree indexes
        self.index_manager.rebuild_all_indexes()

        logger.info("All search indexes rebuilt")

    def get_stats(self) -> Dict:
        """
        Get search engine statistics

        Returns:
            Dictionary with stats about indexes and performance

        Example:
            stats = engine.get_stats()
            # {
            #     'fts5_items': 212,
            #     'fts5_categories': 28,
            #     'index_size_kb': 150,
            #     'indexes_count': 10
            # }
        """
        stats = {}

        # FTS5 stats
        fts5_stats = self.fts5.get_index_stats()
        stats.update(fts5_stats)

        # B-Tree index stats
        indexes = self.index_manager.get_index_info()
        stats['indexes_count'] = len(indexes)
        stats['indexes'] = indexes

        return stats
