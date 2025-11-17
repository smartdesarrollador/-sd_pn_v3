"""
Pinned Panel Card Widget
Visual card component for each pinned panel in the management window
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PinnedPanelCard(QWidget):
    """Card widget representing a pinned panel"""

    # Signals
    open_requested = pyqtSignal(int)  # panel_id
    edit_requested = pyqtSignal(int)  # panel_id
    delete_requested = pyqtSignal(int)  # panel_id

    def __init__(self, panel_data: dict, parent=None):
        """
        Initialize panel card

        Args:
            panel_data: Dictionary with panel information from database
                Required keys: id, category_id, category_name, custom_name, custom_color,
                              created_at, last_opened, open_count, is_minimized
        """
        super().__init__(parent)
        self.panel_data = panel_data
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setFixedHeight(100)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Card styling
        self.setStyleSheet("""
            PinnedPanelCard {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
            }
            PinnedPanelCard:hover {
                background-color: #353535;
                border: 1px solid #007acc;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)

        # Color indicator bar
        color = self.panel_data.get('custom_color', '#007acc')
        color_bar = QWidget()
        color_bar.setFixedWidth(6)
        color_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        main_layout.addWidget(color_bar)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        # Panel name (custom or category name)
        display_name = self.panel_data.get('custom_name') or self.panel_data.get('category_name', 'Sin nombre')
        name_label = QLabel(display_name)
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #ffffff;")
        info_layout.addWidget(name_label)

        # Category info (if custom name is set)
        if self.panel_data.get('custom_name'):
            category_label = QLabel(f"Categoria: {self.panel_data.get('category_name', 'N/A')}")
            category_label.setStyleSheet("color: #999999; font-size: 9pt;")
            info_layout.addWidget(category_label)

        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Created date
        created_at = self.panel_data.get('created_at', '')
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_str = created_dt.strftime('%d/%m/%Y')
            except:
                created_str = 'N/A'
        else:
            created_str = 'N/A'

        created_label = QLabel(f"Creado: {created_str}")
        created_label.setStyleSheet("color: #888888; font-size: 8pt;")
        stats_layout.addWidget(created_label)

        # Open count
        open_count = self.panel_data.get('open_count', 0)
        count_label = QLabel(f"Aperturas: {open_count}")
        count_label.setStyleSheet("color: #888888; font-size: 8pt;")
        stats_layout.addWidget(count_label)

        # Status (minimized/active)
        is_minimized = self.panel_data.get('is_minimized', False)
        is_active = self.panel_data.get('is_active', True)

        if is_active and is_minimized:
            status_text = "Minimizado"
            status_color = "#ffa500"
        elif is_active:
            status_text = "Activo"
            status_color = "#00ff00"
        else:
            status_text = "Inactivo"
            status_color = "#666666"

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-size: 8pt; font-weight: bold;")
        stats_layout.addWidget(status_label)

        stats_layout.addStretch()

        info_layout.addLayout(stats_layout)
        info_layout.addStretch()

        main_layout.addLayout(info_layout, stretch=1)

        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Open button
        open_btn = QPushButton("Abrir")
        open_btn.setFixedSize(70, 30)
        open_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.panel_data['id']))
        buttons_layout.addWidget(open_btn)

        # Edit button
        edit_btn = QPushButton("⚙")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        edit_btn.setToolTip("Editar nombre y color")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.panel_data['id']))
        buttons_layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #8b0000;
            }
        """)
        delete_btn.setToolTip("Eliminar panel guardado")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.panel_data['id']))
        buttons_layout.addWidget(delete_btn)

        main_layout.addLayout(buttons_layout)

    def update_data(self, panel_data: dict):
        """Update card with new panel data"""
        self.panel_data = panel_data
        # Recreate UI with new data
        # Clear existing layout
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.init_ui()
        logger.debug(f"Updated card for panel {panel_data['id']}")
