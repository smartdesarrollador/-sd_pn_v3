"""
Tables Manager Window - Ventana de gestión de tablas
Lista, visualiza, edita y elimina todas las tablas del sistema
"""

import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QWidget, QMessageBox, QInputDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DBManager
from controllers.table_controller import TableController
from views.dialogs.table_view_dialog import TableViewDialog
from views.dialogs.table_creator_wizard import TableCreatorWizard

logger = logging.getLogger(__name__)


class TablesManagerWindow(QDialog):
    """
    Ventana de gestión de tablas.

    Features:
    - Lista de todas las tablas
    - Crear nueva tabla
    - Ver tabla completa
    - Editar/Renombrar/Eliminar desde aquí
    - Búsqueda de tablas
    - Estadísticas de cada tabla

    Señales:
        tables_changed: Emitida cuando cambian las tablas
    """

    tables_changed = pyqtSignal()

    def __init__(self, db_manager: DBManager, controller=None, parent=None):
        """
        Inicializa la ventana.

        Args:
            db_manager: Instancia de DBManager
            controller: MainController opcional
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = db_manager
        self.controller = controller
        self.table_controller = TableController(db_manager)

        self.tables = []  # Lista de tablas

        self.init_ui()
        self.load_tables()

    def init_ui(self):
        """Inicializa la interfaz."""
        self.setWindowTitle("Gestión de Tablas")
        self.setMinimumSize(800, 600)
        self.setModal(False)  # Non-modal para permitir múltiples ventanas

        # Tema oscuro
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton#new_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#new_button:hover {
                background-color: #005a9e;
            }
            QPushButton#delete_button {
                background-color: #662222;
                color: #ffffff;
            }
            QPushButton#delete_button:hover {
                background-color: #882222;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                color: #cccccc;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QFrame#info_panel {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 15px;
            }
        """)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("📊 Gestión de Tablas")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Contador de tablas
        self.count_label = QLabel("0 tablas")
        self.count_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # Descripción
        desc = QLabel("Administra todas las tablas de items del sistema")
        desc.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        layout.addWidget(desc)

        # Contenido principal (lista + botones)
        content_layout = QHBoxLayout()

        # Lista de tablas
        list_container = QVBoxLayout()

        list_header = QLabel("Tablas Disponibles:")
        list_header.setStyleSheet("font-weight: bold; font-size: 10pt;")
        list_container.addWidget(list_header)

        self.tables_list = QListWidget()
        self.tables_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.tables_list.itemDoubleClicked.connect(self.on_view_table)
        list_container.addWidget(self.tables_list)

        content_layout.addLayout(list_container, 3)

        # Panel de información y acciones
        actions_panel = QVBoxLayout()

        # Info de tabla seleccionada
        self.info_panel = QFrame()
        self.info_panel.setObjectName("info_panel")
        info_layout = QVBoxLayout(self.info_panel)

        self.info_label = QLabel("Selecciona una tabla para ver detalles")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        info_layout.addWidget(self.info_label)

        actions_panel.addWidget(self.info_panel)

        actions_panel.addSpacing(10)

        # Botones de acción
        self.new_button = QPushButton("➕ Nueva Tabla")
        self.new_button.setObjectName("new_button")
        self.new_button.setToolTip("Crea una nueva tabla de items")
        self.new_button.clicked.connect(self.on_create_table)
        actions_panel.addWidget(self.new_button)

        self.view_button = QPushButton("👁️ Ver Tabla")
        self.view_button.setEnabled(False)
        self.view_button.setToolTip("Visualiza la tabla completa")
        self.view_button.clicked.connect(self.on_view_table)
        actions_panel.addWidget(self.view_button)

        self.edit_button = QPushButton("✏️ Editar")
        self.edit_button.setEnabled(False)
        self.edit_button.setToolTip("Edita los datos de la tabla")
        self.edit_button.clicked.connect(self.on_edit_table)
        actions_panel.addWidget(self.edit_button)

        self.rename_button = QPushButton("🏷️ Renombrar")
        self.rename_button.setEnabled(False)
        self.rename_button.setToolTip("Cambia el nombre de la tabla")
        self.rename_button.clicked.connect(self.on_rename_table)
        actions_panel.addWidget(self.rename_button)

        actions_panel.addSpacing(10)

        self.delete_button = QPushButton("🗑️ Eliminar")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip("Elimina la tabla completa")
        self.delete_button.clicked.connect(self.on_delete_table)
        actions_panel.addWidget(self.delete_button)

        actions_panel.addStretch()

        # Botón refrescar
        self.refresh_button = QPushButton("🔄 Refrescar")
        self.refresh_button.setToolTip("Recarga la lista de tablas")
        self.refresh_button.clicked.connect(self.load_tables)
        actions_panel.addWidget(self.refresh_button)

        content_layout.addLayout(actions_panel, 1)

        layout.addLayout(content_layout)

        # Botón cerrar
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.close)
        close_layout.addWidget(self.close_btn)

        layout.addLayout(close_layout)

    def load_tables(self):
        """Carga todas las tablas desde la BD."""
        try:
            logger.info("Loading tables list")

            # Obtener todas las tablas
            self.tables = self.table_controller.get_tables_summary()

            # Limpiar lista
            self.tables_list.clear()

            # Agregar items
            for table_info in self.tables:
                table_name = table_info.get('table_name', 'UNKNOWN')
                item_count = table_info.get('item_count', 0)

                # Crear item de lista con formato
                item_text = f"📊 {table_name} ({item_count} items)"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, table_info)  # Guardar info completa

                self.tables_list.addItem(list_item)

            # Actualizar contador
            self.count_label.setText(f"{len(self.tables)} tabla{'s' if len(self.tables) != 1 else ''}")

            logger.info(f"Loaded {len(self.tables)} tables")

        except Exception as e:
            logger.error(f"Error loading tables: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar tablas:\n{str(e)}"
            )

    def on_selection_changed(self):
        """Maneja cambio de selección."""
        selected_items = self.tables_list.selectedItems()

        if selected_items:
            # Habilitar botones
            self.view_button.setEnabled(True)
            self.edit_button.setEnabled(True)
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)

            # Mostrar info
            table_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.show_table_info(table_info)
        else:
            # Deshabilitar botones
            self.view_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)

            # Limpiar info
            self.info_label.setText("Selecciona una tabla para ver detalles")

    def show_table_info(self, table_info: dict):
        """Muestra información de la tabla seleccionada."""
        table_name = table_info.get('table_name', 'UNKNOWN')
        item_count = table_info.get('item_count', 0)
        category_name = table_info.get('category_name', 'N/A')
        rows = table_info.get('rows', 0)
        cols = table_info.get('cols', 0)

        info_text = f"""
<b>Tabla:</b> {table_name}<br>
<b>Categoría:</b> {category_name}<br>
<b>Dimensiones:</b> {rows} × {cols}<br>
<b>Total items:</b> {item_count}<br>
        """.strip()

        self.info_label.setText(info_text)

    def get_selected_table_name(self) -> str:
        """Obtiene el nombre de la tabla seleccionada."""
        selected_items = self.tables_list.selectedItems()
        if selected_items:
            table_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
            return table_info.get('table_name', '')
        return ''

    def on_create_table(self):
        """Abre wizard de creación."""
        try:
            wizard = TableCreatorWizard(self.db, self.controller, self)
            wizard.table_created.connect(self.on_table_created)
            wizard.exec()

        except Exception as e:
            logger.error(f"Error opening table creator: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al abrir creador:\n{str(e)}")

    def on_view_table(self):
        """Abre vista de tabla."""
        table_name = self.get_selected_table_name()
        if not table_name:
            return

        try:
            dialog = TableViewDialog(self.db, table_name, parent=self)
            dialog.table_updated.connect(self.on_table_updated)
            dialog.table_deleted.connect(self.on_table_deleted)
            dialog.table_renamed.connect(self.on_table_renamed)
            dialog.show()

        except Exception as e:
            logger.error(f"Error opening table view: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al abrir vista:\n{str(e)}")

    def on_edit_table(self):
        """Abre editor de tabla."""
        table_name = self.get_selected_table_name()
        if not table_name:
            return

        # Abrir vista que tiene botón de editar
        self.on_view_table()

    def on_rename_table(self):
        """Abre diálogo de renombrado."""
        table_name = self.get_selected_table_name()
        if not table_name:
            return

        # Abrir vista que tiene botón de renombrar
        self.on_view_table()

    def on_delete_table(self):
        """Elimina la tabla."""
        table_name = self.get_selected_table_name()
        if not table_name:
            return

        # Abrir vista que tiene botón de eliminar
        self.on_view_table()

    def on_table_created(self, table_name: str, items_created: int):
        """Maneja creación de tabla."""
        logger.info(f"Table created: {table_name}")
        self.load_tables()
        self.tables_changed.emit()

    def on_table_updated(self, table_name: str):
        """Maneja actualización de tabla."""
        logger.info(f"Table updated: {table_name}")
        self.load_tables()
        self.tables_changed.emit()

    def on_table_deleted(self, table_name: str):
        """Maneja eliminación de tabla."""
        logger.info(f"Table deleted: {table_name}")
        self.load_tables()
        self.tables_changed.emit()

    def on_table_renamed(self, old_name: str, new_name: str):
        """Maneja renombrado de tabla."""
        logger.info(f"Table renamed: {old_name} -> {new_name}")
        self.load_tables()
        self.tables_changed.emit()
