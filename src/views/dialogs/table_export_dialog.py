"""
Table Export Dialog - Diálogo para exportar tablas a diferentes formatos
"""

import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QGroupBox,
    QFileDialog, QLineEdit, QCheckBox, QMessageBox,
    QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.table_exporter import TableExporter

logger = logging.getLogger(__name__)


class TableExportDialog(QDialog):
    """
    Diálogo para exportar tabla a archivo.

    Features:
    - Selección de formato (CSV, TSV, JSON, JSON Records)
    - Opciones por formato (headers, metadata, pretty print)
    - Selección de ubicación de archivo
    - Preview de nombre de archivo sugerido
    - Resumen de tabla antes de exportar

    Señales:
        export_completed(str): Emitida cuando se completa exportación (file_path)
    """

    export_completed = pyqtSignal(str)  # file_path

    def __init__(
        self,
        table_name: str,
        table_data: list,
        column_names: list,
        parent=None
    ):
        """
        Inicializa el diálogo de exportación.

        Args:
            table_name: Nombre de la tabla
            table_data: Matriz de datos
            column_names: Nombres de columnas
            parent: Widget padre
        """
        super().__init__(parent)
        self.table_name = table_name
        self.table_data = table_data
        self.column_names = column_names

        # Default output path
        self.output_path = None

        self.init_ui()
        self.update_summary()
        self.update_suggested_filename()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle(f"Exportar Tabla: {self.table_name}")
        self.setMinimumWidth(600)
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
            QPushButton#export_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#export_button:hover {
                background-color: #005a9e;
            }
            QRadioButton {
                color: #cccccc;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox {
                color: #cccccc;
                spacing: 8px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                background-color: #252525;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                color: #cccccc;
            }
        """)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel(f"📤 Exportar Tabla: {self.table_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        # Resumen de tabla
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #aaaaaa; font-size: 9pt; padding: 10px;")
        layout.addWidget(self.summary_label)

        # Grupo: Formato
        format_group = QGroupBox("Formato de Exportación")
        format_layout = QVBoxLayout()

        self.format_group = QButtonGroup(self)

        self.csv_radio = QRadioButton("CSV (Comma Separated Values)")
        self.csv_radio.setChecked(True)
        self.format_group.addButton(self.csv_radio, 1)
        format_layout.addWidget(self.csv_radio)

        self.tsv_radio = QRadioButton("TSV (Tab Separated Values)")
        self.format_group.addButton(self.tsv_radio, 2)
        format_layout.addWidget(self.tsv_radio)

        self.json_radio = QRadioButton("JSON (Matriz)")
        self.format_group.addButton(self.json_radio, 3)
        format_layout.addWidget(self.json_radio)

        self.json_records_radio = QRadioButton("JSON (Registros/Objetos)")
        self.format_group.addButton(self.json_records_radio, 4)
        format_layout.addWidget(self.json_records_radio)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Conectar cambio de formato para actualizar extensión
        self.format_group.buttonClicked.connect(self.update_suggested_filename)

        # Grupo: Opciones
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()

        self.include_headers_check = QCheckBox("Incluir nombres de columnas (headers)")
        self.include_headers_check.setChecked(True)
        options_layout.addWidget(self.include_headers_check)

        self.include_metadata_check = QCheckBox("Incluir metadata (solo JSON)")
        self.include_metadata_check.setChecked(True)
        options_layout.addWidget(self.include_metadata_check)

        self.pretty_json_check = QCheckBox("Formatear JSON con indentación")
        self.pretty_json_check.setChecked(True)
        options_layout.addWidget(self.pretty_json_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Grupo: Ubicación
        location_group = QGroupBox("Ubicación del Archivo")
        location_layout = QFormLayout()

        # Sugerencia de nombre
        self.filename_input = QLineEdit()
        self.filename_input.setReadOnly(True)
        location_layout.addRow("Nombre sugerido:", self.filename_input)

        # Botón seleccionar ubicación
        self.browse_button = QPushButton("📁 Seleccionar Ubicación...")
        self.browse_button.clicked.connect(self.browse_location)
        location_layout.addRow("", self.browse_button)

        # Ruta completa
        self.path_label = QLabel("No seleccionado")
        self.path_label.setStyleSheet("color: #858585; font-size: 9pt; font-style: italic;")
        self.path_label.setWordWrap(True)
        location_layout.addRow("Ruta completa:", self.path_label)

        location_group.setLayout(location_layout)
        layout.addWidget(location_group)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        self.export_button = QPushButton("📤 Exportar")
        self.export_button.setObjectName("export_button")
        self.export_button.clicked.connect(self.export_table)
        buttons_layout.addWidget(self.export_button)

        layout.addLayout(buttons_layout)

    def update_summary(self):
        """Actualiza el resumen de la tabla."""
        summary = TableExporter.get_export_summary(
            self.table_name,
            self.table_data,
            self.column_names
        )

        summary_text = (
            f"Filas: {summary['rows']} | "
            f"Columnas: {summary['columns']} | "
            f"Celdas llenas: {summary['filled_cells']}/{summary['total_cells']} ({summary['fill_percentage']}%) | "
            f"Tamaño estimado: {summary['estimated_size_kb']} KB"
        )

        self.summary_label.setText(summary_text)

    def update_suggested_filename(self):
        """Actualiza el nombre de archivo sugerido según formato."""
        format_id = self.format_group.checkedId()

        if format_id == 1:  # CSV
            format_ext = "csv"
        elif format_id == 2:  # TSV
            format_ext = "tsv"
        elif format_id in [3, 4]:  # JSON
            format_ext = "json"
        else:
            format_ext = "csv"

        suggested = TableExporter.get_suggested_filename(self.table_name, format_ext)
        self.filename_input.setText(suggested)

        # Actualizar ruta completa si ya hay ubicación
        if self.output_path:
            output_dir = Path(self.output_path).parent
            new_path = output_dir / suggested
            self.output_path = str(new_path)
            self.path_label.setText(self.output_path)

    def browse_location(self):
        """Abre diálogo para seleccionar ubicación de archivo."""
        format_id = self.format_group.checkedId()

        if format_id == 1:  # CSV
            file_filter = "CSV Files (*.csv);;All Files (*.*)"
            default_ext = ".csv"
        elif format_id == 2:  # TSV
            file_filter = "TSV Files (*.tsv);;All Files (*.*)"
            default_ext = ".tsv"
        elif format_id in [3, 4]:  # JSON
            file_filter = "JSON Files (*.json);;All Files (*.*)"
            default_ext = ".json"
        else:
            file_filter = "All Files (*.*)"
            default_ext = ""

        suggested_name = self.filename_input.text()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Tabla Como",
            suggested_name,
            file_filter
        )

        if file_path:
            # Asegurar extensión correcta
            if not file_path.endswith(default_ext) and default_ext:
                file_path += default_ext

            self.output_path = file_path
            self.path_label.setText(file_path)

            logger.info(f"Export location selected: {file_path}")

    def export_table(self):
        """Ejecuta la exportación."""
        # Validar que se haya seleccionado ubicación
        if not self.output_path:
            QMessageBox.warning(
                self,
                "Ubicación Requerida",
                "Por favor selecciona una ubicación para guardar el archivo."
            )
            return

        # Validar datos
        is_valid, error_msg = TableExporter.validate_export_data(
            self.table_data,
            self.column_names
        )

        if not is_valid:
            QMessageBox.critical(
                self,
                "Datos Inválidos",
                f"No se puede exportar:\n{error_msg}"
            )
            return

        # Obtener opciones
        include_headers = self.include_headers_check.isChecked()
        include_metadata = self.include_metadata_check.isChecked()
        pretty_json = self.pretty_json_check.isChecked()

        format_id = self.format_group.checkedId()

        try:
            success = False

            if format_id == 1:  # CSV
                success = TableExporter.export_to_csv(
                    self.table_data,
                    self.column_names,
                    self.output_path,
                    include_headers=include_headers
                )

            elif format_id == 2:  # TSV
                success = TableExporter.export_to_tsv(
                    self.table_data,
                    self.column_names,
                    self.output_path,
                    include_headers=include_headers
                )

            elif format_id == 3:  # JSON (Matriz)
                success = TableExporter.export_to_json(
                    self.table_name,
                    self.table_data,
                    self.column_names,
                    self.output_path,
                    include_metadata=include_metadata,
                    pretty=pretty_json
                )

            elif format_id == 4:  # JSON (Records)
                success = TableExporter.export_to_json_records(
                    self.table_name,
                    self.table_data,
                    self.column_names,
                    self.output_path,
                    include_metadata=include_metadata,
                    pretty=pretty_json
                )

            if success:
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"Tabla exportada exitosamente a:\n{self.output_path}"
                )

                # Emitir señal
                self.export_completed.emit(self.output_path)

                # Cerrar diálogo
                self.accept()

            else:
                QMessageBox.critical(
                    self,
                    "Error de Exportación",
                    "No se pudo exportar la tabla. Revisa los logs para más detalles."
                )

        except Exception as e:
            logger.error(f"Error exporting table: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al exportar tabla:\n{str(e)}"
            )
