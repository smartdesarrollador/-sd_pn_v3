"""
Pinned Panels Management Window
Window to view, manage, and restore pinned panels
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.widgets.pinned_panel_card import PinnedPanelCard
from views.dialogs.panel_config_dialog import PanelConfigDialog
import logging

logger = logging.getLogger(__name__)


class PinnedPanelsWindow(QWidget):
    """Window for managing saved pinned panels"""

    # Signals
    panel_open_requested = pyqtSignal(int)  # panel_id to open/restore
    panel_deleted = pyqtSignal(int)  # panel_id that was deleted
    panel_updated = pyqtSignal(int, str, str)  # panel_id, custom_name, custom_color

    def __init__(self, panels_manager, parent=None):
        """
        Initialize the pinned panels window

        Args:
            panels_manager: PinnedPanelsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.panels_manager = panels_manager
        self.panel_cards = {}  # panel_id -> PinnedPanelCard widget
        self.init_ui()
        self.load_panels()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Gestión de Paneles Anclados")
        self.setMinimumSize(700, 500)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )

        # Dark theme styling
        self.setStyleSheet("""
            PinnedPanelsWindow {
                background-color: #252525;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Paneles Anclados Guardados")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.refresh_panels)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # Info label
        self.info_label = QLabel("Cargando paneles...")
        self.info_label.setStyleSheet("color: #999999; font-size: 9pt;")
        main_layout.addWidget(self.info_label)

        # Scroll area for panel cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
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

        # Container for panel cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area)

        # Empty state label (hidden by default)
        self.empty_label = QLabel("No hay paneles guardados.\nAncla un panel y se guardará automáticamente aquí.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11pt;
                padding: 40px;
            }
        """)
        self.empty_label.setVisible(False)
        main_layout.addWidget(self.empty_label)

    def load_panels(self):
        """Load all panels from database and display them"""
        logger.info("Loading pinned panels...")

        # Get all panels (active and inactive)
        panels = self.panels_manager.get_all_panels(active_only=False)

        # Clear existing cards
        self.clear_cards()

        if not panels:
            # Show empty state
            self.info_label.setText("No hay paneles guardados")
            self.empty_label.setVisible(True)
            logger.info("No panels found")
            return

        # Hide empty state
        self.empty_label.setVisible(False)

        # Create card for each panel
        for panel_data in panels:
            self.add_panel_card(panel_data)

        # Update info label
        active_count = sum(1 for p in panels if p.get('is_active', False))
        self.info_label.setText(f"Total: {len(panels)} paneles ({active_count} activos)")

        logger.info(f"Loaded {len(panels)} panels ({active_count} active)")

    def add_panel_card(self, panel_data: dict):
        """Add a panel card to the list"""
        panel_id = panel_data['id']

        # Create card
        card = PinnedPanelCard(panel_data)

        # Connect signals
        card.open_requested.connect(self.on_open_panel)
        card.edit_requested.connect(self.on_edit_panel)
        card.delete_requested.connect(self.on_delete_panel)

        # Insert before stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        # Store reference
        self.panel_cards[panel_id] = card

        logger.debug(f"Added card for panel {panel_id}")

    def clear_cards(self):
        """Remove all panel cards"""
        # Remove all cards
        for panel_id, card in list(self.panel_cards.items()):
            self.cards_layout.removeWidget(card)
            card.deleteLater()

        self.panel_cards.clear()
        logger.debug("Cleared all panel cards")

    def refresh_panels(self):
        """Refresh panel list from database"""
        logger.info("Refreshing panel list...")
        self.load_panels()

    def on_open_panel(self, panel_id: int):
        """Handle open panel request"""
        logger.info(f"Open panel requested: {panel_id}")
        self.panel_open_requested.emit(panel_id)

    def on_edit_panel(self, panel_id: int):
        """Handle edit panel request - open config dialog"""
        logger.info(f"Edit panel requested: {panel_id}")

        # Get panel data
        panel_data = self.panels_manager.get_panel_by_id(panel_id)
        if not panel_data:
            logger.error(f"Panel {panel_id} not found")
            return

        # Open config dialog
        dialog = PanelConfigDialog(
            current_name=panel_data.get('custom_name', ''),
            current_color=panel_data.get('custom_color', '#007acc'),
            category_name=panel_data.get('category_name', ''),
            parent=self
        )

        # Connect save signal
        dialog.config_saved.connect(lambda name, color: self.on_panel_customized(panel_id, name, color))

        # Show dialog
        dialog.exec()

    def on_panel_customized(self, panel_id: int, custom_name: str, custom_color: str):
        """Handle panel customization from dialog"""
        logger.info(f"Updating panel {panel_id} - Name: '{custom_name}', Color: {custom_color}")

        # Update in database via manager
        self.panels_manager.update_panel_customization(
            panel_id=panel_id,
            custom_name=custom_name if custom_name else None,
            custom_color=custom_color
        )

        # Emit signal for parent to handle (if panel is currently open)
        self.panel_updated.emit(panel_id, custom_name, custom_color)

        # Refresh the card
        panel_data = self.panels_manager.get_panel_by_id(panel_id)
        if panel_data and panel_id in self.panel_cards:
            self.panel_cards[panel_id].update_data(panel_data)

        logger.info(f"Panel {panel_id} updated successfully")

    def on_delete_panel(self, panel_id: int):
        """Handle delete panel request"""
        logger.info(f"Delete panel requested: {panel_id}")

        # Get panel data for confirmation message
        panel_data = self.panels_manager.get_panel_by_id(panel_id)
        if not panel_data:
            logger.error(f"Panel {panel_id} not found")
            return

        display_name = panel_data.get('custom_name') or panel_data.get('category_name', 'Sin nombre')

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Eliminar el panel '{display_name}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete from database
            self.panels_manager.delete_panel(panel_id)

            # Remove card from UI
            if panel_id in self.panel_cards:
                card = self.panel_cards[panel_id]
                self.cards_layout.removeWidget(card)
                card.deleteLater()
                del self.panel_cards[panel_id]

            # Emit signal
            self.panel_deleted.emit(panel_id)

            # Refresh list
            self.refresh_panels()

            logger.info(f"Panel {panel_id} deleted successfully")
