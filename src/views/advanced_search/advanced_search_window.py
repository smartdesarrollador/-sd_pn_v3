"""
Advanced Search Window - Main window for advanced search with multiple views
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QSizePolicy, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.search.advanced_search_engine import AdvancedSearchEngine
from .left_panel import LeftPanel

logger = logging.getLogger(__name__)


class SearchInputPanel(QWidget):
    """Panel de entrada de búsqueda con selector de modo"""

    search_requested = pyqtSignal(str, str)  # query, mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        self.pending_query = ""
        self.pending_mode = "smart"

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 5)
        layout.setSpacing(5)

        # Search input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar items...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #f093fb;
            }
        """)
        self.search_input.textChanged.connect(self._on_text_changed)
        input_row.addWidget(self.search_input)

        # Mode selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(['Smart', 'FTS5', 'Exact'])
        self.mode_selector.setCurrentText('Smart')
        self.mode_selector.setFixedWidth(120)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #f093fb;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #f093fb;
                border: 1px solid #3a3a3a;
            }
        """)
        self.mode_selector.currentTextChanged.connect(self._on_mode_changed)
        input_row.addWidget(self.mode_selector)

        layout.addLayout(input_row)

        # Info label
        self.info_label = QLabel("Modos: Smart (automático), FTS5 (rápido), Exact (preciso)")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.info_label)

    def _on_text_changed(self, text):
        """Handle text change with debouncing"""
        self.pending_query = text
        self.pending_mode = self.mode_selector.currentText().lower()
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms debounce

    def _on_mode_changed(self, mode):
        """Handle mode change"""
        if self.search_input.text().strip():
            self._on_text_changed(self.search_input.text())

    def _perform_search(self):
        """Perform the actual search"""
        query = self.pending_query.strip()
        mode = self.pending_mode
        if query:
            logger.debug(f"Searching: '{query}' with mode '{mode}'")
            self.search_requested.emit(query, mode)

    def clear(self):
        """Clear search input"""
        self.search_input.clear()

    def focus(self):
        """Focus on search input"""
        self.search_input.setFocus()


class ResultsPanel(QWidget):
    """Panel de resultados con selector de vista"""

    view_changed = pyqtSignal(str)  # list, table, tree
    item_clicked = pyqtSignal(object)  # Forward item clicks from views
    url_open_requested = pyqtSignal(str)  # Forward URL open requests from views
    item_edit_requested = pyqtSignal(object)  # Forward item edit requests from views

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_view = "list"
        self.results_data = []  # Store raw results for tag filtering
        self.current_query = ""

        # Import views here to avoid circular imports
        from .results_list_view import ResultsListView
        from .results_table_view import ResultsTableView
        from .results_tree_view import ResultsTreeView

        self.ResultsListView = ResultsListView
        self.ResultsTableView = ResultsTableView
        self.ResultsTreeView = ResultsTreeView

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with view selector
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(10)

        # Results count label
        self.results_label = QLabel("0 resultados")
        self.results_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.results_label)

        header_layout.addStretch()

        # View selector buttons
        self.view_buttons = {}
        for view_type, icon in [('list', '☰'), ('table', '⊞'), ('tree', '🌳')]:
            btn = QPushButton(icon)
            btn.setFixedSize(35, 35)
            btn.setCheckable(True)
            btn.setChecked(view_type == 'list')
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                    border-radius: 4px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border-color: #f093fb;
                }
                QPushButton:checked {
                    background-color: #f093fb;
                    border-color: #f093fb;
                }
            """)
            btn.clicked.connect(lambda checked, v=view_type: self._on_view_changed(v))
            self.view_buttons[view_type] = btn
            header_layout.addWidget(btn)

        layout.addWidget(header)

        # Container for views (will hold one view at a time)
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(0)

        # Create all three views
        self.list_view = self.ResultsListView()
        self.list_view.item_clicked.connect(self._on_item_clicked)
        self.list_view.url_open_requested.connect(self._on_url_open_requested)

        self.table_view = self.ResultsTableView()
        self.table_view.item_clicked.connect(self._on_item_clicked)
        self.table_view.item_edit_requested.connect(self._on_item_edit_requested)

        self.tree_view = self.ResultsTreeView()
        self.tree_view.item_clicked.connect(self._on_item_clicked)

        # Add list view by default
        self.view_layout.addWidget(self.list_view)
        self.table_view.setVisible(False)
        self.tree_view.setVisible(False)

        # Store current active view
        self.active_view = self.list_view

        layout.addWidget(self.view_container)

    def _on_view_changed(self, view_type):
        """Handle view change"""
        logger.info(f"Changing view to: {view_type}")

        # Update button states
        for vtype, btn in self.view_buttons.items():
            btn.setChecked(vtype == view_type)

        # Hide current view
        if self.active_view:
            self.view_layout.removeWidget(self.active_view)
            self.active_view.setVisible(False)

        # Show new view
        if view_type == 'list':
            self.active_view = self.list_view
        elif view_type == 'table':
            self.active_view = self.table_view
        elif view_type == 'tree':
            self.active_view = self.tree_view

        self.view_layout.addWidget(self.active_view)
        self.active_view.setVisible(True)

        # Update view with current results
        if self.results_data:
            self.active_view.update_results(self.results_data)

        self.current_view = view_type
        self.view_changed.emit(view_type)

    def update_results(self, results, count, execution_time):
        """Update results display"""
        self.results_data = results

        # Update count label
        time_str = f"{execution_time:.2f}ms"
        self.results_label.setText(f"{count} resultados ({time_str})")

        # Update active view
        if self.active_view:
            self.active_view.update_results(results)

        logger.info(f"Results updated: {count} items in {time_str}")

    def _on_item_clicked(self, item):
        """Handle item click from any view"""
        logger.debug(f"Item clicked: {item.label}")
        self.item_clicked.emit(item)

    def _on_url_open_requested(self, url: str):
        """Handle URL open request from any view"""
        logger.info(f"URL open requested in results panel: {url}")
        # Forward signal to parent (AdvancedSearchWindow)
        self.url_open_requested.emit(url)

    def _on_item_edit_requested(self, item):
        """Handle item edit request from any view"""
        logger.info(f"Item edit requested in results panel: {item.label}")
        # Forward signal to parent (AdvancedSearchWindow)
        self.item_edit_requested.emit(item)




class AdvancedSearchWindow(QWidget):
    """
    Advanced Search Window with multiple views and filters

    Features:
    - Smart/FTS5/Exact search modes
    - List/Table/Tree views
    - Search history
    - Advanced filters
    - Keyboard shortcuts
    """

    # Signals
    item_clicked = pyqtSignal(object)
    window_closed = pyqtSignal()
    url_open_requested = pyqtSignal(str)  # Signal for opening URL in embedded browser
    item_edit_requested = pyqtSignal(object)  # Signal for editing item

    def __init__(self, db_manager=None, config_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config_manager = config_manager

        # Initialize search engine
        self.search_engine = AdvancedSearchEngine(db_manager) if db_manager else None

        # Window state
        self.is_pinned = False
        self.panel_name = "Búsqueda Avanzada"
        self.is_maximized = False
        self.normal_geometry = None  # Store normal geometry before maximize

        # Store raw results before tag filtering
        self.raw_search_results = []

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        """Initialize the window UI"""
        # Window properties
        self.setWindowTitle("Búsqueda Avanzada")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Window size
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            window_width = int(screen_geo.width() * 0.7)
            window_height = int(screen_geo.height() * 0.8)
        else:
            window_width = 1000
            window_height = 700

        self.resize(window_width, window_height)
        self.setMinimumSize(800, 600)

        # Set opacity
        self.setWindowOpacity(0.95)

        # Don't close app when closing this window
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        # Styling
        self.setStyleSheet("""
            AdvancedSearchWindow {
                background-color: #252525;
                border: 2px solid #f093fb;
                border-left: 5px solid #f093fb;
                border-radius: 8px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Search input panel
        self.search_panel = SearchInputPanel()
        self.search_panel.search_requested.connect(self._on_search_requested)
        main_layout.addWidget(self.search_panel)

        # Splitter for left panel and results
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3a3a3a;
                width: 2px;
            }
        """)

        # Left panel
        self.left_panel = LeftPanel()
        self.left_panel.setMinimumWidth(200)
        self.left_panel.setMaximumWidth(350)
        self.left_panel.search_requested.connect(self._on_history_search_requested)
        self.left_panel.filters_changed.connect(self._on_filters_changed)
        self.left_panel.tags_filter_changed.connect(self._on_tags_filter_changed)
        splitter.addWidget(self.left_panel)

        # Results panel
        self.results_panel = ResultsPanel()
        self.results_panel.view_changed.connect(self._on_view_changed)
        self.results_panel.item_clicked.connect(self._on_item_clicked)
        self.results_panel.url_open_requested.connect(self._on_url_open_requested)
        self.results_panel.item_edit_requested.connect(self._on_item_edit_requested)
        splitter.addWidget(self.results_panel)

        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

        # Focus on search input
        self.search_panel.focus()

    def _create_header(self):
        """Create header with title and controls"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-radius: 6px 6px 0 0;
            }
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 5, 5)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔍⚡ Búsqueda Avanzada")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)

        layout.addStretch()

        # Minimize button
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(minimize_btn)

        # Maximize button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.maximize_btn.clicked.connect(self._on_maximize_clicked)
        layout.addWidget(self.maximize_btn)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return header

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.close)

        # F5 to refresh
        refresh_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        refresh_shortcut.activated.connect(self._on_refresh)

        # Ctrl+F to focus search
        focus_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        focus_shortcut.activated.connect(self.search_panel.focus)

    def _on_search_requested(self, query, mode):
        """Handle search request"""
        if not self.search_engine:
            logger.error("Search engine not initialized")
            return

        logger.info(f"Performing search: '{query}' mode='{mode}'")

        # Get active filters from left panel
        filters = self.left_panel.get_active_filters()

        # Perform search
        result = self.search_engine.search(
            query=query,
            mode=mode,
            filters=filters,
            limit=100
        )

        # Get raw results and store them
        self.raw_search_results = result.get('results', [])

        # Update tags filter panel with all results (before filtering by tags)
        self.left_panel.update_tags_from_results(self.raw_search_results)

        # Apply tags filter
        filtered_results = self._filter_results_by_tags(self.raw_search_results)

        # Update results panel with filtered results
        self.results_panel.update_results(
            results=filtered_results,
            count=len(filtered_results),
            execution_time=result.get('execution_time_ms', 0.0)
        )

        # Add to history (using original count before tag filtering)
        self.left_panel.add_search_to_history(query, mode, result.get('count', 0))

    def _on_history_search_requested(self, query, mode):
        """Handle search request from history"""
        logger.info(f"Search from history: '{query}' mode='{mode}'")

        # Update search input
        self.search_panel.search_input.setText(query)
        self.search_panel.mode_selector.setCurrentText(mode.capitalize())

        # Trigger search
        self._on_search_requested(query, mode)

    def _on_filters_changed(self, filters):
        """Handle filters changed"""
        logger.info(f"Filters changed: {filters}")

        # Re-run current search with new filters
        query = self.search_panel.search_input.text().strip()
        mode = self.search_panel.mode_selector.currentText().lower()

        if query:
            self._on_search_requested(query, mode)

    def _on_tags_filter_changed(self, selected_tags):
        """Handle tags filter changed"""
        logger.info(f"Tags filter changed: {len(selected_tags)} tags selected")

        # Filter current results by selected tags
        if self.raw_search_results:
            filtered_results = self._filter_results_by_tags(self.raw_search_results)

            logger.info(f"Filtering {len(self.raw_search_results)} results -> {len(filtered_results)} after tag filter")

            # Update results panel with filtered results
            self.results_panel.update_results(
                results=filtered_results,
                count=len(filtered_results),
                execution_time=0.0  # No search performed, instant filter
            )

    def _filter_results_by_tags(self, results):
        """
        Filter results by selected tags

        Args:
            results: List of result dicts

        Returns:
            List of filtered results (only items with at least one selected tag)
        """
        selected_tags = self.left_panel.get_selected_tags()

        logger.debug(f"Filtering with {len(selected_tags)} selected tags: {selected_tags[:5]}...")

        # If no tags selected, show no results
        if not selected_tags:
            logger.info("No tags selected, showing no results")
            return []

        # Filter results: keep items that have at least one of the selected tags
        filtered = []
        excluded_count = 0

        for result in results:
            tags_str = result.get('tags', '')
            if not tags_str:
                # Items without tags are excluded when tag filter is active
                excluded_count += 1
                continue

            # Split item tags and check if any match selected tags
            item_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

            # Check if this item has any of the selected tags
            has_selected_tag = any(tag in selected_tags for tag in item_tags)

            if has_selected_tag:
                filtered.append(result)
            else:
                excluded_count += 1
                logger.debug(f"Excluding item '{result.get('label', 'N/A')}' with tags {item_tags}")

        logger.info(f"Tag filter: {len(results)} total -> {len(filtered)} shown, {excluded_count} excluded")
        return filtered

    def _on_view_changed(self, view_type):
        """Handle view type change"""
        logger.info(f"View changed to: {view_type}")

    def _on_item_clicked(self, item):
        """Handle item click from results views"""
        logger.info(f"Item clicked: {item.label}")
        # Emit signal to parent (MainWindow) to handle clipboard copy
        self.item_clicked.emit(item)

    def _on_url_open_requested(self, url: str):
        """Handle URL open request from results views"""
        logger.info(f"URL open requested in advanced search window: {url}")
        # Forward signal to parent (MainWindow) to open embedded browser
        self.url_open_requested.emit(url)

    def _on_item_edit_requested(self, item):
        """Handle item edit request from results views"""
        logger.info(f"Item edit requested in advanced search window: {item.label}")
        # Forward signal to parent (MainWindow) to open ItemEditorDialog
        self.item_edit_requested.emit(item)

    def _on_refresh(self):
        """Handle refresh shortcut"""
        logger.info("Refreshing search results")
        # Re-trigger current search if there's a query
        if self.search_panel.search_input.text().strip():
            self.search_panel._perform_search()

    def _on_maximize_clicked(self):
        """Handle maximize/restore button click"""
        from PyQt6.QtWidgets import QApplication

        if self.is_maximized:
            # Restore to normal size
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.maximize_btn.setText("□")
            self.is_maximized = False
            logger.info("Window restored to normal size")
        else:
            # Save current geometry
            self.normal_geometry = self.geometry()

            # Maximize but leave space for sidebar (80px on right)
            screen = QApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                # Leave 80px margin on right for sidebar
                self.setGeometry(
                    screen_geo.x(),
                    screen_geo.y(),
                    screen_geo.width() - 80,  # Don't cover sidebar
                    screen_geo.height()
                )

            self.maximize_btn.setText("❐")  # Change icon to indicate restore
            self.is_maximized = True
            logger.info("Window maximized (sidebar-aware)")

    def show(self):
        """Show window and position it"""
        super().show()

        # Position window in center of screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            window_geo = self.frameGeometry()
            center_point = screen_geo.center()
            window_geo.moveCenter(center_point)
            self.move(window_geo.topLeft())

        # Focus on search input
        self.search_panel.focus()

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Advanced search window closed")
        self.window_closed.emit()
        event.accept()
