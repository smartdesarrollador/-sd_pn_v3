"""
AI Table Prompt Step - Paso 2: Generación y copia de prompt

Este step:
- Genera prompt personalizado basado en config del paso 1
- Muestra el prompt con formato
- Permite copiar al portapapeles
- Muestra instrucciones para el usuario
"""
import sys
from pathlib import Path
import logging
import pyperclip

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.ai_table_data import AITablePromptConfig
from utils.ai_table_prompt_templates import AITablePromptTemplate

logger = logging.getLogger(__name__)


class AITablePromptStep(QWidget):
    """Step 2: Generación de prompt para IA."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt_config = None
        self.generated_prompt = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Título
        title = QLabel("📝 Prompt Generado")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Instrucciones
        instructions = QLabel(
            "1. Copia el prompt usando el botón de abajo\n"
            "2. Pégalo en ChatGPT, Claude u otra IA\n"
            "3. Copia el JSON que te genere la IA\n"
            "4. En el siguiente paso, pega el JSON"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 2px solid #007acc;
                border-radius: 5px;
                padding: 15px;
                color: #cccccc;
                font-size: 10pt;
            }
        """)
        layout.addWidget(instructions)

        # Prompt display
        self.prompt_display = QTextEdit()
        self.prompt_display.setReadOnly(True)
        self.prompt_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 12px;
                color: #cccccc;
                font-family: monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.prompt_display, 1)

        # Botón copiar
        copy_button = QPushButton("📋 Copiar Prompt al Portapapeles")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        copy_button.clicked.connect(self.copy_prompt)
        layout.addWidget(copy_button)

    def set_config(self, config: AITablePromptConfig):
        """
        Establece la config y genera el prompt.

        Args:
            config: Configuración del prompt
        """
        self.prompt_config = config

        # Generar prompt
        config_dict = {
            'table_name': config.table_name,
            'category_id': config.category_id,
            'category_name': config.category_name,
            'user_context': config.user_context,
            'expected_rows': config.expected_rows,
            'expected_cols': config.expected_cols,
            'columns_config': config.columns_config,
            'tags': config.tags,
            'auto_detect_sensitive': config.auto_detect_sensitive,
            'auto_detect_urls': config.auto_detect_urls
        }

        self.generated_prompt = AITablePromptTemplate.generate(config_dict)
        self.prompt_display.setPlainText(self.generated_prompt)

        logger.info(f"Prompt generated: {len(self.generated_prompt)} characters")

    def copy_prompt(self):
        """Copia el prompt al portapapeles."""
        if self.generated_prompt:
            pyperclip.copy(self.generated_prompt)
            QMessageBox.information(
                self,
                "Copiado",
                "Prompt copiado al portapapeles.\n\n"
                "Ahora pégalo en ChatGPT, Claude u otra IA."
            )
            logger.info("Prompt copied to clipboard")

    def get_prompt(self) -> str:
        """Retorna el prompt generado."""
        return self.generated_prompt

    def is_valid(self) -> bool:
        """Siempre válido (prompt ya generado)."""
        return self.generated_prompt is not None

    def get_validation_message(self) -> str:
        """Mensaje de validación."""
        return "Prompt generado correctamente."
