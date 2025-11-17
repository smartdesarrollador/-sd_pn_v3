"""
AI Table JSON Step - Paso 3: Importación y validación de JSON

Este step:
- Permite pegar JSON generado por IA
- Valida estructura y coherencia
- Parsea datos para el siguiente paso
- Muestra preview de dimensiones
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ai_table_manager import AITableManager
from models.ai_table_data import AITableData

logger = logging.getLogger(__name__)


class AITableJSONStep(QWidget):
    """Step 3: Importación de JSON de IA."""

    def __init__(self, ai_manager: AITableManager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.json_text = None
        self.parsed_data = None
        self.is_validated = False
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("📥 Importación de JSON")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Instrucciones
        instructions = QLabel(
            "Pega aquí el JSON generado por la IA y presiona 'Validar JSON'"
        )
        instructions.setStyleSheet("color: #aaaaaa; font-size: 10pt; padding: 0 10px;")
        layout.addWidget(instructions)

        # Editor JSON
        self.json_editor = QTextEdit()
        self.json_editor.setPlaceholderText(
            '{\n'
            '  "table_config": {\n'
            '    "table_name": "NOMBRE_TABLA",\n'
            '    "category_id": 1,\n'
            '    ...\n'
            '  },\n'
            '  "table_structure": { ... },\n'
            '  "table_data": [ ... ]\n'
            '}'
        )
        self.json_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 12px;
                color: #cccccc;
                font-family: monospace;
                font-size: 9pt;
            }
            QTextEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        self.json_editor.textChanged.connect(self.on_json_changed)
        layout.addWidget(self.json_editor, 1)

        # Botón validar
        validate_layout = QHBoxLayout()

        self.validate_button = QPushButton("✓ Validar JSON")
        self.validate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.validate_button.clicked.connect(self.validate_json)
        validate_layout.addWidget(self.validate_button)

        validate_layout.addStretch()

        # Indicador de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 10pt;")
        validate_layout.addWidget(self.status_label)

        layout.addLayout(validate_layout)

        # Preview de dimensiones
        self.dimensions_label = QLabel("")
        self.dimensions_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 10px;
                color: #00d4ff;
                font-size: 10pt;
            }
        """)
        self.dimensions_label.setVisible(False)
        layout.addWidget(self.dimensions_label)

        # Área de errores
        self.errors_display = QTextEdit()
        self.errors_display.setReadOnly(True)
        self.errors_display.setMaximumHeight(120)
        self.errors_display.setStyleSheet("""
            QTextEdit {
                background-color: #3d2020;
                border: 1px solid #dd4444;
                border-radius: 4px;
                padding: 10px;
                color: #ffaaaa;
                font-size: 9pt;
            }
        """)
        self.errors_display.setVisible(False)
        layout.addWidget(self.errors_display)

    def on_json_changed(self):
        """Callback cuando cambia el JSON."""
        self.is_validated = False
        self.status_label.setText("")
        self.dimensions_label.setVisible(False)
        self.errors_display.setVisible(False)

    def validate_json(self):
        """Valida el JSON pegado."""
        json_text = self.json_editor.toPlainText().strip()

        if not json_text:
            QMessageBox.warning(
                self,
                "JSON Vacío",
                "Por favor pega el JSON generado por la IA."
            )
            return

        # Validar con AITableManager
        validation_result = self.ai_manager.validate_json(json_text)

        if validation_result.is_valid:
            # Parsear datos
            self.json_text = json_text
            self.parsed_data, errors = self.ai_manager.parse_json(json_text)

            if errors:
                self.show_errors(errors)
                self.is_validated = False
            else:
                self.show_success(validation_result)
                self.is_validated = True
        else:
            self.show_errors(validation_result.errors)
            self.is_validated = False

    def show_success(self, result):
        """Muestra resultado exitoso."""
        self.status_label.setText("✓ JSON válido")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 10pt; font-weight: bold;")

        # Mostrar dimensiones
        if result.dimensions:
            dim_text = (
                f"📊 Tabla detectada: "
                f"{result.dimensions['rows']} filas × {result.dimensions['cols']} columnas"
            )
            self.dimensions_label.setText(dim_text)
            self.dimensions_label.setVisible(True)

        # Mostrar warnings si hay
        if result.warnings:
            warnings_text = "Advertencias:\n" + "\n".join(f"• {w}" for w in result.warnings)
            self.errors_display.setPlainText(warnings_text)
            self.errors_display.setStyleSheet("""
                QTextEdit {
                    background-color: #3d3420;
                    border: 1px solid #ddaa44;
                    border-radius: 4px;
                    padding: 10px;
                    color: #ffddaa;
                    font-size: 9pt;
                }
            """)
            self.errors_display.setVisible(True)

        logger.info("JSON validated successfully")

    def show_errors(self, errors):
        """Muestra errores de validación."""
        self.status_label.setText("✗ JSON inválido")
        self.status_label.setStyleSheet("color: #dd4444; font-size: 10pt; font-weight: bold;")

        errors_text = "Errores encontrados:\n\n" + "\n".join(f"• {e}" for e in errors)
        self.errors_display.setPlainText(errors_text)
        self.errors_display.setStyleSheet("""
            QTextEdit {
                background-color: #3d2020;
                border: 1px solid #dd4444;
                border-radius: 4px;
                padding: 10px;
                color: #ffaaaa;
                font-size: 9pt;
            }
        """)
        self.errors_display.setVisible(True)
        self.dimensions_label.setVisible(False)

        logger.warning(f"JSON validation failed: {len(errors)} errors")

    def get_json_text(self) -> str:
        """Retorna el JSON validado."""
        return self.json_text

    def get_parsed_data(self) -> AITableData:
        """Retorna los datos parseados."""
        return self.parsed_data

    def is_valid(self) -> bool:
        """Retorna si el JSON está validado."""
        return self.is_validated and self.parsed_data is not None

    def get_validation_message(self) -> str:
        """Mensaje de validación."""
        if not self.json_editor.toPlainText().strip():
            return "Por favor pega el JSON generado por la IA."
        if not self.is_validated:
            return "Por favor valida el JSON antes de continuar."
        return "JSON válido."
