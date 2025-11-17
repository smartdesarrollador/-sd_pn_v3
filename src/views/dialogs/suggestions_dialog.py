"""
Favorite Suggestions Dialog - Sugerencias inteligentes de favoritos
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.stats_manager import StatsManager
from core.favorites_manager import FavoritesManager
import logging

logger = logging.getLogger(__name__)


class FavoriteSuggestionsDialog(QDialog):
    """Diálogo con sugerencias de items para marcar como favoritos"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_manager = StatsManager()
        self.favorites_manager = FavoritesManager()
        self.init_ui()
        self.load_suggestions()

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("💡 Sugerencias de Favoritos")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Items que usas frecuentemente pero no son favoritos:")
        header.setWordWrap(True)
        header_font = QFont()
        header_font.setPointSize(10)
        header.setFont(header_font)
        layout.addWidget(header)

        # Lista de sugerencias
        self.suggestions_list = QListWidget()
        self.suggestions_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.suggestions_list)

        # Info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_font = QFont()
        info_font.setPointSize(8)
        info_font.setItalic(True)
        self.info_label.setFont(info_font)
        layout.addWidget(self.info_label)

        # Botones
        btn_layout = QHBoxLayout()

        self.add_all_btn = QPushButton("⭐ Agregar Todos")
        self.add_all_btn.clicked.connect(self.add_all_suggestions)
        btn_layout.addWidget(self.add_all_btn)

        self.add_selected_btn = QPushButton("⭐ Agregar Seleccionados")
        self.add_selected_btn.clicked.connect(self.add_selected_suggestions)
        btn_layout.addWidget(self.add_selected_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #cccccc;
                padding: 5px;
            }
            QListWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3e3e42;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #3e3e42;
                border-left: 3px solid #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)

    def load_suggestions(self):
        """Cargar sugerencias"""
        try:
            suggestions = self.stats_manager.suggest_favorites(limit=15)

            if not suggestions:
                self.suggestions_list.addItem("No hay sugerencias disponibles")
                self.suggestions_list.setEnabled(False)
                self.add_all_btn.setEnabled(False)
                self.add_selected_btn.setEnabled(False)
                self.info_label.setText("Todos los items populares ya son favoritos")
                return

            for item in suggestions:
                # Crear texto del item
                badge = item.get('badge', '')
                text = f"{badge} " if badge else ""
                text += item['label']
                text += f"\n  {item['use_count']} usos totales"

                recent_uses = item.get('uses_last_30_days', 0)
                if recent_uses > 0:
                    text += f" | {recent_uses} usos últimos 30 días"

                # Crear item de lista
                list_item = QListWidgetItem(text)
                list_item.setData(Qt.ItemDataRole.UserRole, item['id'])
                self.suggestions_list.addItem(list_item)

            self.info_label.setText(f"💡 Tip: Selecciona los items que quieras agregar o agrega todos")

            logger.info(f"Loaded {len(suggestions)} favorite suggestions")

        except Exception as e:
            logger.error(f"Error loading suggestions: {e}")
            self.suggestions_list.addItem("Error al cargar sugerencias")
            self.add_all_btn.setEnabled(False)
            self.add_selected_btn.setEnabled(False)

    def add_all_suggestions(self):
        """Agregar todas las sugerencias como favoritos"""
        try:
            count = 0
            for i in range(self.suggestions_list.count()):
                item = self.suggestions_list.item(i)
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id:
                    self.favorites_manager.mark_as_favorite(item_id)
                    count += 1

            QMessageBox.information(
                self,
                "Éxito",
                f"{count} items agregados a favoritos"
            )
            self.accept()

        except Exception as e:
            logger.error(f"Error adding all suggestions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al agregar favoritos: {str(e)}"
            )

    def add_selected_suggestions(self):
        """Agregar sugerencias seleccionadas como favoritos"""
        try:
            selected = self.suggestions_list.selectedItems()
            if not selected:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "Selecciona al menos un item"
                )
                return

            count = 0
            for item in selected:
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id:
                    self.favorites_manager.mark_as_favorite(item_id)
                    count += 1

            QMessageBox.information(
                self,
                "Éxito",
                f"{count} items agregados a favoritos"
            )
            self.accept()

        except Exception as e:
            logger.error(f"Error adding selected suggestions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al agregar favoritos: {str(e)}"
            )
