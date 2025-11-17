"""
Command Output Dialog
Dialog para mostrar el resultado de la ejecución de comandos
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyperclip

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class CommandOutputDialog(QDialog):
    """Dialog para mostrar el output de comandos ejecutados"""

    def __init__(self, command: str, output: str, error: str = None, return_code: int = 0, parent=None):
        super().__init__(parent)
        self.command = command
        self.output = output
        self.error = error
        self.return_code = return_code
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Resultado de Ejecución")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header con icono de éxito/error
        header_layout = QHBoxLayout()

        if self.return_code == 0 and not self.error:
            status_icon = QLabel("✅")
            status_text = QLabel("Comando ejecutado exitosamente")
            status_text.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            status_icon = QLabel("❌")
            status_text = QLabel("Error al ejecutar comando")
            status_text.setStyleSheet("color: #ff0000; font-weight: bold;")

        status_icon.setStyleSheet("font-size: 20pt;")
        status_text_font = QFont()
        status_text_font.setPointSize(12)
        status_text.setFont(status_text_font)

        header_layout.addWidget(status_icon)
        header_layout.addWidget(status_text)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Comando ejecutado
        command_label = QLabel("Comando:")
        command_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        main_layout.addWidget(command_label)

        command_text = QLabel(self.command)
        command_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        """)
        command_text.setWordWrap(True)
        command_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(command_text)

        # Output
        output_label = QLabel("Salida:")
        output_label.setStyleSheet("font-weight: bold; color: #cccccc;")
        main_layout.addWidget(output_label)

        # Text edit para el output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """)

        # Combinar output y error
        full_output = ""
        if self.output:
            full_output += self.output
        if self.error:
            if full_output:
                full_output += "\n\n--- STDERR ---\n"
            full_output += self.error

        if not full_output:
            full_output = "(Sin salida)"

        self.output_text.setPlainText(full_output)
        main_layout.addWidget(self.output_text)

        # Return code
        return_code_label = QLabel(f"Código de salida: {self.return_code}")
        if self.return_code == 0:
            return_code_label.setStyleSheet("color: #00ff00; font-size: 9pt;")
        else:
            return_code_label.setStyleSheet("color: #ff0000; font-size: 9pt;")
        main_layout.addWidget(return_code_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Copy output button
        copy_btn = QPushButton("📋 Copiar Salida")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self.copy_output)
        buttons_layout.addWidget(copy_btn)

        buttons_layout.addStretch()

        # Close button
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e42;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4e4e52;
            }
            QPushButton:pressed {
                background-color: #2e2e32;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

        # Dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QLabel {
                color: #cccccc;
            }
        """)

    def copy_output(self):
        """Copiar output al portapapeles"""
        try:
            full_output = self.output_text.toPlainText()
            pyperclip.copy(full_output)

            # Visual feedback
            original_text = self.sender().text()
            self.sender().setText("✅ Copiado!")
            self.sender().setStyleSheet("""
                QPushButton {
                    background-color: #00ff00;
                    color: #000000;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
            """)

            # Restaurar después de 1 segundo
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.reset_copy_button(original_text))

        except Exception as e:
            print(f"Error copying output: {e}")

    def reset_copy_button(self, original_text):
        """Restaurar botón de copiar"""
        copy_btn = self.findChild(QPushButton, "")
        for btn in self.findChildren(QPushButton):
            if "Copiado" in btn.text():
                btn.setText(original_text)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0e639c;
                        color: #ffffff;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1177bb;
                    }
                    QPushButton:pressed {
                        background-color: #0d5a8f;
                    }
                """)
                break
