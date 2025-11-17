"""
Step Item Widget
Widget para representar un paso individual en una lista
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class StepItemWidget(QWidget):
    """
    Widget para un paso individual de una lista

    Contiene:
    - Número de paso
    - Campo de label/nombre del paso
    - Selector de tipo (TEXT, CODE, URL, PATH)
    - Campo de contenido (textarea)
    - Botones de acción (eliminar, mover arriba, mover abajo)
    """

    # Señales
    delete_requested = pyqtSignal()  # Emitida cuando se solicita eliminar este paso
    move_up_requested = pyqtSignal()  # Emitida cuando se solicita mover arriba
    move_down_requested = pyqtSignal()  # Emitida cuando se solicita mover abajo
    data_changed = pyqtSignal()  # Emitida cuando cambia cualquier dato

    def __init__(self, step_number: int = 1, parent=None):
        """
        Inicializa el widget de paso

        Args:
            step_number: Número del paso (1, 2, 3...)
            parent: Widget padre
        """
        super().__init__(parent)
        self.step_number = step_number

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Configura la interfaz del widget"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # === HEADER: Número + Label + Tipo + Botones ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Número de paso
        self.number_label = QLabel(f"{self.step_number}.")
        self.number_label.setFixedWidth(30)
        number_font = QFont()
        number_font.setBold(True)
        number_font.setPointSize(12)
        self.number_label.setFont(number_font)
        header_layout.addWidget(self.number_label)

        # Label del paso
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText(f"Nombre del paso {self.step_number}")
        self.label_input.textChanged.connect(self.data_changed.emit)
        header_layout.addWidget(self.label_input, stretch=2)

        # Selector de tipo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["TEXT", "CODE", "URL", "PATH"])
        self.type_combo.setCurrentText("TEXT")  # Por defecto TEXT
        self.type_combo.setFixedWidth(80)
        self.type_combo.currentTextChanged.connect(self.data_changed.emit)
        header_layout.addWidget(self.type_combo)

        # Botón mover arriba
        self.up_button = QPushButton("↑")
        self.up_button.setFixedSize(30, 30)
        self.up_button.setToolTip("Mover arriba")
        self.up_button.clicked.connect(self.move_up_requested.emit)
        header_layout.addWidget(self.up_button)

        # Botón mover abajo
        self.down_button = QPushButton("↓")
        self.down_button.setFixedSize(30, 30)
        self.down_button.setToolTip("Mover abajo")
        self.down_button.clicked.connect(self.move_down_requested.emit)
        header_layout.addWidget(self.down_button)

        # Botón eliminar
        self.delete_button = QPushButton("🗑")
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setToolTip("Eliminar paso")
        self.delete_button.clicked.connect(self.delete_requested.emit)
        header_layout.addWidget(self.delete_button)

        main_layout.addLayout(header_layout)

        # === CONTENT: Área de texto para contenido ===
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Contenido del paso (comando, texto, URL, ruta...)")
        self.content_input.setMaximumHeight(80)
        self.content_input.setMinimumHeight(60)
        self.content_input.textChanged.connect(self.data_changed.emit)
        main_layout.addWidget(self.content_input)

    def apply_styles(self):
        """Aplica estilos al widget"""
        # Estilo del contenedor principal
        self.setStyleSheet("""
            StepItemWidget {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
        """)

        # Estilo del label de número
        self.number_label.setStyleSheet("""
            QLabel {
                color: #4a9eff;
                font-weight: bold;
            }
        """)

        # Estilo de inputs
        input_style = """
            QLineEdit, QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #4a9eff;
            }
        """
        self.label_input.setStyleSheet(input_style)
        self.content_input.setStyleSheet(input_style)

        # Estilo del combo
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }
            QComboBox:hover {
                border: 1px solid #4a9eff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #e0e0e0;
                selection-background-color: #4a9eff;
            }
        """)

        # Estilo de botones
        button_style = """
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """
        self.up_button.setStyleSheet(button_style)
        self.down_button.setStyleSheet(button_style)

        # Botón eliminar con color rojo
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #3a2a2a;
                border: 1px solid #5a3a3a;
                border-radius: 3px;
                color: #ff6666;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a3a3a;
                border: 1px solid #7a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a1a1a;
            }
        """)

    def set_step_number(self, number: int):
        """
        Actualiza el número del paso

        Args:
            number: Nuevo número de paso
        """
        self.step_number = number
        self.number_label.setText(f"{number}.")
        self.label_input.setPlaceholderText(f"Nombre del paso {number}")

    def get_step_data(self) -> dict:
        """
        Obtiene los datos del paso

        Returns:
            Dict con label, content y type
        """
        return {
            'label': self.label_input.text().strip(),
            'content': self.content_input.toPlainText().strip(),
            'type': self.type_combo.currentText()
        }

    def set_step_data(self, label: str = "", content: str = "", step_type: str = "TEXT"):
        """
        Establece los datos del paso

        Args:
            label: Etiqueta del paso
            content: Contenido del paso
            step_type: Tipo del paso (TEXT, CODE, URL, PATH)
        """
        self.label_input.setText(label)
        self.content_input.setPlainText(content)
        self.type_combo.setCurrentText(step_type)

    def is_empty(self) -> bool:
        """
        Verifica si el paso está vacío

        Returns:
            True si tanto label como content están vacíos
        """
        return not self.label_input.text().strip() and not self.content_input.toPlainText().strip()

    def has_label(self) -> bool:
        """
        Verifica si el paso tiene label

        Returns:
            True si tiene label
        """
        return bool(self.label_input.text().strip())

    def enable_move_buttons(self, enable_up: bool, enable_down: bool):
        """
        Habilita/deshabilita botones de movimiento

        Args:
            enable_up: Habilitar botón mover arriba
            enable_down: Habilitar botón mover abajo
        """
        self.up_button.setEnabled(enable_up)
        self.down_button.setEnabled(enable_down)
