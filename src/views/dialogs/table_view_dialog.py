"""
Table View Dialog - Visualización de tablas completas
Muestra todos los items de una tabla en formato tabular con opciones de exportación
"""

import sys
from pathlib import Path
import logging
import json

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QCursor
import pyperclip

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_manager import DBManager
from views.dialogs.table_export_dialog import TableExportDialog
from views.dialogs.table_editor_dialog import TableEditorDialog
from views.dialogs.table_rename_dialog import TableRenameDialog
from controllers.table_controller import TableController

logger = logging.getLogger(__name__)


class TableViewDialog(QDialog):
    """
    Diálogo para visualizar tabla completa de items.

    Features:
    - Vista tabular completa de todos los items
    - Exportación a portapapeles (TSV)
    - Copy individual de celdas
    - Navegación entre celdas
    - Indicador de dimensiones
    - Botón para editar tabla (futuro)

    Señales:
        cell_copied(str): Emitida cuando se copia contenido de celda
        table_updated(str): Emitida cuando se actualiza la tabla
        table_deleted(str): Emitida cuando se elimina la tabla
        table_renamed(str, str): Emitida cuando se renombra (old_name, new_name)
    """

    cell_copied = pyqtSignal(str)  # (table_name)
    table_updated = pyqtSignal(str)  # (table_name)
    table_deleted = pyqtSignal(str)  # (table_name)
    table_renamed = pyqtSignal(str, str)  # (old_name, new_name)

    def __init__(self, db_manager: DBManager, table_name: str, parent=None):
        """
        Inicializa el diálogo de vista de tabla.

        Args:
            db_manager: Instancia de DBManager
            table_name: Nombre de la tabla a visualizar
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = db_manager
        self.table_name = table_name
        self.table_controller = TableController(db_manager)

        # Data de la tabla
        self.table_items = []
        self.rows = 0
        self.cols = 0
        self.column_names = []

        self.init_ui()
        self.load_table_data()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle(f"Vista de Tabla: {self.table_name}")
        self.setMinimumSize(900, 600)
        self.setModal(False)  # Non-modal para permitir copiar a otras apps

        # Aplicar tema oscuro
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
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton#primary_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#primary_button:hover {
                background-color: #005a9e;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                font-size: 9pt;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #00d4ff;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
        """)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        # Título
        title_label = QLabel(f"📊 {self.table_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00d4ff;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Indicador de dimensiones
        self.dimensions_label = QLabel("0 × 0")
        self.dimensions_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        header_layout.addWidget(self.dimensions_label)

        layout.addLayout(header_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setStyleSheet(self.styleSheet())
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table, 1)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Botón copiar selección
        self.copy_cell_button = QPushButton("📋 Copiar Celda")
        self.copy_cell_button.setToolTip("Copia el contenido de la celda seleccionada")
        self.copy_cell_button.clicked.connect(self.copy_selected_cell)
        buttons_layout.addWidget(self.copy_cell_button)

        # Botón copiar toda la tabla
        self.copy_all_button = QPushButton("📑 Copiar Todo")
        self.copy_all_button.setToolTip("Copia toda la tabla en formato TSV")
        self.copy_all_button.clicked.connect(self.copy_entire_table)
        buttons_layout.addWidget(self.copy_all_button)

        # Botón exportar
        self.export_button = QPushButton("📤 Exportar...")
        self.export_button.setToolTip("Exporta la tabla a CSV, JSON u otros formatos")
        self.export_button.setObjectName("primary_button")
        self.export_button.clicked.connect(self.export_table)
        buttons_layout.addWidget(self.export_button)

        buttons_layout.addStretch()

        # Botón editar
        self.edit_button = QPushButton("✏️ Editar")
        self.edit_button.setToolTip("Edita los datos de la tabla")
        self.edit_button.clicked.connect(self.edit_table)
        buttons_layout.addWidget(self.edit_button)

        # Botón renombrar
        self.rename_button = QPushButton("🏷️ Renombrar")
        self.rename_button.setToolTip("Cambia el nombre de la tabla")
        self.rename_button.clicked.connect(self.rename_table)
        buttons_layout.addWidget(self.rename_button)

        # Botón eliminar
        self.delete_button = QPushButton("🗑️ Eliminar")
        self.delete_button.setToolTip("Elimina toda la tabla")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #662222;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #882222;
            }
        """)
        self.delete_button.clicked.connect(self.delete_table)
        buttons_layout.addWidget(self.delete_button)

        # Botón cerrar
        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

    def load_table_data(self):
        """Carga los datos de la tabla desde la BD."""
        try:
            logger.info(f"Loading table data: {self.table_name}")

            # Obtener items de la tabla
            self.table_items = self.db.get_table_items(self.table_name)

            if not self.table_items:
                logger.warning(f"Table '{self.table_name}' not found or empty")
                QMessageBox.warning(
                    self,
                    "Tabla Vacía",
                    f"La tabla '{self.table_name}' no tiene datos."
                )
                self.close()
                return

            # Reconstruir estructura de tabla
            self.reconstruct_table()

            # Llenar tabla UI
            self.populate_table_widget()

            logger.info(f"Table loaded: {self.rows}x{self.cols}")

        except Exception as e:
            logger.error(f"Error loading table: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar tabla:\n{str(e)}"
            )
            self.close()

    def reconstruct_table(self):
        """Reconstruye la estructura de tabla desde items de BD."""
        # Obtener dimensiones y columnas
        max_row = 0
        max_col = 0
        cells = {}

        for item in self.table_items:
            # Parsear orden_table [row, col]
            try:
                orden = json.loads(item['orden_table'])
                row, col = orden[0], orden[1]

                # Actualizar máximos
                max_row = max(max_row, row)
                max_col = max(max_col, col)

                # Guardar celda
                cells[(row, col)] = {
                    'content': item['content'],
                    'label': item['label']
                }

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning(f"Invalid orden_table for item {item.get('id')}: {e}")
                continue

        self.rows = max_row + 1
        self.cols = max_col + 1

        # Extraer nombres de columnas (de la primera fila)
        self.column_names = []
        for col in range(self.cols):
            cell = cells.get((0, col))
            if cell:
                self.column_names.append(cell['label'])
            else:
                self.column_names.append(f"COL_{col+1}")

        # Guardar celdas
        self.cells = cells

    def populate_table_widget(self):
        """Llena el QTableWidget con los datos."""
        # Configurar tabla
        self.table.setRowCount(self.rows)
        self.table.setColumnCount(self.cols)
        self.table.setHorizontalHeaderLabels(self.column_names)

        # Llenar celdas
        for (row, col), cell_data in self.cells.items():
            content = cell_data['content']
            item = QTableWidgetItem(content)
            item.setToolTip(content)  # Tooltip con contenido completo
            self.table.setItem(row, col, item)

        # Actualizar label de dimensiones
        self.dimensions_label.setText(f"{self.rows} filas × {self.cols} columnas")

        # Auto-resize columnas al contenido
        self.table.resizeColumnsToContents()

        # Limitar ancho máximo de columnas
        for col in range(self.cols):
            width = self.table.columnWidth(col)
            if width > 300:
                self.table.setColumnWidth(col, 300)

    def copy_selected_cell(self):
        """Copia el contenido de la celda seleccionada al portapapeles."""
        current_item = self.table.currentItem()

        if not current_item:
            QMessageBox.information(
                self,
                "Selección Vacía",
                "Por favor selecciona una celda primero."
            )
            return

        content = current_item.text()

        try:
            pyperclip.copy(content)

            # Emitir señal
            self.cell_copied.emit(self.table_name)

            # Feedback visual temporal
            row = self.table.currentRow()
            col = self.table.currentColumn()

            logger.info(f"Cell copied: [{row}, {col}] = '{content[:50]}...'")

            # Mostrar mensaje en status (si existe)
            # self.statusBar().showMessage(f"✓ Celda [{row}, {col}] copiada", 2000)

        except Exception as e:
            logger.error(f"Error copying cell: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo copiar al portapapeles:\n{str(e)}"
            )

    def copy_entire_table(self):
        """Copia toda la tabla al portapapeles en formato TSV."""
        try:
            lines = []

            # Headers
            lines.append('\t'.join(self.column_names))

            # Data rows
            for row in range(self.rows):
                row_data = []
                for col in range(self.cols):
                    item = self.table.item(row, col)
                    cell_value = item.text() if item else ""
                    row_data.append(cell_value)
                lines.append('\t'.join(row_data))

            tsv_text = '\n'.join(lines)

            # Copiar al portapapeles
            pyperclip.copy(tsv_text)

            # Emitir señal
            self.cell_copied.emit(self.table_name)

            QMessageBox.information(
                self,
                "Tabla Copiada",
                f"Tabla '{self.table_name}' copiada al portapapeles.\n\n"
                f"Formato: TSV (Tab Separated Values)\n"
                f"Filas: {self.rows}\n"
                f"Columnas: {self.cols}"
            )

            logger.info(f"Entire table copied: {self.table_name}")

        except Exception as e:
            logger.error(f"Error copying table: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo copiar la tabla:\n{str(e)}"
            )

    def show_context_menu(self, position: QPoint):
        """Muestra menú contextual en celda."""
        item = self.table.itemAt(position)

        if not item:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #007acc;
            }
        """)

        # Acción copiar celda
        copy_action = menu.addAction("📋 Copiar Celda")
        copy_action.triggered.connect(self.copy_selected_cell)

        # Acción copiar todo
        menu.addSeparator()
        copy_all_action = menu.addAction("📑 Copiar Toda la Tabla")
        copy_all_action.triggered.connect(self.copy_entire_table)

        # Acción exportar
        menu.addSeparator()
        export_action = menu.addAction("📤 Exportar Tabla...")
        export_action.triggered.connect(self.export_table)

        # Opciones avanzadas
        menu.addSeparator()
        edit_action = menu.addAction("✏️ Editar Tabla...")
        edit_action.triggered.connect(self.edit_table)

        rename_action = menu.addAction("🏷️ Renombrar Tabla...")
        rename_action.triggered.connect(self.rename_table)

        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Eliminar Tabla...")
        delete_action.triggered.connect(self.delete_table)

        # Mostrar menú
        menu.exec(QCursor.pos())

    def export_table(self):
        """Abre diálogo de exportación."""
        try:
            # Obtener datos de tabla
            table_data = self.get_table_data()

            # Abrir diálogo de exportación
            dialog = TableExportDialog(
                table_name=self.table_name,
                table_data=table_data,
                column_names=self.column_names,
                parent=self
            )

            dialog.export_completed.connect(self.on_export_completed)
            dialog.exec()

        except Exception as e:
            logger.error(f"Error opening export dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir diálogo de exportación:\n{str(e)}"
            )

    def get_table_data(self) -> list:
        """Obtiene datos de la tabla como lista 2D."""
        data = []
        for row in range(self.rows):
            row_data = []
            for col in range(self.cols):
                cell_data = self.cells.get((row, col))
                if cell_data:
                    row_data.append(cell_data['content'])
                else:
                    row_data.append("")
            data.append(row_data)
        return data

    def on_export_completed(self, file_path: str):
        """Maneja completación de exportación."""
        logger.info(f"Table exported to: {file_path}")
        # Podríamos mostrar notificación o abrir carpeta, etc.

    def edit_table(self):
        """Abre editor de tabla."""
        try:
            editor = TableEditorDialog(self.db, self.table_name, parent=self)
            editor.table_updated.connect(self.on_table_updated)

            result = editor.exec()

            if result == QDialog.DialogCode.Accepted:
                # Recargar datos actualizados
                self.load_table_data()

        except Exception as e:
            logger.error(f"Error opening table editor: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir editor:\n{str(e)}"
            )

    def rename_table(self):
        """Abre diálogo de renombrado."""
        try:
            rename_dialog = TableRenameDialog(self.db, self.table_name, parent=self)
            rename_dialog.table_renamed.connect(self.on_table_renamed)

            result = rename_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                # El diálogo ya emitió la señal, solo cerramos este diálogo
                self.close()

        except Exception as e:
            logger.error(f"Error opening rename dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir diálogo de renombrado:\n{str(e)}"
            )

    def delete_table(self):
        """Elimina la tabla completa."""
        # Doble confirmación por ser operación destructiva
        response1 = QMessageBox.warning(
            self,
            "Eliminar Tabla",
            f"⚠️ ADVERTENCIA: Esta acción eliminará TODA la tabla '{self.table_name}' "
            f"({len(self.table_items)} items).\n\n"
            "Esta operación NO se puede deshacer.\n\n"
            "¿Estás seguro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if response1 != QMessageBox.StandardButton.Yes:
            return

        # Segunda confirmación
        response2 = QMessageBox.critical(
            self,
            "Confirmación Final",
            f"Confirma que deseas eliminar la tabla '{self.table_name}'.\n\n"
            "Escribe 'ELIMINAR' para confirmar:",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if response2 != QMessageBox.StandardButton.Ok:
            return

        # Ejecutar eliminación usando controller
        try:
            result = self.table_controller.delete_table(self.table_name)

            if result['success']:
                QMessageBox.information(
                    self,
                    "Tabla Eliminada",
                    f"Tabla '{self.table_name}' eliminada exitosamente.\n\n"
                    f"Items eliminados: {result['items_deleted']}"
                )

                # Emitir señal
                self.table_deleted.emit(self.table_name)

                # Cerrar diálogo
                self.close()

            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo eliminar la tabla:\n{result.get('error', 'Error desconocido')}"
                )

        except Exception as e:
            logger.error(f"Error deleting table: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al eliminar tabla:\n{str(e)}"
            )

    def on_table_updated(self, table_name: str):
        """Maneja actualización de tabla."""
        logger.info(f"Table updated: {table_name}")
        self.table_updated.emit(table_name)

    def on_table_renamed(self, old_name: str, new_name: str):
        """Maneja renombrado de tabla."""
        logger.info(f"Table renamed: {old_name} -> {new_name}")
        self.table_renamed.emit(old_name, new_name)

    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        # Ctrl+C para copiar celda seleccionada
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.copy_selected_cell()
        # Ctrl+Shift+C para copiar toda la tabla
        elif event.key() == Qt.Key.Key_C and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.copy_entire_table()
        # ESC para cerrar
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)

    # Crear instancia de DBManager
    from database.db_manager import DBManager
    db = DBManager()

    # Mostrar diálogo con tabla de prueba
    dialog = TableViewDialog(db, "TABLA_TEST")
    dialog.show()

    sys.exit(app.exec())
