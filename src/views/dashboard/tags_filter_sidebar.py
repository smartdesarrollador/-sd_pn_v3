"""
Tags Filter Sidebar Widget - Panel lateral de filtro por tags para Dashboard de Estructura
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QCheckBox, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class TagsFilterSidebar(QWidget):
    """Panel lateral de filtro dinámico por tags para Dashboard"""

    tags_filter_changed = pyqtSignal(list)  # List of selected tags

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tag_checkboxes = {}  # tag_name -> QCheckBox
        self.available_tags = set()  # Tags from current results
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container frame
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-right: 1px solid #3a3a3a;
            }
        """)

        # Content layout with margins
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        header = QLabel("🏷️ Filtro por Tags")
        header.setStyleSheet("""
            QLabel {
                color: #f093fb;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(header)

        # Tag count badge
        self.tag_count_label = QLabel("(0 tags)")
        self.tag_count_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                padding: 0px 5px;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(self.tag_count_label)

        content_layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3a3a3a; max-height: 1px;")
        content_layout.addWidget(separator)

        # Scroll area for tag checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container for tag checkboxes
        self.tags_container = QWidget()
        self.tags_layout = QVBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 5, 0, 5)
        self.tags_layout.setSpacing(6)

        # Empty state
        self.empty_label = QLabel("No hay tags disponibles\n\nLos tags aparecerán\nautomáticamente al\nbuscar items")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 40px 10px;
                background-color: transparent;
            }
        """)
        self.tags_layout.addWidget(self.empty_label)
        self.tags_layout.addStretch()

        scroll.setWidget(self.tags_container)
        content_layout.addWidget(scroll, 1)

        # Action buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(6)

        # Select all button
        self.select_all_btn = QPushButton("✓ Todos")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #f093fb;
            }
            QPushButton:disabled {
                background-color: #1e1e1e;
                color: #555555;
                border-color: #2a2a2a;
            }
        """)
        self.select_all_btn.clicked.connect(self._on_select_all)
        self.select_all_btn.setEnabled(False)
        buttons_layout.addWidget(self.select_all_btn)

        # Deselect all button
        self.deselect_all_btn = QPushButton("✗ Ninguno")
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #f093fb;
            }
            QPushButton:disabled {
                background-color: #1e1e1e;
                color: #555555;
                border-color: #2a2a2a;
            }
        """)
        self.deselect_all_btn.clicked.connect(self._on_deselect_all)
        self.deselect_all_btn.setEnabled(False)
        buttons_layout.addWidget(self.deselect_all_btn)

        content_layout.addLayout(buttons_layout)

        layout.addLayout(content_layout)

    def update_tags_from_tree(self, tree_widget):
        """
        Extract unique tags from visible tree items

        Args:
            tree_widget: QTreeWidget with structure data
        """
        logger.info("Updating tags filter from tree widget")

        # Extract unique tags from all visible items
        new_tags = set()

        def collect_tags_recursive(item):
            """Recursively collect tags from item and its children"""
            # Check if item is hidden (filtered out)
            if item.isHidden():
                return

            # Get tags from item data
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and isinstance(item_data, dict):
                item_type = item_data.get('type')

                # Only collect tags from actual items, not categories
                if item_type == 'item':
                    tags_str = item_data.get('tags', '')
                    if tags_str:
                        # Split tags and clean whitespace
                        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        new_tags.update(tags)

            # Process children
            for i in range(item.childCount()):
                collect_tags_recursive(item.child(i))

        # Collect from root level
        root = tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            collect_tags_recursive(root.child(i))

        # Only update if tags changed
        if new_tags == self.available_tags:
            logger.debug("Tags unchanged, skipping update")
            return

        self.available_tags = new_tags
        logger.info(f"Found {len(new_tags)} unique tags")

        # Clear existing checkboxes
        self._clear_tag_checkboxes()

        if not new_tags:
            # Show empty state
            self.empty_label.setVisible(True)
            self.select_all_btn.setEnabled(False)
            self.deselect_all_btn.setEnabled(False)
            self.tag_count_label.setText("(0 tags)")
            return

        # Hide empty state
        self.empty_label.setVisible(False)
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)

        # Create checkbox for each unique tag (sorted alphabetically)
        for tag in sorted(new_tags):
            checkbox = QCheckBox(f"🏷️  {tag}")
            checkbox.setChecked(True)  # All tags selected by default
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #ffffff;
                    font-size: 11px;
                    spacing: 5px;
                    padding: 5px 8px;
                    background-color: #252525;
                    border-radius: 4px;
                }
                QCheckBox:hover {
                    background-color: #2a2a2a;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border: 2px solid #3a3a3a;
                    border-radius: 3px;
                    background-color: #1e1e1e;
                }
                QCheckBox::indicator:checked {
                    background-color: #f093fb;
                    border-color: #f093fb;
                }
                QCheckBox::indicator:hover {
                    border-color: #f093fb;
                }
            """)
            checkbox.stateChanged.connect(self._on_tag_checkbox_changed)

            self.tag_checkboxes[tag] = checkbox
            # Insert before stretch
            self.tags_layout.insertWidget(self.tags_layout.count() - 1, checkbox)

        # Update count
        self.tag_count_label.setText(f"({len(new_tags)} tags)")

        logger.info(f"Created {len(new_tags)} tag checkboxes")

    def _clear_tag_checkboxes(self):
        """Remove all tag checkboxes"""
        for checkbox in self.tag_checkboxes.values():
            checkbox.deleteLater()
        self.tag_checkboxes.clear()

    def _on_tag_checkbox_changed(self):
        """Handle tag checkbox state change"""
        selected_tags = self.get_selected_tags()
        logger.debug(f"Tags filter changed: {len(selected_tags)} tags selected")
        self.tags_filter_changed.emit(selected_tags)

    def _on_select_all(self):
        """Select all tag checkboxes"""
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(True)
        logger.info("All tags selected")

    def _on_deselect_all(self):
        """Deselect all tag checkboxes"""
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(False)
        logger.info("All tags deselected")

    def get_selected_tags(self):
        """Get list of currently selected tags"""
        return [tag for tag, checkbox in self.tag_checkboxes.items() if checkbox.isChecked()]

    def clear(self):
        """Clear all tags"""
        self._clear_tag_checkboxes()
        self.available_tags.clear()
        self.empty_label.setVisible(True)
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
        self.tag_count_label.setText("(0 tags)")
        logger.info("Tags filter cleared")
