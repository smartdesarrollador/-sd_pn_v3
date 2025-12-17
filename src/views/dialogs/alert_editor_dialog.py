"""
Alert Editor Dialog
Dialog for creating and editing alerts
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit,
    QPushButton, QDialogButtonBox, QMessageBox, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertEditorDialog(QDialog):
    """
    Dialog for creating and editing alerts
    Provides a simple form for alert data entry
    """

    def __init__(self, db_manager, alert=None, item_id=None, parent=None):
        """
        Initialize alert editor dialog

        Args:
            db_manager: DBManager instance
            alert: Alert dictionary for editing (None for create mode)
            item_id: Default item ID for new alerts
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.alert = alert
        self.default_item_id = item_id

        # Determine mode
        self.is_edit_mode = alert is not None

        self.setup_window()
        self.setup_ui()
        self.apply_styles()

        # Load alert data if editing
        if self.is_edit_mode:
            self.load_alert_data()

        logger.info(f"AlertEditorDialog initialized ({'Edit' if self.is_edit_mode else 'Create'} mode)")

    def setup_window(self):
        """Configure window properties"""
        title = "Editar Alerta" if self.is_edit_mode else "Nueva Alerta"
        self.setWindowTitle(title)
        self.setMinimumSize(550, 450)
        self.setModal(True)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("🔔 " + ("Editar Alerta" if self.is_edit_mode else "Nueva Alerta"))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Item selector
        self.item_combo = QComboBox()
        self.load_items()
        form_layout.addRow("Item asociado:", self.item_combo)

        # Alert title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Ej: Recordatorio importante")
        form_layout.addRow("Título:*", self.title_edit)

        # Alert message
        self.message_edit = QTextEdit()
        self.message_edit.setMaximumHeight(120)
        self.message_edit.setPlaceholderText("Mensaje que se mostrará cuando se dispare la alerta")
        form_layout.addRow("Mensaje:*", self.message_edit)

        # Date and time
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
        form_layout.addRow("Fecha y hora:*", self.datetime_edit)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("🟢 Baja", "low")
        self.priority_combo.addItem("🟡 Media", "medium")
        self.priority_combo.addItem("🔴 Alta", "high")
        self.priority_combo.setCurrentIndex(1)  # Default to medium
        form_layout.addRow("Prioridad:", self.priority_combo)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Alerta habilitada")
        self.enabled_checkbox.setChecked(True)
        form_layout.addRow("", self.enabled_checkbox)

        layout.addLayout(form_layout)

        # Info box
        info_label = QLabel(
            "💡 Las alertas se dispararán automáticamente cuando llegue su fecha/hora. "
            "El servicio de alertas revisa cada 60 segundos."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            background-color: #1e3a5f;
            color: #b0d0ff;
            border: 1px solid #2a5a8f;
            border-radius: 4px;
            padding: 10px;
            font-size: 9pt;
        """)
        layout.addWidget(info_label)

        # Required fields note
        note_label = QLabel("* Campos requeridos")
        note_label.setStyleSheet("color: #999999; font-size: 9pt;")
        layout.addWidget(note_label)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("💾 Guardar")
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton("❌ Cancelar")

        button_box.addButton(self.save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def apply_styles(self):
        """Apply dark theme styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit, QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #007acc;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QDateTimeEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QDateTimeEdit:focus {
                border-color: #007acc;
            }
            QCheckBox {
                color: #cccccc;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton[default="true"] {
                background-color: #007acc;
                color: #ffffff;
            }
            QPushButton[default="true"]:hover {
                background-color: #005a9e;
            }
        """)

    def load_items(self):
        """Load items from database into combo box"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, label FROM items ORDER BY label")
            items = cursor.fetchall()

            self.item_combo.clear()

            # Add "None" option at the beginning
            self.item_combo.addItem("(Ninguno - Sin item asociado)", None)

            # Add all items
            for item_id, label in items:
                self.item_combo.addItem(label, item_id)

            # Set default item if provided
            if self.default_item_id:
                index = self.item_combo.findData(self.default_item_id)
                if index >= 0:
                    self.item_combo.setCurrentIndex(index)
            else:
                # Select "None" by default if no default item
                self.item_combo.setCurrentIndex(0)

            logger.debug(f"Loaded {len(items)} items into combo box")

        except Exception as e:
            logger.error(f"Error loading items: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                "Advertencia",
                "No se pudieron cargar los items disponibles."
            )

    def load_alert_data(self):
        """Load alert data into form fields"""
        if not self.alert:
            return

        try:
            # Set item
            item_id = self.alert.get('item_id')
            if item_id:
                index = self.item_combo.findData(item_id)
                if index >= 0:
                    self.item_combo.setCurrentIndex(index)

            # Set title
            self.title_edit.setText(self.alert.get('alert_title', ''))

            # Set message
            self.message_edit.setPlainText(self.alert.get('alert_message', ''))

            # Set datetime
            datetime_str = self.alert.get('alert_datetime', '')
            if datetime_str:
                dt = QDateTime.fromString(datetime_str, "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.datetime_edit.setDateTime(dt)

            # Set priority
            priority = self.alert.get('priority', 'medium')
            index = self.priority_combo.findData(priority)
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)

            # Set enabled
            is_enabled = self.alert.get('is_enabled', 1)
            self.enabled_checkbox.setChecked(bool(is_enabled))

            logger.debug(f"Loaded alert data: {self.alert['id']}")

        except Exception as e:
            logger.error(f"Error loading alert data: {e}", exc_info=True)

    def validate(self):
        """
        Validate form data

        Returns:
            bool: True if valid, False otherwise
        """
        # Check title
        if not self.title_edit.text().strip():
            QMessageBox.warning(
                self,
                "Validación",
                "El título es requerido."
            )
            self.title_edit.setFocus()
            return False

        # Check message
        if not self.message_edit.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Validación",
                "El mensaje es requerido."
            )
            self.message_edit.setFocus()
            return False

        # Item is now optional - no validation needed

        # Check datetime is valid
        if not self.datetime_edit.dateTime().isValid():
            QMessageBox.warning(
                self,
                "Validación",
                "La fecha y hora no son válidas."
            )
            self.datetime_edit.setFocus()
            return False

        return True

    def save(self):
        """Save alert to database"""
        if not self.validate():
            return

        try:
            # Get form data
            item_id = self.item_combo.currentData()
            alert_title = self.title_edit.text().strip()
            alert_message = self.message_edit.toPlainText().strip()
            alert_datetime = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            priority = self.priority_combo.currentData()
            is_enabled = 1 if self.enabled_checkbox.isChecked() else 0

            if self.is_edit_mode:
                # Update existing alert
                success = self.db.update_item_alert(
                    self.alert['id'],
                    item_id=item_id,
                    alert_title=alert_title,
                    alert_message=alert_message,
                    alert_datetime=alert_datetime,
                    priority=priority,
                    is_enabled=is_enabled
                )

                if success:
                    logger.info(f"Alert updated: {self.alert['id']}")
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "Alerta actualizada correctamente."
                    )
                    self.accept()
                else:
                    raise Exception("La actualización retornó False")

            else:
                # Create new alert
                alert_id = self.db.add_item_alert(
                    item_id=item_id,
                    alert_datetime=alert_datetime,
                    alert_title=alert_title,
                    alert_message=alert_message,
                    priority=priority
                )

                # Update is_enabled if unchecked
                if not is_enabled:
                    self.db.update_item_alert(alert_id, is_enabled=0)

                logger.info(f"Alert created: {alert_id}")
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Alerta creada correctamente."
                )
                self.accept()

        except Exception as e:
            logger.error(f"Error saving alert: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar alerta: {str(e)}"
            )
