"""
FTS5 Manager - Full-Text Search engine using SQLite FTS5

Provides ultra-fast text search with:
- Basic search with BM25 ranking
- Boolean operators (AND, OR, NOT)
- Wildcards (*)
- Phrase search ("exact phrase")
- Proximity search (NEAR)
- Column filters (label:query)
- Highlighting with snippets
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
import time

logger = logging.getLogger(__name__)


class FTS5Manager:
    """Manager for Full-Text Search using SQLite FTS5"""

    def __init__(self, db_manager):
        """
        Initialize FTS5 Manager

        Args:
            db_manager: Database manager instance with connection
        """
        self.db = db_manager
        self.supported_operators = {
            'AND', 'OR', 'NOT', 'NEAR',
            '*',  # Wildcard
            '"',  # Phrase search
            ':',  # Column filter
        }

    def search_basic(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict], float]:
        """
        Basic FTS5 search with BM25 ranking

        Args:
            query: Search query (e.g., "git push")
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            Tuple of (results, execution_time_ms)

        Example:
            results, time = fts5.search_basic("git push", limit=50)
        """
        start_time = time.time()

        conn = self.db.connect()
        cursor = conn.cursor()

        try:
            results = cursor.execute("""
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
                    c.color as category_color,
                    bm25(items_fts, 10.0, 5.0, 3.0, 2.0, 1.0) as rank_score
                FROM items_fts
                JOIN items i ON items_fts.rowid = i.id
                LEFT JOIN categories c ON i.category_id = c.id
                WHERE items_fts MATCH ?
                  AND i.is_active = 1
                ORDER BY rank_score
                LIMIT ? OFFSET ?
            """, (query, limit, offset)).fetchall()

            execution_time = (time.time() - start_time) * 1000

            # Convert to list of dicts
            columns = [
                'id', 'category_id', 'label', 'content', 'type', 'tags', 'description',
                'is_favorite', 'is_sensitive', 'use_count', 'last_used', 'created_at',
                'category_name', 'category_icon', 'category_color', 'rank_score'
            ]

            results_list = []
            for row in results:
                result_dict = dict(zip(columns, row))
                results_list.append(result_dict)

            logger.info(f"FTS5 basic search: '{query}' -> {len(results_list)} results in {execution_time:.2f}ms")

            return results_list, execution_time

        except sqlite3.OperationalError as e:
            logger.error(f"FTS5 search error: {e}")
            return [], 0.0

    def search_with_operators(
        self,
        query: str,
        limit: int = 100
    ) -> Tuple[List[Dict], float]:
        """
        Advanced search with boolean operators

        Supported operators:
        - AND: "git AND push"
        - OR: "git OR svn"
        - NOT: "git NOT pull"
        - Wildcards: "python*"
        - Phrases: '"git push"'
        - Proximity: 'NEAR(git push, 5)'
        - Column filters: 'label:git' or 'tags:python'

        Args:
            query: Query with operators
            limit: Maximum results

        Returns:
            Tuple of (results, execution_time_ms)

        Examples:
            # Boolean AND
            results, _ = fts5.search_with_operators("git AND push")

            # Wildcard
            results, _ = fts5.search_with_operators("python*")

            # Phrase
            results, _ = fts5.search_with_operators('"git push origin"')

            # Column filter
            results, _ = fts5.search_with_operators("label:docker")
        """
        return self.search_basic(query, limit=limit)

    def search_with_highlighting(
        self,
        query: str,
        context_length: int = 50,
        limit: int = 100
    ) -> Tuple[List[Dict], float]:
        """
        Search with highlighted snippets

        Args:
            query: Search query
            context_length: Characters of context around match
            limit: Maximum results

        Returns:
            Tuple of (results with snippets, execution_time_ms)

        Result structure:
            {
                'id': 123,
                'label': 'git push',
                'label_snippet': '<mark>git</mark> <mark>push</mark>',
                'content_snippet': 'Push commits to <mark>remote</mark>...',
                'rank_score': -5.2,
                ...
            }
        """
        start_time = time.time()

        conn = self.db.connect()
        cursor = conn.cursor()

        try:
            results = cursor.execute("""
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
                    c.name as category_name,
                    c.icon as category_icon,
                    snippet(items_fts, 1, '<mark>', '</mark>', '...', ?) as label_snippet,
                    snippet(items_fts, 2, '<mark>', '</mark>', '...', ?) as content_snippet,
                    bm25(items_fts) as rank_score
                FROM items_fts
                JOIN items i ON items_fts.rowid = i.id
                LEFT JOIN categories c ON i.category_id = c.id
                WHERE items_fts MATCH ?
                  AND i.is_active = 1
                ORDER BY rank_score
                LIMIT ?
            """, (context_length, context_length, query, limit)).fetchall()

            execution_time = (time.time() - start_time) * 1000

            # Convert to dicts
            columns = [
                'id', 'category_id', 'label', 'content', 'type', 'tags', 'description',
                'is_favorite', 'is_sensitive', 'use_count', 'last_used',
                'category_name', 'category_icon', 'label_snippet', 'content_snippet', 'rank_score'
            ]

            results_list = []
            for row in results:
                result_dict = dict(zip(columns, row))
                results_list.append(result_dict)

            logger.info(f"FTS5 search with highlighting: '{query}' -> {len(results_list)} results in {execution_time:.2f}ms")

            return results_list, execution_time

        except sqlite3.OperationalError as e:
            logger.error(f"FTS5 highlighting error: {e}")
            return [], 0.0

    def search_autocomplete(
        self,
        prefix: str,
        field: str = 'label',
        limit: int = 10
    ) -> List[str]:
        """
        Autocomplete suggestions using FTS5 prefix search

        Args:
            prefix: Text prefix (e.g., "git pu")
            field: Field to search ('label', 'tags', 'content')
            limit: Maximum suggestions

        Returns:
            List of suggestion strings

        Example:
            suggestions = fts5.search_autocomplete("git pu")
            # Returns: ["git push", "git pull", "git publish"]
        """
        if not prefix or len(prefix) < 2:
            return []

        conn = self.db.connect()
        cursor = conn.cursor()

        # Query with wildcard for prefix
        fts_query = f"{field}:{prefix}*"

        try:
            results = cursor.execute("""
                SELECT DISTINCT i.label
                FROM items_fts
                JOIN items i ON items_fts.rowid = i.id
                WHERE items_fts MATCH ?
                  AND i.is_active = 1
                ORDER BY bm25(items_fts)
                LIMIT ?
            """, (fts_query, limit)).fetchall()

            suggestions = [row[0] for row in results]

            logger.debug(f"Autocomplete: '{prefix}' -> {len(suggestions)} suggestions")

            return suggestions

        except sqlite3.OperationalError as e:
            logger.error(f"Autocomplete error: {e}")
            return []

    def search_with_filters(
        self,
        query: str,
        item_types: Optional[List[str]] = None,
        categories: Optional[List[int]] = None,
        is_favorite: Optional[bool] = None,
        is_sensitive: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_use_count: Optional[int] = None,
        limit: int = 100
    ) -> Tuple[List[Dict], float]:
        """
        FTS5 search combined with SQL filters

        Combines power of full-text search with traditional filters

        Args:
            query: FTS5 search query
            item_types: Filter by types (e.g., ['CODE', 'URL'])
            categories: Filter by category IDs
            is_favorite: Filter favorites only
            is_sensitive: Filter sensitive items
            date_from: Created after date (ISO format)
            date_to: Created before date (ISO format)
            min_use_count: Minimum usage count
            limit: Maximum results

        Returns:
            Tuple of (filtered results, execution_time_ms)

        Example:
            results, time = fts5.search_with_filters(
                query="git",
                item_types=['CODE'],
                is_favorite=True,
                min_use_count=5
            )
        """
        start_time = time.time()

        # Build WHERE clauses
        where_clauses = ["items_fts MATCH ?", "i.is_active = 1"]
        params = [query]

        if item_types:
            placeholders = ','.join('?' * len(item_types))
            where_clauses.append(f"i.type IN ({placeholders})")
            params.extend(item_types)

        if categories:
            placeholders = ','.join('?' * len(categories))
            where_clauses.append(f"i.category_id IN ({placeholders})")
            params.extend(categories)

        if is_favorite is not None:
            where_clauses.append("i.is_favorite = ?")
            params.append(1 if is_favorite else 0)

        if is_sensitive is not None:
            where_clauses.append("i.is_sensitive = ?")
            params.append(1 if is_sensitive else 0)

        if date_from:
            where_clauses.append("DATE(i.created_at) >= ?")
            params.append(date_from)

        if date_to:
            where_clauses.append("DATE(i.created_at) <= ?")
            params.append(date_to)

        if min_use_count is not None:
            where_clauses.append("i.use_count >= ?")
            params.append(min_use_count)

        where_sql = " AND ".join(where_clauses)

        conn = self.db.connect()
        cursor = conn.cursor()

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
                    bm25(items_fts) as rank_score
                FROM items_fts
                JOIN items i ON items_fts.rowid = i.id
                LEFT JOIN categories c ON i.category_id = c.id
                WHERE {where_sql}
                ORDER BY rank_score
                LIMIT ?
            """, params + [limit]).fetchall()

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

            filter_info = {
                'types': item_types,
                'categories': categories,
                'favorite': is_favorite,
                'sensitive': is_sensitive
            }

            logger.info(f"FTS5 filtered search: '{query}' with filters {filter_info} -> {len(results_list)} results in {execution_time:.2f}ms")

            return results_list, execution_time

        except sqlite3.OperationalError as e:
            logger.error(f"FTS5 filtered search error: {e}")
            return [], 0.0

    def rebuild_index(self):
        """
        Rebuild FTS5 index completely

        Use this if index gets corrupted or after major data changes
        """
        conn = self.db.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO items_fts(items_fts) VALUES('rebuild');")
            cursor.execute("INSERT INTO categories_fts(categories_fts) VALUES('rebuild');")

            conn.commit()

            logger.info("FTS5 index rebuilt successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to rebuild FTS5 index: {e}")
            return False

    def optimize_index(self):
        """
        Optimize FTS5 index (merge segments)

        Run periodically to maintain search performance
        Recommended: after bulk inserts/updates
        """
        conn = self.db.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO items_fts(items_fts) VALUES('optimize');")
            cursor.execute("INSERT INTO categories_fts(categories_fts) VALUES('optimize');")

            conn.commit()

            logger.info("FTS5 index optimized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to optimize FTS5 index: {e}")
            return False

    def get_index_stats(self) -> Dict:
        """
        Get FTS5 index statistics

        Returns:
            Dictionary with index stats

        Example:
            stats = fts5.get_index_stats()
            # {
            #     'items_indexed': 212,
            #     'categories_indexed': 28,
            #     'index_size_kb': 150
            # }
        """
        conn = self.db.connect()
        cursor = conn.cursor()

        stats = {}

        try:
            # Count items (using original table to avoid FTS5 issues)
            cursor.execute("SELECT COUNT(*) FROM items WHERE is_active = 1")
            stats['items_indexed'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM categories WHERE is_active = 1")
            stats['categories_indexed'] = cursor.fetchone()[0]

            # Get database page info for size estimation
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]

            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]

            stats['index_size_kb'] = (page_count * page_size) / 1024

            return stats

        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {
                'items_indexed': 0,
                'categories_indexed': 0,
                'index_size_kb': 0
            }
