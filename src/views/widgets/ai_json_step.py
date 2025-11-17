"""AI Bulk JSON Step - Paso 3: Importación de JSON generado por IA"""
import sys
from pathlib import Path
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.ai_bulk_manager import AIBulkItemManager
from models.bulk_item_data import ValidationResult
from views.widgets.json_editor import JSONEditor

logger = logging.getLogger(__name__)

class JSONStep(QWidget):
    """Step 3: Importación y validación de JSON"""

    def __init__(self, manager: AIBulkItemManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.validation_result = None
        self.json_text = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("📋 Importar JSON")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Instrucciones
        instructions = QLabel(
            "<b>Pega aquí el JSON que generó la IA:</b><br>"
            "La IA debió generar un JSON con la estructura especificada en el prompt. "
            "Pégalo completo en el editor de abajo y haz click en <b>Validar JSON</b>."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #888888; padding: 10px; font-size: 11pt;")
        layout.addWidget(instructions)

        # Editor JSON
        self.json_editor = JSONEditor()
        self.json_editor.setPlaceholderText(
            '{\n  "category_id": 1,\n  "defaults": {...},\n  "items": [...]\n}'
        )
        layout.addWidget(self.json_editor)

        # Botón validar + Estado
        btn_layout = QHBoxLayout()
        self.validate_button = QPushButton("🔍 Validar JSON")
        self.validate_button.setFixedHeight(40)
        self.validate_button.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00b8e6; }
            QPushButton:pressed { background-color: #0099cc; }
        """)
        self.validate_button.clicked.connect(self.validate_json)
        btn_layout.addWidget(self.validate_button)

        self.status_label = QLabel("⏳ Pendiente de validación")
        self.status_label.setStyleSheet("color: #888888; font-size: 11pt; padding: 8px;")
        btn_layout.addWidget(self.status_label)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Área de errores/warnings
        self.errors_label = QLabel()
        self.errors_label.setWordWrap(True)
        self.errors_label.setStyleSheet("""
            QLabel {
                background-color: #3d1e1e;
                color: #ff6b6b;
                border-left: 4px solid #ff4444;
                border-radius: 3px;
                padding: 12px;
                font-size: 10pt;
            }
        """)
        self.errors_label.setVisible(False)
        layout.addWidget(self.errors_label)

    def validate_json(self):
        """Valida el JSON ingresado"""
        self.json_text = self.json_editor.toPlainText().strip()

        if not self.json_text:
            QMessageBox.warning(self, "Advertencia", "Por favor pega el JSON primero.")
            return

        try:
            self.validation_result = self.manager.validate_json(self.json_text)

            if self.validation_result.is_valid:
                self.status_label.setText(f"✓ JSON válido - {self.validation_result.items_count} items")
                self.status_label.setStyleSheet("color: #00ff88; font-size: 11pt; font-weight: bold; padding: 8px;")
                self.errors_label.setVisible(False)
                logger.info(f"JSON valid: {self.validation_result.items_count} items")
            else:
                self.status_label.setText("✗ JSON inválido")
                self.status_label.setStyleSheet("color: #ff4444; font-size: 11pt; font-weight: bold; padding: 8px;")
                error_text = "<b>Errores encontrados:</b><br>" + "<br>".join(f"• {e}" for e in self.validation_result.errors[:5])
                self.errors_label.setText(error_text)
                self.errors_label.setVisible(True)
                logger.warning(f"JSON invalid: {len(self.validation_result.errors)} errors")

        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al validar JSON:\n{str(e)}")

    def is_valid(self) -> bool:
        """Valida que se puede avanzar"""
        return self.validation_result is not None and self.validation_result.is_valid

    def get_json_text(self) -> str:
        """Retorna el JSON validado"""
        return self.json_text
