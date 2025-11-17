"""
Notification Widget - Widget para mostrar notificaciones en main window
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class NotificationWidget(QWidget):
    """Widget para mostrar notificaciones en main window"""

    action_triggered = pyqtSignal(str)  # action name
    dismissed = pyqtSignal()

    def __init__(self, notification: Dict, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.init_ui()
        self.animate_entry()

    def init_ui(self):
        """Inicializar UI"""
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Color según tipo
        colors = {
            'suggestion': '#007acc',  # Azul
            'alert': '#cc7a00',       # Naranja
            'warning': '#c42b1c',     # Rojo
            'info': '#00897b'         # Turquesa/Verde
        }
        color = colors.get(self.notification.get('type', 'info'), '#858585')

        # Icono según tipo
        icons = {
            'suggestion': '💡',
            'alert': '⚠️',
            'warning': '🚨',
            'info': 'ℹ️'
        }
        icon = icons.get(self.notification.get('type', 'info'), '📢')

        # Estilo del widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 6px;
                border-left: 4px solid {self._darken_color(color)};
            }}
            QLabel {{
                color: white;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.9);
                color: {color};
                border: none;
                padding: 6px 15px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.8);
            }}
        """)

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24pt;")
        icon_label.setFixedWidth(40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Mensaje
        message_label = QLabel(self.notification.get('message', ''))
        message_label.setWordWrap(True)
        message_font = QFont()
        message_font.setPointSize(9)
        message_label.setFont(message_font)
        layout.addWidget(message_label, 1)

        # Botón de acción
        action_btn = QPushButton("Ver")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_btn.clicked.connect(self.on_action_clicked)
        layout.addWidget(action_btn)

        # Botón cerrar
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.on_dismiss)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                font-size: 12pt;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        layout.addWidget(close_btn)

    def _darken_color(self, hex_color: str) -> str:
        """Oscurecer un color hexadecimal"""
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Oscurecer (reducir cada componente en 30%)
        r = int(r * 0.7)
        g = int(g * 0.7)
        b = int(b * 0.7)

        # Convertir de vuelta a hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def animate_entry(self):
        """Animar entrada del widget"""
        self.setMaximumHeight(0)

        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(80)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def animate_exit(self):
        """Animar salida del widget"""
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def on_action_clicked(self):
        """Handler de acción"""
        action = self.notification.get('action', '')
        logger.info(f"Notification action triggered: {action}")
        self.action_triggered.emit(action)
        self.animate_exit()

    def on_dismiss(self):
        """Handler de cierre"""
        logger.info(f"Notification dismissed: {self.notification.get('category', 'unknown')}")
        self.dismissed.emit()
        self.animate_exit()
