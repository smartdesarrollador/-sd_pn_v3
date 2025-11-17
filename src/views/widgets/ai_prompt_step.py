"""
AI Bulk Prompt Step - Paso 2: Generación de prompt para IA

Este step muestra el prompt generado que el usuario debe copiar y
dar a una IA (ChatGPT, Claude, etc.) para generar el JSON.
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyperclip

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ai_bulk_manager import AIBulkItemManager
from models.bulk_item_data import BulkImportConfig

logger = logging.getLogger(__name__)


class PromptStep(QWidget):
    """
    Step 2: Generación y copia de prompt para IA.

    Muestra el prompt personalizado generado según la configuración
    del Step 1. Permite copiarlo al portapapeles.
    """

    def __init__(self, manager: AIBulkItemManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.config = None
        self.prompt_text = ""

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del step."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("📝 Prompt para la IA")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Instrucciones
        instructions = QLabel(
            "<b>Instrucciones:</b><br>"
            "1. Copia el prompt completo (botón abajo)<br>"
            "2. Pégalo en ChatGPT, Claude, Gemini o cualquier IA<br>"
            "3. La IA generará un JSON con los items<br>"
            "4. Copia el JSON que te devuelva la IA<br>"
            "5. Vuelve aquí y pégalo en el siguiente paso"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #1e3a4d;
                color: #ffffff;
                border-left: 4px solid #00d4ff;
                border-radius: 3px;
                padding: 15px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(instructions)

        # TextEdit con el prompt (readonly)
        self.prompt_display = QTextEdit()
        self.prompt_display.setReadOnly(True)
        self.prompt_display.setPlaceholderText("El prompt se generará automáticamente...")
        self.prompt_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 15px;
                font-size: 10pt;
                font-family: Consolas, monospace;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.prompt_display)

        # Botón copiar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.copy_button = QPushButton("📋 Copiar Prompt al Portapapeles")
        self.copy_button.setFixedHeight(45)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b8e6;
            }
            QPushButton:pressed {
                background-color: #0099cc;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.copy_button.clicked.connect(self.copy_prompt)
        self.copy_button.setEnabled(False)
        btn_layout.addWidget(self.copy_button)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Contador de caracteres
        self.char_count_label = QLabel("Prompt: 0 caracteres")
        self.char_count_label.setStyleSheet("color: #888888; font-size: 9pt;")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.char_count_label)

    def set_config(self, config: BulkImportConfig):
        """
        Establece la configuración y genera el prompt.

        Args:
            config: Configuración del Step 1
        """
        self.config = config

        try:
            # Generar prompt
            self.prompt_text = self.manager.generate_prompt(config)

            # Mostrar en display
            self.prompt_display.setPlainText(self.prompt_text)

            # Habilitar botón copiar
            self.copy_button.setEnabled(True)

            # Actualizar contador
            char_count = len(self.prompt_text)
            self.char_count_label.setText(f"Prompt: {char_count:,} caracteres")

            logger.info(f"Prompt generated: {char_count} characters")

        except Exception as e:
            logger.error(f"Error generating prompt: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al generar el prompt:\n{str(e)}"
            )

    def copy_prompt(self):
        """Copia el prompt al portapapeles."""
        try:
            pyperclip.copy(self.prompt_text)

            # Feedback visual
            original_text = self.copy_button.text()
            self.copy_button.setText("✓ ¡Copiado!")
            self.copy_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff88;
                    color: #000000;
                    border: none;
                    border-radius: 5px;
                    padding: 12px 24px;
                    font-size: 12pt;
                    font-weight: bold;
                }
            """)

            # Restaurar después de 2 segundos
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.restore_copy_button(original_text))

            logger.info("Prompt copied to clipboard")

        except Exception as e:
            logger.error(f"Error copying prompt: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"Error al copiar al portapapeles:\n{str(e)}"
            )

    def restore_copy_button(self, original_text: str):
        """Restaura el botón copiar a su estado original."""
        self.copy_button.setText(original_text)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b8e6;
            }
            QPushButton:pressed {
                background-color: #0099cc;
            }
        """)

    def is_valid(self) -> bool:
        """Valida que el step se puede avanzar."""
        # Siempre válido si hay prompt generado
        return bool(self.prompt_text)
