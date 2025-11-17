"""
Index Manager - Manage B-Tree indexes for search optimization

Handles creation and maintenance of traditional SQL indexes
to complement FTS5 search performance.
"""

import sqlite3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class IndexManager:
    """Manager for B-Tree indexes"""

    def __init__(self, db_manager):
        """
        Initialize Index Manager

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def create_all_indexes(self):
        """
        Create all search-related B-Tree indexes

        Indexes created:
        - Label search (case-insensitive)
        - Tags search
        - Composite indexes for filtering
        - Usage/frequency indexes
        - Date indexes
        - Type indexes
        """
        indexes_sql = [
            # Label search (case-insensitive)
            """
            CREATE INDEX IF NOT EXISTS idx_items_label_lower
            ON items(LOWER(label))
            """,

            # Tags search
            """
            CREATE INDEX IF NOT EXISTS idx_items_tags
            ON items(tags)
            """,

            # Composite index for common filters
            """
            CREATE INDEX IF NOT EXISTS idx_items_search_composite
            ON items(category_id, is_active, is_favorite)
            """,

            # Usage-based ordering
            """
            CREATE INDEX IF NOT EXISTS idx_items_usage_search
            ON items(use_count DESC, last_used DESC)
            """,

            # Date-based ordering
            """
            CREATE INDEX IF NOT EXISTS idx_items_dates_search
            ON items(created_at DESC)
            """,

            # Type filtering
            """
            CREATE INDEX IF NOT EXISTS idx_items_type_search
            ON items(type)
            """,

            # State filtering
            """
            CREATE INDEX IF NOT EXISTS idx_items_state_search
            ON items(is_active, is_archived)
            """,

            # Favorite items
            """
            CREATE INDEX IF NOT EXISTS idx_items_favorite
            ON items(is_favorite, favorite_order)
            """,

            # Category name for search
            """
            CREATE INDEX IF NOT EXISTS idx_categories_name_lower
            ON categories(LOWER(name))
            """,
        ]

        cursor = self.db.connection.cursor()

        created_count = 0
        for index_sql in indexes_sql:
            try:
                cursor.execute(index_sql)
                created_count += 1
            except sqlite3.OperationalError as e:
                logger.warning(f"Index creation skipped: {e}")

        self.db.connection.commit()

        logger.info(f"Created/verified {created_count} B-Tree indexes for search")

        return created_count

    def analyze_performance(self):
        """
        Analyze and update index statistics

        Runs ANALYZE command to update SQLite query planner statistics
        Should be run periodically (e.g., after bulk operations)
        """
        cursor = self.db.connection.cursor()

        try:
            cursor.execute("ANALYZE")
            self.db.connection.commit()

            logger.info("Index statistics updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to analyze indexes: {e}")
            return False

    def get_index_info(self) -> List[Dict]:
        """
        Get information about existing indexes

        Returns:
            List of index information dictionaries

        Example:
            [
                {
                    'name': 'idx_items_label_lower',
                    'table': 'items',
                    'unique': False,
                    'columns': ['LOWER(label)']
                },
                ...
            ]
        """
        cursor = self.db.connection.cursor()

        try:
            # Get all indexes
            cursor.execute("""
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type = 'index'
                  AND name LIKE 'idx_%search%'
                ORDER BY name
            """)

            indexes = []
            for name, table, sql in cursor.fetchall():
                indexes.append({
                    'name': name,
                    'table': table,
                    'sql': sql
                })

            return indexes

        except Exception as e:
            logger.error(f"Failed to get index info: {e}")
            return []

    def drop_all_search_indexes(self):
        """
        Drop all search-related indexes

        WARNING: This will slow down searches until indexes are recreated
        Use only for maintenance or migration purposes
        """
        cursor = self.db.connection.cursor()

        # Get all search index names
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'index'
              AND name LIKE 'idx_%search%'
        """)

        index_names = [row[0] for row in cursor.fetchall()]

        dropped_count = 0
        for index_name in index_names:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
                dropped_count += 1
                logger.info(f"Dropped index: {index_name}")
            except Exception as e:
                logger.error(f"Failed to drop index {index_name}: {e}")

        self.db.connection.commit()

        logger.info(f"Dropped {dropped_count} search indexes")

        return dropped_count

    def rebuild_all_indexes(self):
        """
        Rebuild all search indexes

        Drops and recreates all indexes for maintenance
        """
        logger.info("Starting index rebuild...")

        # Drop existing indexes
        dropped = self.drop_all_search_indexes()
        logger.info(f"Dropped {dropped} indexes")

        # Create indexes again
        created = self.create_all_indexes()
        logger.info(f"Created {created} indexes")

        # Update statistics
        self.analyze_performance()

        logger.info("Index rebuild completed successfully")

        return True
