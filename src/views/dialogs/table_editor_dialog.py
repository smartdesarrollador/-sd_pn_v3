"""
Table Editor Dialog - Editor de tabla existente
Permite editar datos de una tabla ya creada
"""

import sys
from pathlib import Path
import logging
import json

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import pyperclip

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_manager import DBManager
from controllers.table_controller import TableController

logger = logging.getLogger(__name__)


class TableEditorDialog(QDialog):
    """
    Diálogo para editar tabla existente.

    Features:
    - Edición de celdas
    - Navegación con Tab/Enter
    - Copy/Paste desde Excel
    - Guardar cambios
    - Cancelar sin guardar

    Señales:
        table_updated(str): Emitida cuando se actualiza la tabla
    """

    table_updated = pyqtSignal(str)  # table_name

    def __init__(self, db_manager: DBManager, table_name: str, parent=None):
        """
        Inicializa el editor de tabla.

        Args:
            db_manager: Instancia de DBManager
            table_name: Nombre de la tabla a editar
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
        self.cells = {}

        # Track changes
        self.has_changes = False

        self.init_ui()
        self.load_table_data()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle(f"Editar Tabla: {self.table_name}")
        self.setMinimumSize(900, 600)
        self.setModal(True)

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
            QPushButton#save_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#save_button:hover {
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

        title = QLabel(f"✏️ Editar: {self.table_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.dimensions_label = QLabel("0 × 0")
        self.dimensions_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        header_layout.addWidget(self.dimensions_label)

        layout.addLayout(header_layout)

        # Instrucciones
        instructions = QLabel(
            "💡 Haz doble clic en cualquier celda para editar. "
            "Usa Tab/Enter para navegar. Ctrl+V para pegar desde Excel."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #aaaaaa; font-size: 9pt; padding: 5px;")
        layout.addWidget(instructions)

        # Tabla editable
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Conectar señal de cambio
        self.table.itemChanged.connect(self.on_cell_changed)

        layout.addWidget(self.table, 1)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Botón limpiar cambios
        self.reset_button = QPushButton("🔄 Recargar Original")
        self.reset_button.setToolTip("Descarta cambios y recarga datos originales")
        self.reset_button.clicked.connect(self.reset_table)
        buttons_layout.addWidget(self.reset_button)

        buttons_layout.addStretch()

        # Botón cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_edit)
        buttons_layout.addWidget(self.cancel_button)

        # Botón guardar
        self.save_button = QPushButton("💾 Guardar Cambios")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout)

    def load_table_data(self):
        """Carga los datos de la tabla desde la BD."""
        try:
            logger.info(f"Loading table for editing: {self.table_name}")

            # Obtener items de la tabla
            self.table_items = self.db.get_table_items(self.table_name)

            if not self.table_items:
                logger.warning(f"Table '{self.table_name}' not found or empty")
                QMessageBox.warning(
                    self,
                    "Tabla Vacía",
                    f"La tabla '{self.table_name}' no tiene datos."
                )
                self.reject()
                return

            # Reconstruir estructura
            self.reconstruct_table()

            # Llenar tabla UI
            self.populate_table()

            logger.info(f"Table loaded for editing: {self.rows}x{self.cols}")

        except Exception as e:
            logger.error(f"Error loading table: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar tabla:\n{str(e)}"
            )
            self.reject()

    def reconstruct_table(self):
        """Reconstruye la estructura de tabla desde items de BD."""
        max_row = 0
        max_col = 0
        self.cells = {}

        for item in self.table_items:
            try:
                orden = json.loads(item['orden_table'])
                row, col = orden[0], orden[1]

                max_row = max(max_row, row)
                max_col = max(max_col, col)

                self.cells[(row, col)] = {
                    'content': item['content'],
                    'label': item['label'],
                    'item_id': item['id']
                }

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning(f"Invalid orden_table for item {item.get('id')}: {e}")
                continue

        self.rows = max_row + 1
        self.cols = max_col + 1

        # Extraer nombres de columnas
        self.column_names = []
        for col in range(self.cols):
            cell = self.cells.get((0, col))
            if cell:
                self.column_names.append(cell['label'])
            else:
                self.column_names.append(f"COL_{col+1}")

    def populate_table(self):
        """Llena el QTableWidget con los datos."""
        # Bloquear señales temporalmente
        self.table.blockSignals(True)

        # Configurar tabla
        self.table.setRowCount(self.rows)
        self.table.setColumnCount(self.cols)
        self.table.setHorizontalHeaderLabels(self.column_names)

        # Llenar celdas
        for (row, col), cell_data in self.cells.items():
            content = cell_data['content']
            item = QTableWidgetItem(content)
            self.table.setItem(row, col, item)

        # Actualizar label de dimensiones
        self.dimensions_label.setText(f"{self.rows} filas × {self.cols} columnas")

        # Auto-resize columnas
        self.table.resizeColumnsToContents()

        # Limitar ancho máximo
        for col in range(self.cols):
            width = self.table.columnWidth(col)
            if width > 300:
                self.table.setColumnWidth(col, 300)

        # Reactivar señales
        self.table.blockSignals(False)

    def on_cell_changed(self, item):
        """Maneja cambios en celdas."""
        self.has_changes = True
        logger.debug(f"Cell changed: [{item.row()}, {item.column()}]")

    def reset_table(self):
        """Recarga datos originales descartando cambios."""
        if self.has_changes:
            response = QMessageBox.question(
                self,
                "Descartar Cambios",
                "¿Estás seguro de que deseas descartar todos los cambios?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response != QMessageBox.StandardButton.Yes:
                return

        # Recargar datos
        self.load_table_data()
        self.has_changes = False

        logger.info("Table reset to original data")

    def cancel_edit(self):
        """Cancela edición."""
        if self.has_changes:
            response = QMessageBox.question(
                self,
                "Cancelar Edición",
                "Tienes cambios sin guardar. ¿Estás seguro de que deseas cancelar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response != QMessageBox.StandardButton.Yes:
                return

        self.reject()

    def save_changes(self):
        """Guarda cambios en la BD."""
        if not self.has_changes:
            QMessageBox.information(
                self,
                "Sin Cambios",
                "No hay cambios para guardar."
            )
            return

        # Confirmar guardado
        response = QMessageBox.question(
            self,
            "Guardar Cambios",
            f"¿Deseas guardar los cambios en la tabla '{self.table_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        try:
            # Obtener datos actuales de la tabla
            table_data = []
            for row in range(self.rows):
                row_data = []
                for col in range(self.cols):
                    item = self.table.item(row, col)
                    cell_value = item.text() if item else ""
                    row_data.append(cell_value)
                table_data.append(row_data)

            # Usar controller para actualizar
            result = self.table_controller.update_table(
                table_name=self.table_name,
                table_data=table_data,
                column_names=self.column_names
            )

            if result['success']:
                QMessageBox.information(
                    self,
                    "Cambios Guardados",
                    f"Tabla '{self.table_name}' actualizada exitosamente.\n\n"
                    f"Celdas actualizadas: {result['updates_count']}"
                )

                # Emitir señal
                self.table_updated.emit(self.table_name)

                # Cerrar diálogo
                self.accept()

            else:
                errors_text = '\n'.join(result.get('errors', [])[:5])
                QMessageBox.critical(
                    self,
                    "Error al Guardar",
                    f"No se pudieron guardar todos los cambios:\n\n{errors_text}"
                )

        except Exception as e:
            logger.error(f"Error saving table changes: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar cambios:\n{str(e)}"
            )

    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        # Ctrl+V para pegar
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_from_clipboard()
        # Ctrl+S para guardar
        elif event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.save_changes()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        """Pega datos desde el portapapeles."""
        try:
            clipboard_text = pyperclip.paste()

            if not clipboard_text.strip():
                return

            # Parsear datos (TSV o CSV)
            lines = clipboard_text.strip().split('\n')

            # Obtener celda actual
            current_row = self.table.currentRow()
            current_col = self.table.currentColumn()

            if current_row < 0 or current_col < 0:
                current_row = 0
                current_col = 0

            # Bloquear señales
            self.table.blockSignals(True)

            # Pegar datos
            pasted_cells = 0
            for line_idx, line in enumerate(lines):
                target_row = current_row + line_idx
                if target_row >= self.rows:
                    break

                # Separar por tabs o comas
                if '\t' in line:
                    cells = line.split('\t')
                else:
                    cells = line.split(',')

                for cell_idx, cell_value in enumerate(cells):
                    target_col = current_col + cell_idx
                    if target_col >= self.cols:
                        break

                    item = self.table.item(target_row, target_col)
                    if item:
                        item.setText(cell_value.strip())
                        pasted_cells += 1

            # Reactivar señales
            self.table.blockSignals(False)

            # Marcar como modificado
            if pasted_cells > 0:
                self.has_changes = True

            logger.info(f"Pasted {pasted_cells} cells from clipboard")

        except Exception as e:
            logger.error(f"Error pasting: {e}")
