"""
Table Group Widget - Agrupa items de tabla con navegación
Muestra una vista compacta de tabla con botón para ver completa
"""

import sys
from pathlib import Path
import logging
import json
from typing import List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item

logger = logging.getLogger(__name__)


class TableGroupWidget(QFrame):
    """
    Widget que agrupa items de una tabla.

    Features:
    - Header con nombre de tabla y conteo de items
    - Preview de tabla (primeras 3 filas)
    - Botón para ver tabla completa
    - Botón para copiar celda individual

    Señales:
        view_table_clicked(str): Emitida cuando se solicita ver tabla completa
        cell_copied(str, int, int): Emitida cuando se copia una celda (table_name, row, col)
    """

    view_table_clicked = pyqtSignal(str)  # table_name
    cell_copied = pyqtSignal(str, int, int)  # table_name, row, col

    def __init__(self, table_name: str, table_items: List[Dict], parent=None):
        """
        Inicializa el widget de grupo de tabla.

        Args:
            table_name: Nombre de la tabla
            table_items: Lista de items de la tabla (dicts)
            parent: Widget padre
        """
        super().__init__(parent)
        self.table_name = table_name
        self.table_items = table_items

        # Estructura reconstruida
        self.rows = 0
        self.cols = 0
        self.cells = {}
        self.column_names = []

        self.init_ui()
        self.reconstruct_table()
        self.populate_preview()

    def init_ui(self):
        """Inicializa la interfaz del widget."""
        # Estilo del frame
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Ícono + Nombre de tabla
        table_icon = QLabel("📊")
        table_icon.setStyleSheet("font-size: 16pt;")
        header_layout.addWidget(table_icon)

        self.table_label = QLabel(self.table_name)
        table_font = QFont()
        table_font.setPointSize(12)
        table_font.setBold(True)
        self.table_label.setFont(table_font)
        self.table_label.setStyleSheet("color: #f093fb;")
        header_layout.addWidget(self.table_label)

        header_layout.addStretch()

        # Contador de items
        self.count_label = QLabel(f"{len(self.table_items)} items")
        self.count_label.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        header_layout.addWidget(self.count_label)

        # Botón ver tabla completa
        self.view_button = QPushButton("🗂️ Ver Completa")
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.view_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_button.clicked.connect(self.on_view_clicked)
        header_layout.addWidget(self.view_button)

        layout.addLayout(header_layout)

        # Tabla preview (solo primeras 3 filas)
        self.preview_table = QTableWidget()
        self.preview_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                font-size: 9pt;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #00d4ff;
                padding: 6px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
                font-size: 8pt;
            }
        """)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.preview_table.verticalHeader().setDefaultSectionSize(25)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.preview_table.setMaximumHeight(150)  # Altura limitada para preview

        layout.addWidget(self.preview_table)

        # Nota si hay más filas
        self.more_rows_label = QLabel()
        self.more_rows_label.setStyleSheet("color: #858585; font-size: 8pt; font-style: italic;")
        layout.addWidget(self.more_rows_label)

    def reconstruct_table(self):
        """Reconstruye la estructura de tabla desde items."""
        max_row = 0
        max_col = 0

        for item in self.table_items:
            try:
                orden = json.loads(item['orden_table'])
                row, col = orden[0], orden[1]

                max_row = max(max_row, row)
                max_col = max(max_col, col)

                self.cells[(row, col)] = {
                    'content': item['content'],
                    'label': item['label']
                }
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning(f"Invalid orden_table: {e}")
                continue

        self.rows = max_row + 1
        self.cols = max_col + 1

        # Extraer nombres de columnas
        for col in range(self.cols):
            cell = self.cells.get((0, col))
            if cell:
                self.column_names.append(cell['label'])
            else:
                self.column_names.append(f"COL_{col+1}")

    def populate_preview(self):
        """Llena la tabla preview con primeras 3 filas."""
        preview_rows = min(3, self.rows)

        self.preview_table.setRowCount(preview_rows)
        self.preview_table.setColumnCount(self.cols)
        self.preview_table.setHorizontalHeaderLabels(self.column_names)

        # Llenar celdas
        for row in range(preview_rows):
            for col in range(self.cols):
                cell_data = self.cells.get((row, col))
                if cell_data:
                    content = cell_data['content']
                    # Truncar contenido largo
                    if len(content) > 50:
                        content = content[:50] + "..."
                    item = QTableWidgetItem(content)
                    item.setToolTip(cell_data['content'])  # Tooltip con contenido completo
                    self.preview_table.setItem(row, col, item)

        # Auto-resize columnas
        self.preview_table.resizeColumnsToContents()

        # Limitar ancho máximo de columnas
        for col in range(self.cols):
            width = self.preview_table.columnWidth(col)
            if width > 200:
                self.preview_table.setColumnWidth(col, 200)

        # Mostrar nota si hay más filas
        if self.rows > 3:
            remaining = self.rows - 3
            self.more_rows_label.setText(f"... y {remaining} fila(s) más. Haz clic en 'Ver Completa' para ver todas.")
        else:
            self.more_rows_label.hide()

    def on_view_clicked(self):
        """Maneja clic en botón ver tabla completa."""
        self.view_table_clicked.emit(self.table_name)
        logger.info(f"View table clicked: {self.table_name}")
