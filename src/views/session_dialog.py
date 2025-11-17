"""
Session Dialog - Dialog para gestionar sesiones del navegador
Author: Widget Sidebar Team
Date: 2025-11-03
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class SessionItemWidget(QListWidgetItem):
    """Widget personalizado para items de sesión."""

    def __init__(self, session_data: dict):
        """
        Inicializa el item de sesión.

        Args:
            session_data: Diccionario con datos de la sesión
        """
        super().__init__()
        self.session_data = session_data

        # Formatear texto del item
        name = session_data['name']
        tab_count = session_data.get('tab_count', 0)
        created_at = session_data.get('created_at', '')

        display_text = f"📁 {name}\n   {tab_count} pestaña(s) • {created_at}"
        self.setText(display_text)


class SessionDialog(QDialog):
    """Dialog para gestionar sesiones del navegador."""

    session_restored = pyqtSignal(list)  # Emite lista de pestañas a restaurar

    def __init__(self, session_manager, parent=None):
        """
        Inicializa el dialog.

        Args:
            session_manager: Instancia de BrowserSessionManager
            parent: Widget padre
        """
        super().__init__(parent)
        self.session_manager = session_manager

        self._setup_ui()
        self._apply_styles()
        self._load_sessions()

    def _setup_ui(self):
        """Configura la interfaz del dialog."""
        self.setWindowTitle("Gestor de Sesiones")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(600, 500)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("🗂️ Sesiones Guardadas")
        header_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(header_label)

        # Descripción
        desc_label = QLabel("Guarda y restaura tus pestañas del navegador")
        desc_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(desc_label)

        # Lista de sesiones
        self.sessions_list = QListWidget()
        self.sessions_list.setMinimumHeight(300)
        main_layout.addWidget(self.sessions_list)

        # Botones de acción para sesiones
        session_actions_layout = QHBoxLayout()

        self.restore_btn = QPushButton("Restaurar")
        self.restore_btn.setFixedWidth(100)
        self.restore_btn.clicked.connect(self._restore_session)
        session_actions_layout.addWidget(self.restore_btn)

        self.rename_btn = QPushButton("Renombrar")
        self.rename_btn.setFixedWidth(100)
        self.rename_btn.clicked.connect(self._rename_session)
        session_actions_layout.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setFixedWidth(100)
        self.delete_btn.clicked.connect(self._delete_session)
        session_actions_layout.addWidget(self.delete_btn)

        session_actions_layout.addStretch()

        main_layout.addLayout(session_actions_layout)

        # Botón de cerrar
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

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

            QListWidget {
                background-color: #16213e;
                color: #00d4ff;
                border: 1px solid #0f3460;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }

            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 2px;
            }

            QListWidget::item:selected {
                background-color: #0f3460;
                border: 1px solid #00d4ff;
            }

            QListWidget::item:hover {
                background-color: rgba(0, 212, 255, 0.1);
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

            QPushButton:disabled {
                background-color: #0f1f2e;
                color: #4a5568;
                border: 1px solid #2d3748;
            }
        """)

    def _load_sessions(self):
        """Carga las sesiones en la lista."""
        self.sessions_list.clear()

        sessions = self.session_manager.get_all_sessions(include_auto_save=False)

        if not sessions:
            # Mostrar mensaje si no hay sesiones
            item = QListWidgetItem("No hay sesiones guardadas")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.sessions_list.addItem(item)
            self._update_button_states(False)
            return

        # Agregar sesiones a la lista
        for session in sessions:
            item = SessionItemWidget(session)
            self.sessions_list.addItem(item)

        self._update_button_states(True)

    def _update_button_states(self, enabled: bool):
        """
        Actualiza el estado de los botones.

        Args:
            enabled: Si habilitar o deshabilitar los botones
        """
        self.restore_btn.setEnabled(enabled)
        self.rename_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)

    def _restore_session(self):
        """Restaura la sesión seleccionada."""
        current_item = self.sessions_list.currentItem()

        if not current_item or not isinstance(current_item, SessionItemWidget):
            QMessageBox.warning(
                self,
                "Advertencia",
                "Por favor selecciona una sesión para restaurar"
            )
            return

        session_id = current_item.session_data['id']
        session_name = current_item.session_data['name']

        # Confirmar restauración
        reply = QMessageBox.question(
            self,
            "Confirmar Restauración",
            f"¿Deseas restaurar la sesión '{session_name}'?\n\n"
            "Esto cerrará las pestañas actuales y abrirá las de la sesión guardada.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Restaurar sesión
            tabs = self.session_manager.restore_session(session_id)

            if tabs:
                logger.info(f"Restaurando sesión: {session_name}")
                self.session_restored.emit(tabs)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No se pudo restaurar la sesión '{session_name}'"
                )

    def _rename_session(self):
        """Renombra la sesión seleccionada."""
        current_item = self.sessions_list.currentItem()

        if not current_item or not isinstance(current_item, SessionItemWidget):
            QMessageBox.warning(
                self,
                "Advertencia",
                "Por favor selecciona una sesión para renombrar"
            )
            return

        session_id = current_item.session_data['id']
        current_name = current_item.session_data['name']

        # Pedir nuevo nombre
        new_name, ok = QInputDialog.getText(
            self,
            "Renombrar Sesión",
            "Nuevo nombre:",
            QLineEdit.EchoMode.Normal,
            current_name
        )

        if ok and new_name:
            success = self.session_manager.rename_session(session_id, new_name)

            if success:
                logger.info(f"Sesión renombrada: {current_name} -> {new_name}")
                self._load_sessions()  # Recargar lista
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No se pudo renombrar la sesión"
                )

    def _delete_session(self):
        """Elimina la sesión seleccionada."""
        current_item = self.sessions_list.currentItem()

        if not current_item or not isinstance(current_item, SessionItemWidget):
            QMessageBox.warning(
                self,
                "Advertencia",
                "Por favor selecciona una sesión para eliminar"
            )
            return

        session_id = current_item.session_data['id']
        session_name = current_item.session_data['name']

        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar la sesión '{session_name}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_manager.delete_session(session_id)

            if success:
                logger.info(f"Sesión eliminada: {session_name}")
                self._load_sessions()  # Recargar lista
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No se pudo eliminar la sesión"
                )
