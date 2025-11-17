"""
Favorites Panel - Panel lateral de items favoritos
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.favorites_manager import FavoritesManager
from core.usage_tracker import UsageTracker
import logging

logger = logging.getLogger(__name__)


class FavoritesPanel(QWidget):
    """Panel de items favoritos con drag & drop"""

    # Señales
    favorite_clicked = pyqtSignal(int)  # item_id
    favorite_double_clicked = pyqtSignal(int)  # item_id para ejecutar
    favorite_removed = pyqtSignal(int)  # item_id
    favorites_reordered = pyqtSignal()  # Cuando se reordena

    def __init__(self, parent=None):
        super().__init__(parent)
        self.favorites_manager = FavoritesManager()
        self.usage_tracker = UsageTracker()
        self.init_ui()
        self.load_favorites()

    def init_ui(self):
        """Inicializar UI"""
        self.setObjectName("favorites_panel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Título con contador
        self.title_label = QLabel("⭐ FAVORITOS (0)")
        self.title_label.setObjectName("title_label")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Botón de opciones
        self.options_btn = QPushButton("⚙")
        self.options_btn.setObjectName("options_btn")
        self.options_btn.setFixedSize(30, 30)
        self.options_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.options_btn.setToolTip("Opciones")
        self.options_btn.clicked.connect(self.show_options_menu)
        header_layout.addWidget(self.options_btn)

        layout.addWidget(header_widget)

        # Lista de favoritos
        self.favorites_list = QListWidget()
        self.favorites_list.setObjectName("favorites_list")
        self.favorites_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.favorites_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.favorites_list.setSpacing(2)
        self.favorites_list.itemClicked.connect(self.on_item_clicked)
        self.favorites_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.favorites_list.model().rowsMoved.connect(self.on_items_reordered)
        self.favorites_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.favorites_list)

        # Footer con info
        self.footer_label = QLabel("Arrastra para reordenar")
        self.footer_label.setObjectName("footer_label")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_font = QFont()
        footer_font.setPointSize(8)
        footer_font.setItalic(True)
        self.footer_label.setFont(footer_font)
        layout.addWidget(self.footer_label)

        # Aplicar estilos
        self.apply_styles()

    def apply_styles(self):
        """Aplicar estilos CSS"""
        self.setStyleSheet("""
            QWidget#favorites_panel {
                background-color: #1e1e1e;
                border-right: 2px solid #2d2d2d;
            }

            QWidget#header_widget {
                background-color: #252526;
                border-bottom: 1px solid #2d2d2d;
            }

            QLabel#title_label {
                color: #cccccc;
            }

            QPushButton#options_btn {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 14pt;
            }

            QPushButton#options_btn:hover {
                background-color: #3e3e42;
                border-radius: 3px;
            }

            QListWidget#favorites_list {
                background-color: #1e1e1e;
                border: none;
                outline: none;
            }

            QListWidget#favorites_list::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d2d;
                color: #cccccc;
            }

            QListWidget#favorites_list::item:hover {
                background-color: #2d2d2d;
            }

            QListWidget#favorites_list::item:selected {
                background-color: #3e3e42;
                border-left: 3px solid #007acc;
            }

            QLabel#footer_label {
                color: #858585;
                padding: 5px;
                background-color: #252526;
                border-top: 1px solid #2d2d2d;
            }
        """)

    def load_favorites(self):
        """Cargar y mostrar favoritos"""
        try:
            # Limpiar lista actual
            self.favorites_list.clear()

            # Obtener favoritos
            favorites = self.favorites_manager.get_all_favorites()

            # Actualizar contador en título
            self.title_label.setText(f"⭐ FAVORITOS ({len(favorites)})")

            # Agregar cada favorito a la lista
            for fav in favorites:
                self.add_favorite_item(fav)

            logger.info(f"Loaded {len(favorites)} favorites")

        except Exception as e:
            logger.error(f"Error loading favorites: {e}")

    def add_favorite_item(self, item: dict):
        """Agregar item favorito a la lista"""
        try:
            # Obtener stats del item
            use_count = item.get('use_count', 0)
            shortcut = item.get('shortcut', '')
            badge = item.get('badge', '')

            # Construir texto del item
            text = f"{badge} " if badge else ""
            text += item['label']

            # Info adicional
            info_parts = []
            if use_count > 0:
                info_parts.append(f"{use_count} usos")
            if shortcut:
                info_parts.append(shortcut)

            if info_parts:
                text += f"\n  {' | '.join(info_parts)}"

            # Crear item de lista
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            list_item.setSizeHint(QSize(0, 50))

            # Color según uso
            if use_count > 50:
                # Popular
                list_item.setToolTip(f"🔥 Popular - {item['label']}")
            elif use_count == 0:
                # Nunca usado
                list_item.setToolTip(f"🆕 Nuevo - {item['label']}")
            else:
                list_item.setToolTip(item['label'])

            self.favorites_list.addItem(list_item)

        except Exception as e:
            logger.error(f"Error adding favorite item: {e}")

    def on_item_clicked(self, item: QListWidgetItem):
        """Handler cuando se hace click en favorito"""
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_id:
            self.favorite_clicked.emit(item_id)

    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handler cuando se hace doble click (ejecutar)"""
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_id:
            self.favorite_double_clicked.emit(item_id)

    def on_items_reordered(self):
        """Handler cuando se reordenan items (drag & drop)"""
        try:
            # Obtener nuevo orden de IDs
            item_ids = []
            for i in range(self.favorites_list.count()):
                item = self.favorites_list.item(i)
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id:
                    item_ids.append(item_id)

            # Actualizar orden en BD
            if item_ids:
                self.favorites_manager.reorder_favorites(item_ids)
                logger.info(f"Favorites reordered: {item_ids}")
                self.favorites_reordered.emit()

        except Exception as e:
            logger.error(f"Error reordering favorites: {e}")

    def show_context_menu(self, position):
        """Mostrar menú contextual"""
        item = self.favorites_list.itemAt(position)
        if not item:
            return

        item_id = item.data(Qt.ItemDataRole.UserRole)
        if not item_id:
            return

        menu = QMenu(self)

        # Ejecutar
        execute_action = menu.addAction("▶ Ejecutar")
        execute_action.triggered.connect(lambda: self.favorite_double_clicked.emit(item_id))

        menu.addSeparator()

        # Quitar de favoritos
        remove_action = menu.addAction("⭐ Quitar de Favoritos")
        remove_action.triggered.connect(lambda: self.remove_favorite(item_id))

        # Mostrar menú
        menu.exec(self.favorites_list.mapToGlobal(position))

    def show_options_menu(self):
        """Mostrar menú de opciones"""
        menu = QMenu(self)

        # Auto-ordenar
        sort_menu = menu.addMenu("🔢 Auto-ordenar")

        sort_by_use = sort_menu.addAction("Por Uso (más usado primero)")
        sort_by_use.triggered.connect(lambda: self.auto_sort_favorites("use_count"))

        sort_by_name = sort_menu.addAction("Por Nombre (A-Z)")
        sort_by_name.triggered.connect(lambda: self.auto_sort_favorites("label"))

        sort_by_recent = sort_menu.addAction("Por Uso Reciente")
        sort_by_recent.triggered.connect(lambda: self.auto_sort_favorites("last_used"))

        menu.addSeparator()

        # Limpiar todos
        clear_action = menu.addAction("🗑 Limpiar Todos los Favoritos")
        clear_action.triggered.connect(self.clear_all_favorites)

        # Mostrar menú
        menu.exec(QCursor.pos())

    def auto_sort_favorites(self, by: str):
        """Auto-ordenar favoritos"""
        try:
            success = self.favorites_manager.auto_order_favorites(by=by)
            if success:
                self.load_favorites()
                logger.info(f"Favorites auto-sorted by {by}")
        except Exception as e:
            logger.error(f"Error auto-sorting favorites: {e}")

    def remove_favorite(self, item_id: int):
        """Quitar item de favoritos"""
        try:
            success = self.favorites_manager.unmark_favorite(item_id)
            if success:
                self.load_favorites()
                self.favorite_removed.emit(item_id)
                logger.info(f"Item {item_id} removed from favorites")
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")

    def clear_all_favorites(self):
        """Limpiar todos los favoritos"""
        try:
            from PyQt6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "Limpiar Favoritos",
                "¿Estás seguro de quitar TODOS los favoritos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                count = self.favorites_manager.clear_all_favorites()
                self.load_favorites()
                logger.info(f"Cleared {count} favorites")

        except Exception as e:
            logger.error(f"Error clearing favorites: {e}")

    def refresh(self):
        """Refrescar lista de favoritos"""
        self.load_favorites()

    def add_to_favorites(self, item_id: int):
        """Agregar item a favoritos y refrescar"""
        try:
            success = self.favorites_manager.mark_as_favorite(item_id)
            if success:
                self.load_favorites()
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding to favorites: {e}")
            return False
