"""
Selection Utilities Widget
Provides quick selection tools (select all, invert, select by criteria)
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class SelectionUtilsWidget(QWidget):
    """Widget with quick selection utilities"""

    # Signals for selection utilities
    select_all_requested = pyqtSignal()
    select_none_requested = pyqtSignal()
    invert_selection_requested = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize selection utilities widget

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            SelectionUtilsWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
            }
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)

        # Label
        label = QLabel("Selección rápida:")
        label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        layout.addWidget(label)

        # Select All button
        self.btn_select_all = QPushButton("☑ Seleccionar Todo")
        self.btn_select_all.setToolTip("Seleccionar todos los elementos (Ctrl+A)")
        self.btn_select_all.clicked.connect(self.on_select_all_clicked)
        layout.addWidget(self.btn_select_all)

        # Select None button
        self.btn_select_none = QPushButton("☐ Deseleccionar Todo")
        self.btn_select_none.setToolTip("Deseleccionar todos los elementos (Ctrl+Shift+A)")
        self.btn_select_none.clicked.connect(self.on_select_none_clicked)
        layout.addWidget(self.btn_select_none)

        # Invert Selection button
        self.btn_invert = QPushButton("🔄 Invertir Selección")
        self.btn_invert.setToolTip("Invertir selección actual (Ctrl+I)")
        self.btn_invert.clicked.connect(self.on_invert_clicked)
        layout.addWidget(self.btn_invert)

        layout.addStretch()

        # Apply button styles
        button_style = """
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                padding: 5px 12px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border: 1px solid #5d5d5d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """

        for btn in [self.btn_select_all, self.btn_select_none, self.btn_invert]:
            btn.setStyleSheet(button_style)

        logger.info("SelectionUtilsWidget initialized")

    def on_select_all_clicked(self):
        """Handle select all button click"""
        logger.info("Select all requested")
        self.select_all_requested.emit()

    def on_select_none_clicked(self):
        """Handle select none button click"""
        logger.info("Select none requested")
        self.select_none_requested.emit()

    def on_invert_clicked(self):
        """Handle invert selection button click"""
        logger.info("Invert selection requested")
        self.invert_selection_requested.emit()
