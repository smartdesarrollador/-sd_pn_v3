"""
Search Bar Widget for Dashboard
Provides incremental search with debouncing and scope filters
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QCheckBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class SearchBarWidget(QWidget):
    """Search bar with incremental search and scope filters"""

    # Signal emitted when search query changes (after debouncing)
    search_changed = pyqtSignal(str, dict)  # query, scope_filters

    # Signal emitted when navigating between results
    navigate_to_result = pyqtSignal(int)  # result_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

        self.current_result_index = 0
        self.total_results = 0

        self.init_ui()

    def init_ui(self):
        """Initialize search bar UI"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom: 1px solid #3d3d3d;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(8)

        # Search input row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        # Search icon label
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14pt; background-color: transparent;")
        search_row.addWidget(search_icon)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en categorías, items, tags, contenido...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        self.search_input.textChanged.connect(self._on_text_changed)
        search_row.addWidget(self.search_input)

        # Navigation buttons container
        nav_container = QWidget()
        nav_container.setStyleSheet("background-color: transparent;")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        # Previous button
        self.prev_button = QLabel("⬆")
        self.prev_button.setToolTip("Resultado anterior (Shift+F3)")
        self.prev_button.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #888888;
                font-size: 12pt;
                padding: 5px;
            }
            QLabel:hover {
                color: #ffffff;
                background-color: #3d3d3d;
                border-radius: 3px;
            }
        """)
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.mousePressEvent = lambda e: self.navigate_previous()
        self.prev_button.setVisible(False)
        nav_layout.addWidget(self.prev_button)

        # Next button
        self.next_button = QLabel("⬇")
        self.next_button.setToolTip("Siguiente resultado (F3)")
        self.next_button.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #888888;
                font-size: 12pt;
                padding: 5px;
            }
            QLabel:hover {
                color: #ffffff;
                background-color: #3d3d3d;
                border-radius: 3px;
            }
        """)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.mousePressEvent = lambda e: self.navigate_next()
        self.next_button.setVisible(False)
        nav_layout.addWidget(self.next_button)

        search_row.addWidget(nav_container)

        # Clear button
        self.clear_button = QLabel("✖")
        self.clear_button.setToolTip("Limpiar búsqueda (Esc)")
        self.clear_button.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #888888;
                font-size: 12pt;
                padding: 5px;
            }
            QLabel:hover {
                color: #ffffff;
            }
        """)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.mousePressEvent = lambda e: self.clear_search()
        self.clear_button.setVisible(False)
        search_row.addWidget(self.clear_button)

        main_layout.addLayout(search_row)

        # Scope filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(20)
        filters_row.setContentsMargins(30, 0, 0, 0)

        filters_label = QLabel("Buscar en:")
        filters_label.setStyleSheet("color: #888888; font-size: 9pt; background-color: transparent;")
        filters_row.addWidget(filters_label)

        # Create checkboxes for each scope
        self.scope_checkboxes = {}

        scopes = [
            ('categories', 'Categorías'),
            ('items', 'Items'),
            ('lists', 'Listas'),
            ('tags', 'Tags'),
            ('content', 'Contenido')
        ]

        for scope_id, scope_label in scopes:
            checkbox = QCheckBox(scope_label)
            checkbox.setChecked(True)  # All checked by default
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #cccccc;
                    font-size: 9pt;
                    background-color: transparent;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #3d3d3d;
                    border-radius: 3px;
                    background-color: #1e1e1e;
                }
                QCheckBox::indicator:checked {
                    background-color: #007acc;
                    border-color: #007acc;
                }
                QCheckBox::indicator:hover {
                    border-color: #007acc;
                }
            """)
            checkbox.stateChanged.connect(self._on_filter_changed)
            self.scope_checkboxes[scope_id] = checkbox
            filters_row.addWidget(checkbox)

        filters_row.addStretch()

        # Results counter
        self.results_label = QLabel("")
        self.results_label.setStyleSheet("color: #888888; font-size: 9pt; background-color: transparent;")
        self.results_label.setVisible(False)
        filters_row.addWidget(self.results_label)

        main_layout.addLayout(filters_row)

        logger.debug("SearchBarWidget initialized")

    def _on_text_changed(self, text: str):
        """Handle text change with debouncing"""
        # Show/hide clear button
        self.clear_button.setVisible(bool(text))

        # Reset timer on each keystroke
        self.search_timer.stop()

        if text.strip():
            # Start 300ms timer
            self.search_timer.start(300)
            logger.debug(f"Search timer started for query: '{text}'")
        else:
            # Clear search immediately if empty
            self._perform_search()

    def _on_filter_changed(self):
        """Handle filter checkbox change"""
        if self.search_input.text().strip():
            # Re-trigger search with new filters
            self._perform_search()

    def _perform_search(self):
        """Perform the actual search and emit signal"""
        query = self.search_input.text().strip()

        # Get active scope filters
        scope_filters = {
            scope: checkbox.isChecked()
            for scope, checkbox in self.scope_checkboxes.items()
        }

        logger.info(f"Performing search - Query: '{query}', Filters: {scope_filters}")

        # Emit signal
        self.search_changed.emit(query, scope_filters)

    def clear_search(self):
        """Clear search input"""
        logger.debug("Clearing search")
        self.search_input.clear()
        self.results_label.setVisible(False)

    def set_results_count(self, count: int):
        """Update results counter"""
        self.total_results = count

        if count > 0:
            self.current_result_index = 1  # Start at first result
            self.results_label.setText(f"{self.current_result_index}/{count} resultados")
            self.results_label.setVisible(True)
            self.prev_button.setVisible(True)
            self.next_button.setVisible(True)
        else:
            query = self.search_input.text().strip()
            if query:
                self.results_label.setText("No se encontraron resultados")
                self.results_label.setVisible(True)
            else:
                self.results_label.setVisible(False)

            self.prev_button.setVisible(False)
            self.next_button.setVisible(False)
            self.current_result_index = 0

    def navigate_previous(self):
        """Navigate to previous search result"""
        if self.total_results == 0:
            return

        self.current_result_index -= 1
        if self.current_result_index < 1:
            self.current_result_index = self.total_results

        self.results_label.setText(f"{self.current_result_index}/{self.total_results} resultados")
        self.navigate_to_result.emit(self.current_result_index - 1)  # 0-based index
        logger.debug(f"Navigated to previous result: {self.current_result_index}/{self.total_results}")

    def navigate_next(self):
        """Navigate to next search result"""
        if self.total_results == 0:
            return

        self.current_result_index += 1
        if self.current_result_index > self.total_results:
            self.current_result_index = 1

        self.results_label.setText(f"{self.current_result_index}/{self.total_results} resultados")
        self.navigate_to_result.emit(self.current_result_index - 1)  # 0-based index
        logger.debug(f"Navigated to next result: {self.current_result_index}/{self.total_results}")

    def get_query(self) -> str:
        """Get current search query"""
        return self.search_input.text().strip()

    def get_scope_filters(self) -> dict:
        """Get current scope filters"""
        return {
            scope: checkbox.isChecked()
            for scope, checkbox in self.scope_checkboxes.items()
        }

    def focus_search(self):
        """Focus the search input and select all text"""
        self.search_input.setFocus()
        self.search_input.selectAll()
        logger.debug("Search input focused")
