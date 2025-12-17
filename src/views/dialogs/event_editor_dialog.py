"""
Event Editor Dialog
Dialog for creating and editing calendar events
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit,
    QPushButton, QDialogButtonBox, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventEditorDialog(QDialog):
    """
    Dialog for creating and editing calendar events
    Provides a simple form for event data entry
    """

    def __init__(self, db_manager, event=None, item_id=None, parent=None):
        """
        Initialize event editor dialog

        Args:
            db_manager: DBManager instance
            event: Event dictionary for editing (None for create mode)
            item_id: Default item ID for new events
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.event = event
        self.default_item_id = item_id

        # Determine mode
        self.is_edit_mode = event is not None

        self.setup_window()
        self.setup_ui()
        self.apply_styles()

        # Load event data if editing
        if self.is_edit_mode:
            self.load_event_data()

        logger.info(f"EventEditorDialog initialized ({'Edit' if self.is_edit_mode else 'Create'} mode)")

    def setup_window(self):
        """Configure window properties"""
        title = "Editar Evento" if self.is_edit_mode else "Nuevo Evento"
        self.setWindowTitle(title)
        self.setMinimumSize(550, 450)
        self.setModal(True)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("📅 " + ("Editar Evento" if self.is_edit_mode else "Nuevo Evento"))
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

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Ej: Reunión con equipo")
        form_layout.addRow("Título:*", self.title_edit)

        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("Descripción del evento (opcional)")
        form_layout.addRow("Descripción:", self.desc_edit)

        # Date and time
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
        form_layout.addRow("Fecha y hora:*", self.datetime_edit)

        # Event type
        self.type_combo = QComboBox()
        self.type_combo.addItem("📌 Recordatorio", "reminder")
        self.type_combo.addItem("⏰ Fecha límite", "deadline")
        self.type_combo.addItem("✓ Tarea", "task")
        self.type_combo.addItem("📅 Reunión", "meeting")
        self.type_combo.addItem("🎯 Presentación", "presentation")
        form_layout.addRow("Tipo:", self.type_combo)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("🟢 Baja", "low")
        self.priority_combo.addItem("🟡 Media", "medium")
        self.priority_combo.addItem("🔴 Alta", "high")
        self.priority_combo.setCurrentIndex(1)  # Default to medium
        form_layout.addRow("Prioridad:", self.priority_combo)

        layout.addLayout(form_layout)

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

    def load_event_data(self):
        """Load event data into form fields"""
        if not self.event:
            return

        try:
            # Set item
            item_id = self.event.get('item_id')
            if item_id:
                index = self.item_combo.findData(item_id)
                if index >= 0:
                    self.item_combo.setCurrentIndex(index)

            # Set title
            self.title_edit.setText(self.event.get('title', ''))

            # Set description
            self.desc_edit.setPlainText(self.event.get('description', ''))

            # Set datetime
            datetime_str = self.event.get('event_datetime', '')
            if datetime_str:
                dt = QDateTime.fromString(datetime_str, "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.datetime_edit.setDateTime(dt)

            # Set type
            event_type = self.event.get('event_type', 'reminder')
            index = self.type_combo.findData(event_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

            # Set priority
            priority = self.event.get('priority', 'medium')
            index = self.priority_combo.findData(priority)
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)

            logger.debug(f"Loaded event data: {self.event['id']}")

        except Exception as e:
            logger.error(f"Error loading event data: {e}", exc_info=True)

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
        """Save event to database"""
        if not self.validate():
            return

        try:
            # Get form data
            item_id = self.item_combo.currentData()
            title = self.title_edit.text().strip()
            description = self.desc_edit.toPlainText().strip()
            event_datetime = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            event_type = self.type_combo.currentData()
            priority = self.priority_combo.currentData()

            if self.is_edit_mode:
                # Update existing event
                success = self.db.update_calendar_event(
                    self.event['id'],
                    item_id=item_id,
                    title=title,
                    description=description,
                    event_datetime=event_datetime,
                    event_type=event_type,
                    priority=priority
                )

                if success:
                    logger.info(f"Event updated: {self.event['id']}")
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "Evento actualizado correctamente."
                    )
                    self.accept()
                else:
                    raise Exception("La actualización retornó False")

            else:
                # Create new event
                event_id = self.db.add_calendar_event(
                    item_id=item_id,
                    event_datetime=event_datetime,
                    title=title,
                    description=description,
                    event_type=event_type,
                    priority=priority
                )

                logger.info(f"Event created: {event_id}")
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Evento creado correctamente."
                )
                self.accept()

        except Exception as e:
            logger.error(f"Error saving event: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar evento: {str(e)}"
            )
