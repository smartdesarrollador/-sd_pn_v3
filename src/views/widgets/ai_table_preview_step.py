"""
AI Table Preview Step - Paso 4: Previsualización de tabla

Este step:
- Muestra información de la tabla
- Permite revisar columnas y sus tipos
- Muestra preview de los datos
- Permite marcar/desmarcar filas para incluir
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.ai_table_data import AITableData

logger = logging.getLogger(__name__)


class AITablePreviewStep(QWidget):
    """Step 4: Previsualización de tabla."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_table = None
        self.selected_rows = []
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("👁️ Previsualización de Tabla")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Info de tabla
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 12px;
                color: #cccccc;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.info_label)

        # Info de columnas
        self.columns_label = QLabel("")
        self.columns_label.setStyleSheet(self.info_label.styleSheet())
        layout.addWidget(self.columns_label)

        # Preview de datos
        preview_label = QLabel("Preview de Datos:")
        preview_label.setStyleSheet("color: #cccccc; font-size: 10pt; font-weight: bold;")
        layout.addWidget(preview_label)

        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #00d4ff;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
        """)
        self.table_widget.setAlternatingRowColors(True)
        layout.addWidget(self.table_widget, 1)

        # Contador
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        layout.addWidget(self.counter_label)

    def set_table_data(self, ai_table: AITableData):
        """
        Establece los datos de la tabla para preview.

        Args:
            ai_table: Datos completos de la tabla
        """
        self.ai_table = ai_table

        # Actualizar info
        self.info_label.setText(
            f"Tabla: {ai_table.table_config.table_name}\n"
            f"Categoría ID: {ai_table.table_config.category_id}\n"
            f"Tags: {', '.join(ai_table.table_config.tags) if ai_table.table_config.tags else 'ninguno'}"
        )

        # Info de columnas
        columns_info = []
        for i, col in enumerate(ai_table.table_structure.columns):
            marks = []
            if col.is_sensitive:
                marks.append("[S]")
            if col.type == 'URL':
                marks.append("[U]")
            marks_str = " ".join(marks) if marks else ""
            columns_info.append(f"  {i+1}. {col.name} ({col.type}) {marks_str}")

        self.columns_label.setText(
            f"Columnas ({len(ai_table.table_structure.columns)}):\n" +
            "\n".join(columns_info)
        )

        # Configurar tabla
        self.table_widget.setRowCount(ai_table.rows_count)
        self.table_widget.setColumnCount(ai_table.cols_count)

        # Headers
        headers = [col.name for col in ai_table.table_structure.columns]
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Datos
        for row_idx, row_data in enumerate(ai_table.table_data):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                self.table_widget.setItem(row_idx, col_idx, item)

        # Ajustar columnas
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Seleccionar todas las filas por defecto
        self.selected_rows = list(range(ai_table.rows_count))

        # Actualizar contador
        self.update_counter()

        logger.info(f"Table preview set: {ai_table.rows_count}x{ai_table.cols_count}")

    def update_counter(self):
        """Actualiza el contador de filas."""
        if self.ai_table:
            total = self.ai_table.rows_count
            filled = self.ai_table.filled_cells_count
            total_cells = self.ai_table.rows_count * self.ai_table.cols_count

            self.counter_label.setText(
                f"{total} filas | "
                f"{filled}/{total_cells} celdas llenas "
                f"({self.ai_table.get_fill_percentage():.1f}%)"
            )

    def get_final_table_data(self) -> AITableData:
        """Retorna los datos finales de la tabla."""
        # Por ahora retornamos los datos sin modificar
        # En una versión futura podríamos permitir edición
        return self.ai_table

    def is_valid(self) -> bool:
        """Valida que haya datos."""
        return self.ai_table is not None and len(self.selected_rows) > 0

    def get_validation_message(self) -> str:
        """Mensaje de validación."""
        if self.ai_table is None:
            return "No hay datos de tabla cargados."
        if len(self.selected_rows) == 0:
            return "Selecciona al menos una fila para crear."
        return "Preview cargado correctamente."
