"""
Password Verification Dialog
Simple dialog to verify user password for sensitive operations
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.core.auth_manager import AuthManager


class PasswordVerifyDialog(QDialog):
    """Simple dialog to verify user password"""

    def __init__(self, title="Verificación de Contraseña", message="Ingresa tu contraseña para continuar:", parent=None):
        super().__init__(parent)
        self.auth_manager = AuthManager()
        self.title_text = title
        self.message_text = message
        self.password_verified = False
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle(self.title_text)
        self.setFixedSize(400, 220)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Title with icon
        title = QLabel(f"🔐 {self.title_text}")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Message
        message = QLabel(self.message_text)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        main_layout.addWidget(message)

        main_layout.addSpacing(10)

        # Password input
        password_label = QLabel("Contraseña:")
        main_layout.addWidget(password_label)

        # Password container with show/hide button
        password_container = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Ingresa tu contraseña...")
        self.password_input.returnPressed.connect(self.verify_password)
        password_container.addWidget(self.password_input)

        # Show/hide button
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(35, 35)
        self.show_password_btn.setToolTip("Mostrar/Ocultar contraseña")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_container.addWidget(self.show_password_btn)

        main_layout.addLayout(password_container)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #cc0000; font-weight: bold;")
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        verify_btn = QPushButton("Verificar")
        verify_btn.setFixedSize(100, 35)
        verify_btn.clicked.connect(self.verify_password)
        button_layout.addWidget(verify_btn)

        main_layout.addLayout(button_layout)

        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QCheckBox {
                color: #cccccc;
                spacing: 8px;
            }
        """)

        # Focus on password input
        self.password_input.setFocus()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")

    def verify_password(self):
        """Verify the entered password"""
        password = self.password_input.text()

        if not password:
            self.show_error("Por favor ingresa tu contraseña")
            return

        # Verify password with AuthManager
        if self.auth_manager.verify_password(password):
            self.password_verified = True
            self.accept()
        else:
            self.show_error("Contraseña incorrecta")
            self.password_input.clear()
            self.password_input.setFocus()

            # Shake animation for error feedback
            self.shake_dialog()

    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(message)
        self.error_label.show()

    def shake_dialog(self):
        """Shake dialog for error feedback"""
        from PyQt6.QtCore import QPropertyAnimation, QRect

        # Get current geometry
        current_geom = self.geometry()

        # Create animation
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(500)
        animation.setLoopCount(1)

        # Shake left and right
        animation.setKeyValueAt(0, current_geom)
        animation.setKeyValueAt(0.1, QRect(current_geom.x() - 10, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(0.2, QRect(current_geom.x() + 10, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(0.3, QRect(current_geom.x() - 10, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(0.4, QRect(current_geom.x() + 10, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(0.5, QRect(current_geom.x() - 5, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(0.6, QRect(current_geom.x() + 5, current_geom.y(), current_geom.width(), current_geom.height()))
        animation.setKeyValueAt(1, current_geom)

        animation.start()

    @staticmethod
    def verify(title="Verificación de Contraseña", message="Ingresa tu contraseña para continuar:", parent=None):
        """
        Static method to show verification dialog and return result

        Returns:
            bool: True if password was verified, False if cancelled
        """
        dialog = PasswordVerifyDialog(title, message, parent)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted and dialog.password_verified
