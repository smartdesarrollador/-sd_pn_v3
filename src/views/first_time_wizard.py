"""
First Time Wizard
Dialog for initial password setup on first run
"""
import sys
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.auth_manager import AuthManager


class FirstTimeWizard(QDialog):
    """Wizard for creating password on first run"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = AuthManager()
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Bienvenido a Widget Sidebar")
        self.setFixedSize(500, 450)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Welcome title
        title = QLabel("🎉 Bienvenido a Widget Sidebar")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Primera vez que ejecutas la aplicación.\nPor favor, crea una contraseña maestra.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(20)

        # Password input
        password_label = QLabel("Nueva contraseña:")
        main_layout.addWidget(password_label)

        # Password input with show/hide button
        password_container = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Ingresa tu contraseña...")
        self.password_input.textChanged.connect(self.on_password_changed)
        password_container.addWidget(self.password_input)

        # Show/hide button
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(35, 35)
        self.show_password_btn.setToolTip("Mostrar/Ocultar contraseña")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_container.addWidget(self.show_password_btn)

        main_layout.addLayout(password_container)

        # Validation checks
        self.validation_layout = QVBoxLayout()
        self.validation_layout.setSpacing(5)

        self.check_length = QLabel("● Mínimo 8 caracteres")
        self.check_uppercase = QLabel("● Al menos 1 mayúscula")
        self.check_lowercase = QLabel("● Al menos 1 minúscula")
        self.check_number = QLabel("● Al menos 1 número")
        self.check_special = QLabel("● Al menos 1 carácter especial")

        for check in [self.check_length, self.check_uppercase, self.check_lowercase,
                      self.check_number, self.check_special]:
            check.setStyleSheet("color: #888888;")
            self.validation_layout.addWidget(check)

        main_layout.addLayout(self.validation_layout)

        # Strength indicator
        self.strength_label = QLabel("Fortaleza: ")
        main_layout.addWidget(self.strength_label)

        main_layout.addSpacing(10)

        # Confirm password
        confirm_label = QLabel("Confirmar contraseña:")
        main_layout.addWidget(confirm_label)

        confirm_container = QHBoxLayout()
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirma tu contraseña...")
        self.confirm_input.textChanged.connect(self.on_confirm_changed)
        confirm_container.addWidget(self.confirm_input)

        # Show/hide button for confirm
        self.show_confirm_btn = QPushButton("👁")
        self.show_confirm_btn.setFixedSize(35, 35)
        self.show_confirm_btn.setToolTip("Mostrar/Ocultar contraseña")
        self.show_confirm_btn.clicked.connect(self.toggle_confirm_visibility)
        confirm_container.addWidget(self.show_confirm_btn)

        main_layout.addLayout(confirm_container)

        # Match indicator
        self.match_label = QLabel("")
        main_layout.addWidget(self.match_label)

        main_layout.addSpacing(10)

        # Warning
        warning = QLabel("💡 No olvides tu contraseña, no hay forma de recuperarla.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #cc7a00; font-style: italic;")
        main_layout.addWidget(warning)

        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.create_btn = QPushButton("Crear")
        self.create_btn.setFixedSize(100, 35)
        self.create_btn.setEnabled(False)
        self.create_btn.clicked.connect(self.create_password)
        button_layout.addWidget(self.create_btn)

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
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #888888;
            }
        """)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")

    def toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        if self.confirm_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_confirm_btn.setText("🙈")
        else:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_confirm_btn.setText("👁")

    def validate_password(self, password: str) -> dict:
        """
        Validate password strength

        Returns:
            dict with validation results
        """
        return {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'number': bool(re.search(r'[0-9]', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password))
        }

    def on_password_changed(self):
        """Handle password input change"""
        password = self.password_input.text()
        validation = self.validate_password(password)

        # Update validation checks
        self.update_check(self.check_length, validation['length'])
        self.update_check(self.check_uppercase, validation['uppercase'])
        self.update_check(self.check_lowercase, validation['lowercase'])
        self.update_check(self.check_number, validation['number'])
        self.update_check(self.check_special, validation['special'])

        # Calculate strength
        score = sum(validation.values())
        if score == 0:
            strength_text = ""
            strength_color = "#888888"
        elif score <= 2:
            strength_text = "Fortaleza: Débil"
            strength_color = "#cc0000"
        elif score <= 4:
            strength_text = "Fortaleza: Media"
            strength_color = "#cc7a00"
        else:
            strength_text = "Fortaleza: Fuerte"
            strength_color = "#00cc00"

        self.strength_label.setText(strength_text)
        self.strength_label.setStyleSheet(f"color: {strength_color}; font-weight: bold;")

        # Update confirm validation
        self.on_confirm_changed()

    def update_check(self, label: QLabel, is_valid: bool):
        """Update validation check label"""
        if is_valid:
            label.setStyleSheet("color: #00cc00;")
        else:
            label.setStyleSheet("color: #888888;")

    def on_confirm_changed(self):
        """Handle confirm password change"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not confirm:
            self.match_label.setText("")
            self.create_btn.setEnabled(False)
            return

        if password == confirm:
            self.match_label.setText("✓ Las contraseñas coinciden")
            self.match_label.setStyleSheet("color: #00cc00;")

            # Enable create button only if password is strong
            validation = self.validate_password(password)
            all_valid = all(validation.values())
            self.create_btn.setEnabled(all_valid)
        else:
            self.match_label.setText("✗ Las contraseñas NO coinciden")
            self.match_label.setStyleSheet("color: #cc0000;")
            self.create_btn.setEnabled(False)

    def create_password(self):
        """Create password and close dialog"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        # Final validation
        if password != confirm:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        validation = self.validate_password(password)
        if not all(validation.values()):
            QMessageBox.warning(self, "Error", "La contraseña no cumple con todos los requisitos")
            return

        # Save password
        try:
            self.auth_manager.set_password(password)
            QMessageBox.information(self, "Éxito", "Contraseña creada exitosamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear contraseña: {e}")
