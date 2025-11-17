"""
Content Panel View - Expandable panel with items
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from models.item import Item
from views.widgets.item_widget import ItemButton
from views.widgets.search_bar import SearchBar
from core.search_engine import SearchEngine

# Get logger
logger = logging.getLogger(__name__)


class ContentPanel(QWidget):
    """Expandable content panel displaying category items"""

    # Signal emitted when an item is clicked
    item_clicked = pyqtSignal(object)
    # Signal emitted when panel width changes
    width_changed = pyqtSignal(int)

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.current_category = None
        self.is_expanded = False
        self.config_manager = config_manager

        # Get panel width from config, default to 500
        if config_manager:
            self.target_width = config_manager.get_setting('panel_width', 500)
        else:
            self.target_width = 500  # Ancho más amplio para el contenedor

        self.collapsed_width = 0
        self.search_engine = SearchEngine()
        self.all_items = []  # Store all items before filtering

        self.init_ui()

    def init_ui(self):
        """Initialize the panel UI"""
        # Set fixed width (collapsed initially)
        self.setFixedWidth(self.collapsed_width)
        self.setMinimumHeight(400)

        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-right: 1px solid #1e1e1e;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with category name
        self.header_label = QLabel("Select a category")
        self.header_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 15px;
                font-size: 12pt;
                font-weight: bold;
                border-bottom: 2px solid #007acc;
            }
        """)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header_label)

        # Search bar
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.on_search_changed)
        main_layout.addWidget(self.search_bar)

        # Scroll area for items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252525;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)

        # Container for items
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)
        self.items_layout.addStretch()

        scroll_area.setWidget(self.items_container)
        main_layout.addWidget(scroll_area)

        # Animation for expand/collapse
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.valueChanged.connect(lambda: self.width_changed.emit(self.width()))

    def load_category(self, category: Category):
        """Load and display items from a category"""
        logger.info(f"Loading category: {category.name} with {len(category.items)} items")

        self.current_category = category
        self.all_items = category.items.copy()

        # Update header
        self.header_label.setText(category.name)
        logger.debug(f"Header updated to: {category.name}")

        # Clear search bar
        self.search_bar.clear_search()

        # Clear existing items
        self.clear_items()
        logger.debug("Previous items cleared")

        # Add new items
        self.display_items(self.all_items)

        # Expand panel if not already expanded
        if not self.is_expanded:
            logger.info("Expanding panel...")
            self.expand()
        else:
            logger.debug("Panel already expanded")

    def display_items(self, items):
        """Display a list of items"""
        logger.info(f"Displaying {len(items)} items")

        # Clear existing items
        self.clear_items()

        # Add items
        for idx, item in enumerate(items):
            logger.debug(f"Creating button {idx+1}/{len(items)}: {item.label}")
            item_button = ItemButton(item)
            item_button.item_clicked.connect(self.on_item_clicked)
            self.items_layout.insertWidget(self.items_layout.count() - 1, item_button)

        logger.info(f"Successfully added {len(items)} item buttons to layout")

    def clear_items(self):
        """Clear all item buttons"""
        while self.items_layout.count() > 1:  # Keep the stretch at the end
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def expand(self):
        """Expand the panel with animation"""
        if self.is_expanded:
            return

        logger.debug(f"Starting expansion animation from {self.width()}px to {self.target_width}px")
        self.is_expanded = True
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.target_width)
        self.animation.start()
        logger.info("Panel expansion started")

    def collapse(self):
        """Collapse the panel with animation"""
        if not self.is_expanded:
            return

        self.is_expanded = False
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()

    def toggle(self):
        """Toggle panel expansion"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def on_item_clicked(self, item: Item):
        """Handle item click"""
        # Emit signal to parent
        self.item_clicked.emit(item)

    def on_search_changed(self, query: str):
        """Handle search query change with filtering"""
        if not self.current_category:
            return

        if not query or not query.strip():
            # Show all items if query is empty
            self.display_items(self.all_items)
        else:
            # Filter items using search engine
            filtered_items = self.search_engine.search_in_category(query, self.current_category)
            self.display_items(filtered_items)
