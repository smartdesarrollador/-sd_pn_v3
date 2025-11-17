"""
Smart Collections Dialog - Gestión de colecciones inteligentes (filtros guardados)
Permite ver, crear, editar y eliminar Smart Collections
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.smart_collections_manager import SmartCollectionsManager

logger = logging.getLogger(__name__)


class SmartCollectionCard(QFrame):
    """Card widget para mostrar una Smart Collection"""

    view_clicked = pyqtSignal(int)  # collection_id
    edit_clicked = pyqtSignal(int)  # collection_id
    delete_clicked = pyqtSignal(int)  # collection_id

    def __init__(self, collection: dict, parent=None):
        super().__init__(parent)
        self.collection = collection
        self.init_ui()

    def init_ui(self):
        """Inicializar UI del card"""
        self.setObjectName("smartCollectionCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            #smartCollectionCard {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }
            #smartCollectionCard:hover {
                background-color: #3e3e42;
                border-color: #007acc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header: icono + nombre + botones
        header_layout = QHBoxLayout()

        # Icono y nombre
        icon_label = QLabel(self.collection.get('icon', '🔍'))
        icon_label.setStyleSheet("font-size: 24pt; padding: 0; margin: 0;")
        header_layout.addWidget(icon_label)

        name_label = QLabel(self.collection['name'])
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {self.collection.get('color', '#00d4ff')}; padding-left: 8px;")
        header_layout.addWidget(name_label, 1)

        # Botones de acción
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(32, 32)
        view_btn.setToolTip("Ver items de la colección")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_clicked.emit(self.collection['id']))
        header_layout.addWidget(view_btn)

        edit_btn = QPushButton("📝")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Editar colección")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.collection['id']))
        header_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Eliminar colección")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #a22810;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.collection['id']))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Filtros activos
        filters = self._get_active_filters()
        if filters:
            filters_label = QLabel(f"Filtros: {filters}")
            filters_label.setStyleSheet("""
                color: #a0a0a0;
                font-size: 9pt;
                padding: 4px 0;
            """)
            filters_label.setWordWrap(True)
            layout.addWidget(filters_label)

        # Descripción
        if self.collection.get('description'):
            desc_label = QLabel(self.collection['description'])
            desc_label.setStyleSheet("color: #808080; font-size: 9pt; padding: 4px 0;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Contador de items
        if 'item_count' in self.collection:
            count_label = QLabel(f"📊 {self.collection['item_count']} items coinciden")
            count_font = QFont()
            count_font.setPointSize(9)
            count_font.setBold(True)
            count_label.setFont(count_font)
            count_label.setStyleSheet("color: #00d4ff; font-style: italic;")
            layout.addWidget(count_label)

    def _get_active_filters(self) -> str:
        """Obtener descripción legible de los filtros activos"""
        filters = []

        # Tags include
        if self.collection.get('tags_include'):
            tags = self.collection['tags_include']
            filters.append(f"Tags: {tags}")

        # Tags exclude
        if self.collection.get('tags_exclude'):
            tags = self.collection['tags_exclude']
            filters.append(f"Excluye: {tags}")

        # Tipo de item
        if self.collection.get('item_type'):
            filters.append(f"Tipo: {self.collection['item_type']}")

        # Categoría
        if self.collection.get('category_id'):
            filters.append(f"Categoría ID: {self.collection['category_id']}")

        # Favoritos
        if self.collection.get('is_favorite') is not None:
            if self.collection['is_favorite']:
                filters.append("Solo favoritos")

        # Sensibles
        if self.collection.get('is_sensitive') is not None:
            if self.collection['is_sensitive']:
                filters.append("Solo sensibles")

        # Búsqueda de texto
        if self.collection.get('search_text'):
            text = self.collection['search_text']
            filters.append(f"Busca: '{text}'")

        # Fechas
        if self.collection.get('date_from'):
            filters.append(f"Desde: {self.collection['date_from']}")
        if self.collection.get('date_to'):
            filters.append(f"Hasta: {self.collection['date_to']}")

        return ", ".join(filters) if filters else "Sin filtros específicos"


class SmartCollectionsDialog(QDialog):
    """Diálogo principal para gestionar Smart Collections"""

    # Señal emitida cuando se quiere ver los items de una colección
    view_collection = pyqtSignal(int)  # collection_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = self.get_db_path()
        self.manager = SmartCollectionsManager(self.db_path)
        self.init_ui()
        self.load_collections()

    def get_db_path(self) -> str:
        """Obtener ruta de la base de datos"""
        # Intentar obtener desde el parent si es posible
        if hasattr(self.parent(), 'controller'):
            if hasattr(self.parent().controller, 'config_manager'):
                return self.parent().controller.config_manager.db.db_path

        # Fallback: buscar en el directorio raíz del proyecto
        root_dir = Path(__file__).parent.parent.parent.parent
        return str(root_dir / "widget_sidebar.db")

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("🔍 Gestión de Colecciones Inteligentes")
        self.setMinimumSize(750, 600)
        self.setMaximumSize(950, 800)

        # Aplicar estilos generales
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 8px;
                color: #cccccc;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🔍 Colecciones Inteligentes")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón nueva colección
        new_btn = QPushButton("➕ Nueva Colección")
        new_btn.setFixedHeight(35)
        new_btn.clicked.connect(self.create_new_collection)
        header_layout.addWidget(new_btn)

        main_layout.addLayout(header_layout)

        # Descripción
        desc_label = QLabel(
            "Las colecciones inteligentes son filtros guardados que se actualizan automáticamente"
        )
        desc_label.setStyleSheet("color: #808080; font-size: 9pt; font-style: italic;")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14pt;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar colecciones por nombre o descripción...")
        self.search_input.textChanged.connect(self.filter_collections)
        search_layout.addWidget(self.search_input)

        main_layout.addLayout(search_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3e3e42;")
        main_layout.addWidget(separator)

        # Área de scroll para las colecciones
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container para los cards
        self.collections_container = QWidget()
        self.collections_layout = QVBoxLayout(self.collections_container)
        self.collections_layout.setSpacing(10)
        self.collections_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.collections_container)
        main_layout.addWidget(scroll, 1)

        # Estadísticas generales
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            color: #808080;
            font-size: 9pt;
            padding: 8px;
            background-color: #252526;
            border-radius: 4px;
        """)
        main_layout.addWidget(self.stats_label)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_collections)
        buttons_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

    def load_collections(self, search_query: str = ""):
        """Cargar y mostrar colecciones"""
        try:
            # Limpiar container
            while self.collections_layout.count():
                child = self.collections_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Obtener colecciones con conteo de items
            if search_query:
                collections = self.manager.search_collections(search_query)
                # Agregar item_count para cada colección
                for collection in collections:
                    collection['item_count'] = self.manager.get_collection_count(collection['id'])
            else:
                collections = self.manager.get_all_collections_with_count()

            # Crear cards
            if collections:
                for collection in collections:
                    card = SmartCollectionCard(collection, self)
                    card.view_clicked.connect(self.view_collection_items)
                    card.edit_clicked.connect(self.edit_collection)
                    card.delete_clicked.connect(self.delete_collection)
                    self.collections_layout.addWidget(card)
            else:
                # Mensaje cuando no hay colecciones
                no_collections_label = QLabel("No se encontraron colecciones inteligentes")
                no_collections_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_collections_label.setStyleSheet("""
                    color: #808080;
                    font-size: 12pt;
                    padding: 40px;
                """)
                self.collections_layout.addWidget(no_collections_label)

            # Agregar stretch al final
            self.collections_layout.addStretch()

            # Actualizar estadísticas
            self.update_statistics()

        except Exception as e:
            logger.error(f"Error loading smart collections: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar colecciones:\n{str(e)}")

    def filter_collections(self):
        """Filtrar colecciones según el texto de búsqueda"""
        search_query = self.search_input.text().strip()
        self.load_collections(search_query)

    def update_statistics(self):
        """Actualizar estadísticas generales"""
        try:
            stats = self.manager.get_statistics()
            stats_text = (
                f"📊 Total: {stats['total_collections']} colecciones | "
                f"✅ Activas: {stats['active_collections']}"
            )
            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats_label.setText("📊 Estadísticas no disponibles")

    def create_new_collection(self):
        """Abrir diálogo para crear nueva colección"""
        try:
            from views.dialogs.smart_collection_editor_dialog import SmartCollectionEditorDialog

            dialog = SmartCollectionEditorDialog(self.db_path, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_collections()
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Colección inteligente creada correctamente"
                )
        except Exception as e:
            logger.error(f"Error creating smart collection: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al crear colección:\n{str(e)}")

    def edit_collection(self, collection_id: int):
        """Abrir diálogo para editar colección"""
        try:
            from views.dialogs.smart_collection_editor_dialog import SmartCollectionEditorDialog

            dialog = SmartCollectionEditorDialog(self.db_path, collection_id=collection_id, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_collections()
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Colección inteligente actualizada correctamente"
                )
        except Exception as e:
            logger.error(f"Error editing smart collection: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al editar colección:\n{str(e)}")

    def delete_collection(self, collection_id: int):
        """Eliminar una colección inteligente"""
        try:
            # Obtener información de la colección
            collection = self.manager.get_collection(collection_id)
            if not collection:
                QMessageBox.warning(self, "Advertencia", "Colección no encontrada")
                return

            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Estás seguro de que deseas eliminar la colección '{collection['name']}'?\n\n"
                f"Esto no afectará los items, solo el filtro guardado.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.manager.delete_collection(collection_id)
                if success:
                    self.load_collections()
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "Colección eliminada correctamente"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo eliminar la colección"
                    )
        except Exception as e:
            logger.error(f"Error deleting smart collection: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al eliminar colección:\n{str(e)}")

    def view_collection_items(self, collection_id: int):
        """Ver los items de una colección"""
        try:
            # Emitir señal para que el parent maneje la visualización
            self.view_collection.emit(collection_id)
        except Exception as e:
            logger.error(f"Error viewing collection items: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                "Error",
                "No se pudieron ver los items de la colección"
            )


if __name__ == "__main__":
    """Test del diálogo"""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)

    dialog = SmartCollectionsDialog()
    dialog.show()

    sys.exit(app.exec())
