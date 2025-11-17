"""
Search Engine for Widget Sidebar
Provides filtering and searching functionality for items across categories
"""

from typing import List, Optional
import re
from models.item import Item
from models.category import Category


class SearchEngine:
    """
    Search engine for filtering items across categories
    Performs case-insensitive search on item labels and content
    """

    def __init__(self):
        """Initialize search engine"""
        pass

    def search(self, query: str, categories: List[Category]) -> List[Item]:
        """
        Search for items matching the query across all categories

        Args:
            query: Search query string (case-insensitive)
            categories: List of categories to search through

        Returns:
            List of items that match the query
        """
        if not query or not query.strip():
            # Return all items if query is empty
            return self._get_all_items(categories)

        query = query.strip().lower()
        matching_items = []

        for category in categories:
            if not category.is_active:
                continue

            for item in category.items:
                # Search in label, content, and tags
                label_match = query in item.label.lower()
                content_match = query in item.content.lower()

                # Search in tags
                tags_match = False
                if item.tags:
                    for tag in item.tags:
                        if query in tag.lower():
                            tags_match = True
                            break

                if label_match or content_match or tags_match:
                    matching_items.append(item)

        return matching_items

    def search_in_category(self, query: str, category: Category) -> List[Item]:
        """
        Search for items matching the query within a specific category

        Args:
            query: Search query string (case-insensitive)
            category: Category to search in

        Returns:
            List of items that match the query in the category
        """
        if not query or not query.strip():
            return category.items

        query = query.strip().lower()
        matching_items = []

        for item in category.items:
            # Search in label, content, and tags
            label_match = query in item.label.lower()
            content_match = query in item.content.lower()

            # Search in tags
            tags_match = False
            if item.tags:
                for tag in item.tags:
                    if query in tag.lower():
                        tags_match = True
                        break

            if label_match or content_match or tags_match:
                matching_items.append(item)

        return matching_items

    def highlight_matches(self, text: str, query: str) -> str:
        """
        Highlight matching text with HTML tags

        Args:
            text: Original text
            query: Search query to highlight

        Returns:
            Text with <mark> tags around matches
        """
        if not query or not query.strip():
            return text

        query = query.strip()

        # Escape special regex characters
        escaped_query = re.escape(query)

        # Case-insensitive replacement with <mark> tags
        pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
        highlighted = pattern.sub(r'<mark>\1</mark>', text)

        return highlighted

    def _get_all_items(self, categories: List[Category]) -> List[Item]:
        """
        Get all items from all active categories

        Args:
            categories: List of categories

        Returns:
            List of all items
        """
        all_items = []
        for category in categories:
            if category.is_active:
                all_items.extend(category.items)
        return all_items

    def get_search_stats(self, query: str, categories: List[Category]) -> dict:
        """
        Get statistics about search results

        Args:
            query: Search query
            categories: List of categories to search

        Returns:
            Dictionary with search statistics
        """
        results = self.search(query, categories)

        # Count matches by category
        category_counts = {}
        for item in results:
            # Find which category this item belongs to
            for category in categories:
                if item in category.items:
                    category_counts[category.name] = category_counts.get(category.name, 0) + 1
                    break

        return {
            'total_results': len(results),
            'query': query,
            'category_breakdown': category_counts
        }
