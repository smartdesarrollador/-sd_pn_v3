"""
Table Editor Step - Paso 2: Editor de tabla para ingreso de datos

Este step permite:
- Editar tabla con navegación Tab/Enter
- Copy/Paste desde Excel/Sheets
- Indicador de progreso (celdas llenas)
- Limpiar tabla
- Exportar a portapapeles
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent
import pyperclip

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class TableEditorStep(QWidget):
    """
    Step 2: Editor de tabla para ingreso de datos.

    Features:
    - Tabla editable con doble clic
    - Navegación con Tab/Enter
    - Copy/Paste desde Excel/Sheets
    - Indicador de celdas llenas
    - Botones: Limpiar, Copiar todo
    """

    # Señal emitida cuando cambia el número de celdas llenas
    cells_filled_changed = pyqtSignal(int, int)  # (filled, total)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.rows = 0
        self.cols = 0
        self.column_names = []

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del step."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título del step
        title = QLabel("✏️ Ingreso de Datos")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Descripción
        desc = QLabel(
            "Ingresa los datos de tu tabla. Puedes:\n"
            "• Hacer doble clic en cualquier celda para editar\n"
            "• Navegar con Tab, Shift+Tab, Enter, flechas\n"
            "• Copiar/Pegar desde Excel o Google Sheets (Ctrl+V)"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #aaaaaa; font-size: 9pt; padding: 0 10px 5px 10px;")
        layout.addWidget(desc)

        # Barra de progreso
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_label = QLabel("Celdas llenas: 0 / 0")
        self.progress_label.setStyleSheet("color: #cccccc; font-size: 10pt;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #1e1e1e;
                text-align: center;
                color: #cccccc;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar, 1)

        layout.addLayout(progress_layout)

        # Tabla editable
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
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

        # Configurar tabla
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setDefaultSectionSize(30)

        # Conectar señal de cambio de datos
        self.table.itemChanged.connect(self.on_cell_changed)

        layout.addWidget(self.table, 1)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.clear_button = QPushButton("🗑️ Limpiar Tabla")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #662222;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #882222;
            }
        """)
        self.clear_button.clicked.connect(self.clear_table)
        buttons_layout.addWidget(self.clear_button)

        buttons_layout.addStretch()

        self.copy_button = QPushButton("📋 Copiar Todo")
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
        """)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(self.copy_button)

        layout.addLayout(buttons_layout)

    def setup_table(self, rows: int, cols: int, column_names: list):
        """
        Configura la tabla con dimensiones y nombres de columnas.

        Args:
            rows: Número de filas
            cols: Número de columnas
            column_names: Lista de nombres de columnas
        """
        self.rows = rows
        self.cols = cols
        self.column_names = column_names

        # Configurar tabla
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # Establecer headers
        self.table.setHorizontalHeaderLabels(column_names[:cols])

        # Inicializar celdas vacías
        for row in range(rows):
            for col in range(cols):
                item = QTableWidgetItem("")
                self.table.setItem(row, col, item)

        # Actualizar progreso
        self.update_progress()

        logger.info(f"Table setup: {rows}x{cols} with columns: {column_names}")

    def on_cell_changed(self, item):
        """Maneja cambios en celdas de la tabla."""
        self.update_progress()

    def update_progress(self):
        """Actualiza barra de progreso y label."""
        total_cells = self.rows * self.cols
        filled_cells = self.get_filled_cells_count()

        percentage = int((filled_cells / total_cells) * 100) if total_cells > 0 else 0

        self.progress_label.setText(f"Celdas llenas: {filled_cells} / {total_cells}")
        self.progress_bar.setValue(percentage)

        # Emitir señal
        self.cells_filled_changed.emit(filled_cells, total_cells)

    def get_filled_cells_count(self) -> int:
        """Retorna el número de celdas con datos."""
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    count += 1
        return count

    def get_table_data(self) -> list:
        """
        Retorna los datos de la tabla como lista 2D.

        Returns:
            List[List[str]]: Matriz de datos
        """
        data = []
        for row in range(self.rows):
            row_data = []
            for col in range(self.cols):
                item = self.table.item(row, col)
                cell_value = item.text().strip() if item else ""
                row_data.append(cell_value)
            data.append(row_data)

        return data

    def set_table_data(self, data: list):
        """
        Establece los datos de la tabla desde una lista 2D.

        Args:
            data: Matriz de datos
        """
        # Bloquear señales temporalmente para evitar múltiples updates
        self.table.blockSignals(True)

        for row_idx, row_data in enumerate(data):
            if row_idx >= self.rows:
                break

            for col_idx, cell_value in enumerate(row_data):
                if col_idx >= self.cols:
                    break

                item = self.table.item(row_idx, col_idx)
                if item:
                    item.setText(str(cell_value))

        self.table.blockSignals(False)
        self.update_progress()

    def clear_table(self):
        """Limpia todos los datos de la tabla."""
        response = QMessageBox.question(
            self,
            "Limpiar Tabla",
            "¿Estás seguro de que deseas limpiar todos los datos de la tabla?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if response == QMessageBox.StandardButton.Yes:
            self.table.blockSignals(True)

            for row in range(self.rows):
                for col in range(self.cols):
                    item = self.table.item(row, col)
                    if item:
                        item.setText("")

            self.table.blockSignals(False)
            self.update_progress()

            logger.info("Table cleared")

    def copy_to_clipboard(self):
        """Copia toda la tabla al portapapeles en formato TSV."""
        try:
            # Generar texto TSV (Tab Separated Values)
            lines = []

            # Headers
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.cols)]
            lines.append('\t'.join(headers))

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

            QMessageBox.information(
                self,
                "Copiado",
                f"Tabla copiada al portapapeles ({len(lines)-1} filas)"
            )

            logger.info("Table copied to clipboard")

        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo copiar al portapapeles:\n{str(e)}"
            )

    def keyPressEvent(self, event: QKeyEvent):
        """Maneja eventos de teclado para paste."""
        # Ctrl+V para pegar
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        """Pega datos desde el portapapeles (formato TSV/CSV)."""
        try:
            clipboard_text = pyperclip.paste()

            if not clipboard_text.strip():
                return

            # Parsear datos (asumiendo TSV o CSV)
            lines = clipboard_text.strip().split('\n')
            data = []

            for line in lines:
                # Intentar con tabs primero, luego comas
                if '\t' in line:
                    row = line.split('\t')
                else:
                    row = line.split(',')

                data.append(row)

            # Aplicar datos a la tabla
            self.set_table_data(data)

            filled = self.get_filled_cells_count()

            QMessageBox.information(
                self,
                "Datos Pegados",
                f"Se pegaron {len(data)} filas desde el portapapeles.\n"
                f"Celdas llenas: {filled}"
            )

            logger.info(f"Pasted {len(data)} rows from clipboard")

        except Exception as e:
            logger.error(f"Error pasting from clipboard: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo pegar desde el portapapeles:\n{str(e)}"
            )

    def is_valid(self) -> bool:
        """Valida que haya al menos algunos datos."""
        filled_cells = self.get_filled_cells_count()
        return filled_cells > 0
