"""
Results Table View - Display search results in a table format
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item, ItemType

import logging
logger = logging.getLogger(__name__)


class ResultsTableView(QWidget):
    """
    Table view for search results

    Displays results in a table with configurable columns:
    - Label
    - Type
    - Category
    - Tags
    - Use Count
    - Last Used
    - Description
    """

    # Signal emitted when an item is clicked
    item_clicked = pyqtSignal(object)

    # Signal emitted when edit button is clicked
    item_edit_requested = pyqtSignal(object)  # emits Item object

    # Column definitions
    COLUMNS = [
        ('Label', 250),
        ('Tipo', 80),
        ('Categoría', 150),
        ('Tags', 150),
        ('Uso', 60),
        ('Último Uso', 120),
        ('Descripción', 200),
        ('Editar', 80)  # Nueva columna
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels([col[0] for col in self.COLUMNS])

        # Set column widths
        header = self.table.horizontalHeader()
        for i, (_, width) in enumerate(self.COLUMNS):
            self.table.setColumnWidth(i, width)

        # Header properties
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # Style
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                gridline-color: #2a2a2a;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #f093fb;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #2a2a2a;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item:alternate {
                background-color: #1a1a1a;
            }
        """)

        # Connect signals
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)

        layout.addWidget(self.table)

    def update_results(self, results):
        """
        Update the table with new results

        Args:
            results: List of result dictionaries from AdvancedSearchEngine
        """
        logger.info(f"Updating table view with {len(results)} results")

        # Clear table
        self.table.setRowCount(0)
        self.results = results

        if not results:
            return

        # Set row count
        self.table.setRowCount(len(results))

        # Populate table
        for row, result in enumerate(results):
            try:
                # Label
                label_item = QTableWidgetItem(result.get('label', ''))
                label_item.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
                self.table.setItem(row, 0, label_item)

                # Type
                item_type = result.get('type', 'TEXT')
                type_icon = self._get_type_icon(item_type)
                type_item = QTableWidgetItem(f"{type_icon} {item_type}")
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, type_item)

                # Category
                category_icon = result.get('category_icon', '📁')
                category_name = result.get('category_name', 'Sin categoría')
                category_item = QTableWidgetItem(f"{category_icon} {category_name}")
                self.table.setItem(row, 2, category_item)

                # Tags
                tags = result.get('tags', '') or ''
                tags_item = QTableWidgetItem(tags)
                tags_item.setForeground(QColor('#f093fb'))
                self.table.setItem(row, 3, tags_item)

                # Use count
                use_count = result.get('use_count', 0)
                use_item = QTableWidgetItem(str(use_count))
                use_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, use_item)

                # Last used
                last_used = result.get('last_used')
                last_used_str = self._format_date(last_used) if last_used else 'Nunca'
                last_used_item = QTableWidgetItem(last_used_str)
                last_used_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 5, last_used_item)

                # Description
                description = result.get('description', '') or ''
                # Truncate long descriptions
                if len(description) > 100:
                    description = description[:97] + '...'
                desc_item = QTableWidgetItem(description)
                desc_item.setForeground(QColor('#888888'))
                self.table.setItem(row, 6, desc_item)

                # Edit button
                edit_btn = QPushButton('✏️ Editar')
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007acc;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 10pt;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                    QPushButton:pressed {
                        background-color: #004578;
                    }
                """)
                edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                # Store row index and result data in button
                edit_btn.setProperty('row', row)
                edit_btn.setProperty('result_data', result)
                edit_btn.clicked.connect(lambda checked, r=result: self._on_edit_clicked(r))
                self.table.setCellWidget(row, 7, edit_btn)

                # Store result data in first column for retrieval
                label_item.setData(Qt.ItemDataRole.UserRole, result)

            except Exception as e:
                logger.error(f"Error creating table row {row}: {e}", exc_info=True)

        # Resize rows to content
        self.table.resizeRowsToContents()

        logger.debug(f"Table populated with {len(results)} rows")

    def clear_results(self):
        """Clear all results"""
        self.table.setRowCount(0)
        self.results.clear()

    def _on_cell_double_clicked(self, row, column):
        """Handle cell double click"""
        try:
            # Get result data from first column
            label_item = self.table.item(row, 0)
            if not label_item:
                return

            result = label_item.data(Qt.ItemDataRole.UserRole)
            if not result:
                return

            # Convert to Item object
            item = Item(
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

            logger.debug(f"Item double-clicked in table: {item.label}")
            self.item_clicked.emit(item)

        except Exception as e:
            logger.error(f"Error handling cell double click: {e}", exc_info=True)

    def _on_edit_clicked(self, result):
        """Handle edit button click"""
        try:
            logger.info(f"Edit button clicked for item: {result.get('label', 'Unknown')}")

            # Convert result dict to Item object
            item = Item(
                item_id=str(result.get('id', '')),
                label=result.get('label', ''),
                content=result.get('content', ''),
                item_type=result.get('type', 'TEXT').lower(),
                description=result.get('description'),
                tags=result.get('tags', '').split(',') if result.get('tags') else [],
                is_favorite=bool(result.get('is_favorite', 0)),
                is_sensitive=bool(result.get('is_sensitive', 0)),
                is_active=bool(result.get('is_active', 1)),
                is_archived=bool(result.get('is_archived', 0))
            )

            # Add category_id for ItemEditorDialog
            item.category_id = result.get('category_id')

            logger.debug(f"Emitting item_edit_requested for: {item.label}")
            self.item_edit_requested.emit(item)

        except Exception as e:
            logger.error(f"Error handling edit button click: {e}", exc_info=True)

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

    def _format_date(self, date_str):
        """Format date string for display"""
        try:
            if not date_str:
                return 'Nunca'

            # Parse date
            dt = datetime.fromisoformat(date_str.replace(' ', 'T'))

            # Format based on recency
            now = datetime.now()
            diff = now - dt

            if diff.days == 0:
                return 'Hoy'
            elif diff.days == 1:
                return 'Ayer'
            elif diff.days < 7:
                return f'Hace {diff.days} días'
            elif diff.days < 30:
                weeks = diff.days // 7
                return f'Hace {weeks} semana{"s" if weeks > 1 else ""}'
            else:
                return dt.strftime('%d/%m/%Y')

        except Exception as e:
            logger.debug(f"Error formatting date '{date_str}': {e}")
            return date_str or 'Nunca'

    def get_selected_items(self):
        """Get currently selected items"""
        selected_rows = self.table.selectionModel().selectedRows()
        items = []

        for index in selected_rows:
            row = index.row()
            label_item = self.table.item(row, 0)
            if label_item:
                result = label_item.data(Qt.ItemDataRole.UserRole)
                if result:
                    items.append(result)

        return items
