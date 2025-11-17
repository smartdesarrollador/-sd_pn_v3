"""
Forgotten Items Dialog - Diálogo para items olvidados/nunca usados
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem,
                              QWidget, QTabWidget, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.stats_manager import StatsManager
import logging

logger = logging.getLogger(__name__)


class ForgottenItemsDialog(QDialog):
    """Diálogo mostrando items olvidados/nunca usados"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_manager = StatsManager()
        self.init_ui()
        self.load_forgotten_items()

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("📦 Items Olvidados")
        self.setMinimumSize(750, 550)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Items que no has usado recientemente")
        header_font = QFont()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()

        # Tab: Nunca usados
        self.never_used_list = QListWidget()
        self.never_used_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabs.addTab(self.never_used_list, "🆕 Nunca Usados")

        # Tab: Abandonados
        self.abandoned_list = QListWidget()
        self.abandoned_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabs.addTab(self.abandoned_list, "📦 Abandonados (>60 días)")

        # Tab: Poco usados
        self.least_used_list = QListWidget()
        self.least_used_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabs.addTab(self.least_used_list, "📉 Poco Usados")

        layout.addWidget(self.tabs)

        # Información
        info_label = QLabel(
            "💡 Tip: Considera eliminar items que nunca usas para mantener tu widget organizado. "
            "Selecciona los items que deseas eliminar."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #858585; font-style: italic; font-size: 9pt; padding: 10px;")
        layout.addWidget(info_label)

        # Botones
        btn_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("✓ Seleccionar Todos")
        self.select_all_btn.clicked.connect(self.select_all_current_tab)
        btn_layout.addWidget(self.select_all_btn)

        self.clear_selection_btn = QPushButton("✗ Limpiar Selección")
        self.clear_selection_btn.clicked.connect(self.clear_selection_current_tab)
        btn_layout.addWidget(self.clear_selection_btn)

        btn_layout.addStretch()

        self.delete_selected_btn = QPushButton("🗑️ Eliminar Seleccionados")
        self.delete_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        self.delete_selected_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_selected_btn)

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
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 15px;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #252526;
                color: #007acc;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                color: #cccccc;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #3e3e42;
                border-left: 3px solid #c42b1c;
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

    def load_forgotten_items(self):
        """Cargar items olvidados"""
        try:
            # Nunca usados
            never_used = self.stats_manager.get_never_used_items()
            self.populate_list(self.never_used_list, never_used, show_created_date=True)

            # Abandonados
            abandoned = self.stats_manager.get_abandoned_items(days_threshold=60, min_use_count=3)
            self.populate_list(self.abandoned_list, abandoned, show_last_used=True)

            # Poco usados
            least_used = self.stats_manager.get_least_used_items(limit=30)
            self.populate_list(self.least_used_list, least_used, show_use_count=True)

            logger.info("Forgotten items loaded successfully")

        except Exception as e:
            logger.error(f"Error loading forgotten items: {e}")

    def populate_list(self, list_widget: QListWidget, items: list, **kwargs):
        """Poblar lista con items"""
        list_widget.clear()

        if not items:
            empty_item = QListWidgetItem("✅ No hay items en esta categoría")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            list_widget.addItem(empty_item)
            return

        for item in items:
            # Crear texto del item
            badge = item.get('badge', '')
            text = f"{badge} " if badge else ""
            text += item['label']
            text += "\n  "

            # Agregar info según parámetros
            info_parts = []

            if kwargs.get('show_created_date'):
                created = item.get('created_at', '')
                if created:
                    days_ago = self.calculate_days_ago(created)
                    info_parts.append(f"Creado hace {days_ago} días")

            if kwargs.get('show_last_used'):
                last_used = item.get('last_used', '')
                if last_used:
                    days_ago = self.calculate_days_ago(last_used)
                    info_parts.append(f"Último uso hace {days_ago} días")
                use_count = item.get('use_count', 0)
                if use_count:
                    info_parts.append(f"{use_count} usos totales")

            if kwargs.get('show_use_count'):
                use_count = item.get('use_count', 0)
                info_parts.append(f"{use_count} usos")
                last_used = item.get('last_used', '')
                if last_used:
                    days_ago = self.calculate_days_ago(last_used)
                    info_parts.append(f"hace {days_ago} días")

            text += " | ".join(info_parts)

            # Crear item de lista
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            list_widget.addItem(list_item)

    def calculate_days_ago(self, timestamp: str) -> int:
        """Calcular días desde timestamp"""
        try:
            # Parse SQLite datetime format
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            delta = now - dt
            return delta.days
        except Exception as e:
            logger.debug(f"Error parsing timestamp {timestamp}: {e}")
            return 0

    def select_all_current_tab(self):
        """Seleccionar todos los items de la tab actual"""
        current_list = self.tabs.currentWidget()
        if isinstance(current_list, QListWidget):
            current_list.selectAll()

    def clear_selection_current_tab(self):
        """Limpiar selección de la tab actual"""
        current_list = self.tabs.currentWidget()
        if isinstance(current_list, QListWidget):
            current_list.clearSelection()

    def delete_selected(self):
        """Eliminar items seleccionados"""
        # Obtener items seleccionados de todas las tabs
        selected_ids = []

        for list_widget in [self.never_used_list, self.abandoned_list, self.least_used_list]:
            for item in list_widget.selectedItems():
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id:
                    selected_ids.append(item_id)

        if not selected_ids:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Selecciona al menos un item para eliminar"
            )
            return

        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar {len(selected_ids)} items?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Eliminar items de la base de datos
            try:
                import sqlite3
                conn = sqlite3.connect("widget_sidebar.db")
                cursor = conn.cursor()

                for item_id in selected_ids:
                    # Eliminar de item_usage_history primero (foreign key)
                    cursor.execute("DELETE FROM item_usage_history WHERE item_id = ?", (item_id,))
                    # Eliminar item
                    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

                conn.commit()
                conn.close()

                logger.info(f"Deleted {len(selected_ids)} items")

                QMessageBox.information(
                    self,
                    "Éxito",
                    f"{len(selected_ids)} items eliminados correctamente"
                )

                # Recargar listas
                self.load_forgotten_items()

            except Exception as e:
                logger.error(f"Error deleting items: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar items:\n{str(e)}"
                )
