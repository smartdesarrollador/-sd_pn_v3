"""
Login Dialog
Dialog for user authentication
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.auth_manager import AuthManager
from src.core.session_manager import SessionManager


class LoginDialog(QDialog):
    """Dialog for user authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = AuthManager()
        self.session_manager = SessionManager()
        self.countdown_timer = None
        self.init_ui()
        self.check_lock_status()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Widget Sidebar - Iniciar Sesión")
        self.setFixedSize(450, 350)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("🔐 Iniciar Sesión")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Ingresa tu contraseña para acceder")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(20)

        # Password input
        password_label = QLabel("Contraseña:")
        main_layout.addWidget(password_label)

        # Password container
        password_container = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Ingresa tu contraseña...")
        self.password_input.setMinimumHeight(40)  # Aumentar altura para mejor visibilidad
        self.password_input.returnPressed.connect(self.login)
        password_container.addWidget(self.password_input)

        # Show/hide button
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(40, 40)  # Ajustado para alinearse con el campo
        self.show_password_btn.setToolTip("Mostrar/Ocultar contraseña")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_container.addWidget(self.show_password_btn)

        main_layout.addLayout(password_container)

        # Attempts remaining
        self.attempts_label = QLabel("")
        self.attempts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.attempts_label)

        # Lock message (initially hidden)
        self.lock_label = QLabel("")
        self.lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lock_label.setStyleSheet("color: #cc0000; font-weight: bold; font-size: 11pt;")
        self.lock_label.setWordWrap(True)
        self.lock_label.hide()
        main_layout.addWidget(self.lock_label)

        main_layout.addSpacing(10)

        # Remember checkbox
        self.remember_checkbox = QCheckBox("Recordar por 24 horas")
        self.remember_checkbox.setToolTip("Mantener la sesión activa por 24 horas en lugar de 8")
        main_layout.addWidget(self.remember_checkbox)

        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setFixedSize(100, 35)
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)

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
            QCheckBox {
                color: #cccccc;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)

        # Update attempts display
        self.update_attempts_display()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")

    def check_lock_status(self):
        """Check if account is locked"""
        if self.auth_manager.is_locked():
            remaining = self.auth_manager.get_lock_time_remaining()
            self.show_locked_screen(remaining)

    def show_locked_screen(self, remaining_seconds: int):
        """Show locked screen with countdown"""
        # Disable inputs
        self.password_input.setEnabled(False)
        self.login_btn.setEnabled(False)
        self.remember_checkbox.setEnabled(False)
        self.show_password_btn.setEnabled(False)

        # Show lock message
        self.lock_label.show()
        self.attempts_label.hide()

        # Start countdown timer
        self.update_countdown(remaining_seconds)

        if self.countdown_timer:
            self.countdown_timer.stop()

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(lambda: self.update_countdown(None))
        self.countdown_timer.start(1000)  # Update every second

    def update_countdown(self, initial_seconds=None):
        """Update countdown display"""
        if initial_seconds is not None:
            self.remaining_seconds = initial_seconds

        remaining = self.auth_manager.get_lock_time_remaining()

        if remaining <= 0:
            # Unlock
            if self.countdown_timer:
                self.countdown_timer.stop()

            self.lock_label.hide()
            self.attempts_label.show()
            self.password_input.setEnabled(True)
            self.login_btn.setEnabled(True)
            self.remember_checkbox.setEnabled(True)
            self.show_password_btn.setEnabled(True)
            self.password_input.setFocus()

            # Reset attempts
            self.auth_manager.reset_failed_attempts()
            self.update_attempts_display()
        else:
            # Update countdown
            minutes = remaining // 60
            seconds = remaining % 60
            self.lock_label.setText(
                f"🚫 Cuenta bloqueada\n\n"
                f"Demasiados intentos fallidos.\n"
                f"Intenta nuevamente en: {minutes:02d}:{seconds:02d}"
            )

    def update_attempts_display(self):
        """Update attempts remaining display"""
        failed = self.auth_manager.get_failed_attempts()
        max_attempts = self.auth_manager.MAX_ATTEMPTS
        remaining = max_attempts - failed

        if failed > 0:
            if remaining == 1:
                self.attempts_label.setText(f"⚠ Último intento restante")
                self.attempts_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            elif remaining <= 2:
                self.attempts_label.setText(f"⚠ Intentos restantes: {remaining}")
                self.attempts_label.setStyleSheet("color: #cc7a00; font-weight: bold;")
            else:
                self.attempts_label.setText(f"Intentos restantes: {remaining}")
                self.attempts_label.setStyleSheet("color: #888888;")
        else:
            self.attempts_label.setText("")

    def shake_animation(self):
        """Shake animation on error"""
        # Store original position
        original_geo = self.geometry()

        # Create animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setLoopCount(1)

        # Define shake positions
        for i in range(4):
            offset = 10 if i % 2 == 0 else -10
            rect = QRect(
                original_geo.x() + offset,
                original_geo.y(),
                original_geo.width(),
                original_geo.height()
            )
            self.animation.setKeyValueAt(i * 0.25, rect)

        # Return to original position
        self.animation.setKeyValueAt(1.0, original_geo)
        self.animation.start()

    def show_error_state(self):
        """Show error state (red border)"""
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #cc0000;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
        """)

        # Reset border after 2 seconds
        QTimer.singleShot(2000, self.reset_input_style)

    def reset_input_style(self):
        """Reset input style to normal"""
        self.password_input.setStyleSheet("")

    def login(self):
        """Handle login attempt"""
        # Check if locked
        if self.auth_manager.is_locked():
            remaining = self.auth_manager.get_lock_time_remaining()
            self.show_locked_screen(remaining)
            return

        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "Error", "Por favor ingresa tu contraseña")
            return

        # Verify password
        if self.auth_manager.verify_password(password):
            # Success
            self.auth_manager.reset_failed_attempts()

            # Create session
            remember = self.remember_checkbox.isChecked()
            self.session_manager.create_session(remember=remember)

            self.accept()
        else:
            # Failed
            self.auth_manager.increment_failed_attempts()
            self.update_attempts_display()

            # Clear password
            self.password_input.clear()

            # Show error
            self.show_error_state()
            self.shake_animation()

            # Check if locked now
            if self.auth_manager.is_locked():
                remaining = self.auth_manager.get_lock_time_remaining()
                self.show_locked_screen(remaining)
            else:
                # Show error message
                failed = self.auth_manager.get_failed_attempts()
                max_attempts = self.auth_manager.MAX_ATTEMPTS
                remaining = max_attempts - failed

                QMessageBox.warning(
                    self,
                    "Contraseña Incorrecta",
                    f"Contraseña incorrecta.\nIntentos restantes: {remaining}"
                )
