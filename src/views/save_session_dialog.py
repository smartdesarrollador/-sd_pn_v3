"""
Save Session Dialog - Dialog simple para guardar una nueva sesión
Author: Widget Sidebar Team
Date: 2025-11-03
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from datetime import datetime

logger = logging.getLogger(__name__)


class SaveSessionDialog(QDialog):
    """Dialog simple para guardar una sesión con nombre."""

    def __init__(self, parent=None):
        """
        Inicializa el dialog.

        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.session_name = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Configura la interfaz del dialog."""
        self.setWindowTitle("Guardar Sesión")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(400, 200)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("💾 Guardar Sesión Actual")
        header_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(header_label)

        # Descripción
        desc_label = QLabel("Ingresa un nombre para identificar esta sesión:")
        desc_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(desc_label)

        # Input de nombre
        self.name_input = QLineEdit()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.name_input.setPlaceholderText(f"Sesión {timestamp}")
        self.name_input.setText(f"Sesión {timestamp}")
        self.name_input.selectAll()
        main_layout.addWidget(self.name_input)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Guardar")
        self.save_btn.setFixedWidth(100)
        self.save_btn.clicked.connect(self._save_session)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Hacer que Enter guarde
        self.name_input.returnPressed.connect(self._save_session)

    def _apply_styles(self):
        """Aplica estilos al dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                border: 2px solid #00d4ff;
                border-radius: 10px;
            }

            QLabel {
                color: #00d4ff;
                font-size: 13px;
            }

            QLineEdit {
                background-color: #16213e;
                color: #00d4ff;
                border: 1px solid #0f3460;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 2px solid #00d4ff;
            }

            QPushButton {
                background-color: #0f3460;
                color: #00d4ff;
                border: 1px solid #00d4ff;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #16213e;
                border: 2px solid #00d4ff;
            }

            QPushButton:pressed {
                background-color: #00d4ff;
                color: #1a1a2e;
            }
        """)

    def _save_session(self):
        """Guarda el nombre de la sesión y cierra el dialog."""
        name = self.name_input.text().strip()

        if not name:
            # Si está vacío, usar el placeholder
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            name = f"Sesión {timestamp}"

        self.session_name = name
        self.accept()

    def get_session_name(self) -> str:
        """
        Obtiene el nombre de sesión ingresado.

        Returns:
            Nombre de la sesión
        """
        return self.session_name
