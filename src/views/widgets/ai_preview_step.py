"""AI Bulk Preview Step - Paso 4: Previsualización de items"""
import sys
from pathlib import Path
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QCheckBox, QPushButton, QHBoxLayout, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.bulk_item_data import BulkItemData

logger = logging.getLogger(__name__)

class PreviewStep(QWidget):
    """Step 4: Previsualización editable de items"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Título
        title = QLabel("👁️ Previsualizar Items")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        # Contador
        self.counter_label = QLabel("0 de 0 items seleccionados")
        self.counter_label.setStyleSheet("color: #888888; font-size: 11pt;")
        layout.addWidget(self.counter_label)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["✓", "Label", "Type", "Content (preview)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 400)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #3d3d3d;
                border: 1px solid #3d3d3d;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #00d4ff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Seleccionar Todos")
        self.select_all_btn.clicked.connect(self.select_all)
        btn_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deseleccionar Todos")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        btn_layout.addWidget(self.deselect_all_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def set_items(self, items: list):
        """Establece items para previsualizar"""
        self.items = items
        self.table.setRowCount(len(items))

        for i, item in enumerate(items):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(item.selected)
            checkbox.stateChanged.connect(self.update_counter)
            self.table.setCellWidget(i, 0, checkbox)

            # Label
            self.table.setItem(i, 1, QTableWidgetItem(item.label))

            # Type
            self.table.setItem(i, 2, QTableWidgetItem(item.type))

            # Content (preview)
            preview = item.content[:100] + "..." if len(item.content) > 100 else item.content
            content_item = QTableWidgetItem(preview)
            content_item.setToolTip(item.content)  # Tooltip con contenido completo
            self.table.setItem(i, 3, content_item)

        self.update_counter()
        logger.info(f"Preview loaded: {len(items)} items")

    def update_counter(self):
        """Actualiza contador de selección"""
        selected = sum(1 for i in range(self.table.rowCount())
                      if self.table.cellWidget(i, 0).isChecked())
        total = self.table.rowCount()
        self.counter_label.setText(f"{selected} de {total} items seleccionados")

        # Actualizar selected en items
        for i in range(len(self.items)):
            if i < self.table.rowCount():
                self.items[i].selected = self.table.cellWidget(i, 0).isChecked()

    def select_all(self):
        """Selecciona todos los items"""
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).setChecked(True)

    def deselect_all(self):
        """Deselecciona todos los items"""
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).setChecked(False)

    def get_selected_items(self) -> list:
        """Retorna items seleccionados"""
        return [item for item in self.items if item.selected]

    def has_selected_items(self) -> bool:
        """Verifica si hay items seleccionados"""
        return len(self.get_selected_items()) > 0

    def is_valid(self) -> bool:
        """Valida que haya al menos 1 item seleccionado"""
        return self.has_selected_items()
