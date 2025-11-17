"""
Action Bar Widget for Bulk Operations
Provides buttons and controls for bulk actions on selected items
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class ActionBarWidget(QWidget):
    """Action bar widget for bulk operations on selected items"""

    # Signals for bulk actions
    favorite_requested = pyqtSignal()      # Marcar como favoritos
    unfavorite_requested = pyqtSignal()    # Quitar favoritos
    activate_requested = pyqtSignal()      # Activar elementos
    deactivate_requested = pyqtSignal()    # Desactivar elementos
    archive_requested = pyqtSignal()       # Archivar elementos
    unarchive_requested = pyqtSignal()     # Desarchivar elementos
    delete_requested = pyqtSignal()        # Eliminar elementos
    clear_selection_requested = pyqtSignal()  # Limpiar selección

    def __init__(self, parent=None):
        """
        Initialize action bar widget

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        self.setVisible(False)  # Hidden by default
        self.setFixedHeight(60)
        self.setStyleSheet("""
            ActionBarWidget {
                background-color: #007acc;
                border-top: 2px solid #005a9e;
                border-bottom: 2px solid #005a9e;
            }
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        # Selection counter label
        self.selection_label = QLabel("0 elementos seleccionados")
        self.selection_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.selection_label)

        layout.addStretch()

        # Clear selection button
        self.btn_clear = QPushButton("✕ Limpiar")
        self.btn_clear.setToolTip("Limpiar selección actual")
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        layout.addWidget(self.btn_clear)

        # Spacer
        layout.addSpacing(20)

        # Action buttons
        self.btn_favorite = QPushButton("⭐ Marcar Favoritos")
        self.btn_favorite.setToolTip("Marcar items seleccionados como favoritos")
        self.btn_favorite.clicked.connect(self.on_favorite_clicked)
        layout.addWidget(self.btn_favorite)

        self.btn_unfavorite = QPushButton("☆ Quitar Favoritos")
        self.btn_unfavorite.setToolTip("Quitar items seleccionados de favoritos")
        self.btn_unfavorite.clicked.connect(self.on_unfavorite_clicked)
        layout.addWidget(self.btn_unfavorite)

        self.btn_activate = QPushButton("✓ Activar")
        self.btn_activate.setToolTip("Activar elementos seleccionados")
        self.btn_activate.clicked.connect(self.on_activate_clicked)
        layout.addWidget(self.btn_activate)

        self.btn_deactivate = QPushButton("🚫 Desactivar")
        self.btn_deactivate.setToolTip("Desactivar elementos seleccionados")
        self.btn_deactivate.clicked.connect(self.on_deactivate_clicked)
        layout.addWidget(self.btn_deactivate)

        self.btn_archive = QPushButton("📦 Archivar")
        self.btn_archive.setToolTip("Archivar elementos seleccionados")
        self.btn_archive.clicked.connect(self.on_archive_clicked)
        layout.addWidget(self.btn_archive)

        self.btn_unarchive = QPushButton("📂 Desarchivar")
        self.btn_unarchive.setToolTip("Desarchivar elementos seleccionados")
        self.btn_unarchive.clicked.connect(self.on_unarchive_clicked)
        layout.addWidget(self.btn_unarchive)

        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setToolTip("Eliminar elementos seleccionados")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

        # Apply button styles
        button_style = """
            QPushButton {
                background-color: white;
                color: #007acc;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """

        for btn in [self.btn_clear, self.btn_favorite, self.btn_unfavorite,
                    self.btn_activate, self.btn_deactivate, self.btn_archive,
                    self.btn_unarchive, self.btn_delete]:
            btn.setStyleSheet(button_style)

        # Delete button has warning style
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #a31010;
            }
            QPushButton:disabled {
                background-color: #e57373;
                color: #ffcdd2;
            }
        """)

        logger.info("ActionBarWidget initialized")

    def update_selection(self, total_count: int, items_count: int, categories_count: int):
        """
        Update action bar based on current selection

        Args:
            total_count: Total number of elements selected
            items_count: Number of items selected
            categories_count: Number of categories selected
        """
        if total_count > 0:
            self.setVisible(True)

            # Update label
            parts = []
            if items_count > 0:
                parts.append(f"{items_count} item{'s' if items_count != 1 else ''}")
            if categories_count > 0:
                parts.append(f"{categories_count} categoría{'s' if categories_count != 1 else ''}")

            label_text = " + ".join(parts) + " seleccionado" + ("s" if total_count != 1 else "")
            self.selection_label.setText(label_text)

            # Enable/disable buttons based on selection type
            # Favorite/Unfavorite only work on items, not categories
            self.btn_favorite.setEnabled(items_count > 0)
            self.btn_unfavorite.setEnabled(items_count > 0)

            # Activate/Deactivate/Archive/Unarchive/Delete work on both items and categories
            self.btn_activate.setEnabled(total_count > 0)
            self.btn_deactivate.setEnabled(total_count > 0)
            self.btn_archive.setEnabled(total_count > 0)
            self.btn_unarchive.setEnabled(total_count > 0)
            self.btn_delete.setEnabled(total_count > 0)

            logger.debug(f"ActionBar updated: {total_count} elements ({items_count} items, {categories_count} categories)")
        else:
            self.setVisible(False)
            logger.debug("ActionBar hidden (no selection)")

    def on_clear_clicked(self):
        """Handle clear selection button click"""
        logger.info("Clear selection requested")
        self.clear_selection_requested.emit()

    def on_favorite_clicked(self):
        """Handle favorite button click"""
        logger.info("Favorite action requested")
        self.favorite_requested.emit()

    def on_unfavorite_clicked(self):
        """Handle unfavorite button click"""
        logger.info("Unfavorite action requested")
        self.unfavorite_requested.emit()

    def on_activate_clicked(self):
        """Handle activate button click"""
        logger.info("Activate action requested")
        self.activate_requested.emit()

    def on_archive_clicked(self):
        """Handle archive button click"""
        logger.info("Archive action requested")
        self.archive_requested.emit()

    def on_deactivate_clicked(self):
        """Handle deactivate button click"""
        logger.info("Deactivate action requested")
        self.deactivate_requested.emit()

    def on_unarchive_clicked(self):
        """Handle unarchive button click"""
        logger.info("Unarchive action requested")
        self.unarchive_requested.emit()

    def on_delete_clicked(self):
        """Handle delete button click"""
        logger.info("Delete action requested")
        self.delete_requested.emit()
