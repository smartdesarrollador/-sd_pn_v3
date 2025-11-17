"""
Results Tree View - Display search results in a hierarchical tree grouped by category
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item, ItemType

import logging
logger = logging.getLogger(__name__)


class ResultsTreeView(QWidget):
    """
    Tree view for search results

    Groups results hierarchically:
    - Level 1: Categories (with count)
    - Level 2: Items within each category

    Features:
    - Expandable/collapsible categories
    - Category badges with icons
    - Item count per category
    - Color-coded by item type
    """

    # Signal emitted when an item is clicked
    item_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self.category_items = {}  # category_id -> QTreeWidgetItem

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(['Nombre', 'Tipo', 'Tags', 'Uso'])

        # Header properties
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Tree properties
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setAlternatingRowColors(False)

        # Style
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 6px 0;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: #2a2a2a;
            }
            QTreeWidget::item:selected {
                background-color: #f093fb;
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: #1e1e1e;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: none;
                border-left: 1px solid #3a3a3a;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: none;
                border-left: 1px solid #3a3a3a;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Connect signals
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree)

    def update_results(self, results):
        """
        Update the tree with new results

        Args:
            results: List of result dictionaries from AdvancedSearchEngine
        """
        logger.info(f"Updating tree view with {len(results)} results")

        # Clear tree
        self.tree.clear()
        self.category_items.clear()
        self.results = results

        if not results:
            # Show empty state
            empty_item = QTreeWidgetItem(self.tree)
            empty_item.setText(0, "No hay resultados")
            empty_item.setForeground(0, QColor('#888888'))
            return

        # Group results by category
        category_groups = defaultdict(list)
        for result in results:
            category_id = result.get('category_id', 0)
            category_groups[category_id].append(result)

        # Create category nodes
        for category_id, category_results in sorted(category_groups.items()):
            try:
                # Get category info from first item
                first_result = category_results[0]
                category_name = first_result.get('category_name', 'Sin categoría')
                category_icon = first_result.get('category_icon', '📁')

                # Create category item
                category_item = QTreeWidgetItem(self.tree)
                category_item.setText(0, f"{category_icon} {category_name}")
                category_item.setText(3, f"{len(category_results)} items")

                # Style category item
                font = QFont('Segoe UI', 11, QFont.Weight.Bold)
                category_item.setFont(0, font)
                category_item.setForeground(0, QColor('#f093fb'))
                category_item.setForeground(3, QColor('#888888'))

                # Mark as category (not selectable for item click)
                category_item.setData(0, Qt.ItemDataRole.UserRole, {'is_category': True})

                # Store reference
                self.category_items[category_id] = category_item

                # Add items to category
                for result in category_results:
                    self._add_item_to_category(category_item, result)

                # Expand category by default
                category_item.setExpanded(True)

            except Exception as e:
                logger.error(f"Error creating category node: {e}", exc_info=True)

        logger.debug(f"Tree populated with {len(category_groups)} categories")

    def _add_item_to_category(self, category_item, result):
        """Add an item to a category node"""
        try:
            # Create item node
            item_node = QTreeWidgetItem(category_item)

            # Label
            label = result.get('label', '')
            item_node.setText(0, label)

            # Type with icon
            item_type = result.get('type', 'TEXT')
            type_icon = self._get_type_icon(item_type)
            item_node.setText(1, f"{type_icon} {item_type}")

            # Tags
            tags = result.get('tags', '') or ''
            if tags:
                # Truncate long tags
                if len(tags) > 30:
                    tags = tags[:27] + '...'
                item_node.setText(2, tags)
                item_node.setForeground(2, QColor('#f093fb'))

            # Use count
            use_count = result.get('use_count', 0)
            item_node.setText(3, str(use_count))
            item_node.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)

            # Store result data
            item_node.setData(0, Qt.ItemDataRole.UserRole, result)

            # Color code by type
            color = self._get_type_color(item_type)
            if color:
                item_node.setForeground(0, QColor(color))

            # Mark as sensitive if applicable
            if result.get('is_sensitive'):
                item_node.setText(1, f"{type_icon} {item_type} 🔒")

            # Mark as favorite if applicable
            if result.get('is_favorite'):
                item_node.setText(0, f"⭐ {label}")

        except Exception as e:
            logger.error(f"Error adding item to category: {e}", exc_info=True)

    def clear_results(self):
        """Clear all results"""
        self.tree.clear()
        self.category_items.clear()
        self.results.clear()

    def _on_item_double_clicked(self, item, column):
        """Handle item double click"""
        try:
            # Check if it's a category or item
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if not data or data.get('is_category'):
                # It's a category, just toggle expand
                item.setExpanded(not item.isExpanded())
                return

            # It's an item, emit signal
            result = data

            # Convert to Item object
            item_obj = Item(
                item_id=str(result.get('id', '')),
                label=result.get('label', ''),
                content=result.get('content', ''),
                item_type=result.get('type', 'TEXT').lower(),  # Convert to lowercase for ItemType enum
                description=result.get('description'),
                tags=result.get('tags', '').split(',') if result.get('tags') else [],
                is_favorite=bool(result.get('is_favorite', 0)),
                is_sensitive=bool(result.get('is_sensitive', 0)),
                is_active=True
            )

            logger.debug(f"Item double-clicked in tree: {item_obj.label}")
            self.item_clicked.emit(item_obj)

        except Exception as e:
            logger.error(f"Error handling item double click: {e}", exc_info=True)

    def _get_type_icon(self, item_type):
        """Get icon for item type"""
        icons = {
            'CODE': '💻',
            'URL': '🌐',
            'PATH': '📁',
            'TEXT': '📝',
            'IMAGE': '🖼️',
            'PDF': '📄',
            'AUDIO': '🎵',
            'VIDEO': '🎬',
            'ARCHIVE': '📦'
        }
        return icons.get(item_type, '📄')

    def _get_type_color(self, item_type):
        """Get color for item type"""
        colors = {
            'CODE': '#4ec9b0',  # Teal
            'URL': '#569cd6',   # Blue
            'PATH': '#dcdcaa',  # Yellow
            'TEXT': '#d4d4d4',  # White
            'IMAGE': '#c586c0', # Purple
            'PDF': '#ce9178',   # Orange
        }
        return colors.get(item_type)

    def expand_all(self):
        """Expand all categories"""
        self.tree.expandAll()

    def collapse_all(self):
        """Collapse all categories"""
        self.tree.collapseAll()

    def get_selected_items(self):
        """Get currently selected items"""
        selected_items = self.tree.selectedItems()
        results = []

        for item in selected_items:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and not data.get('is_category'):
                results.append(data)

        return results
