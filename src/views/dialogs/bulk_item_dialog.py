"""
Dialog para crear múltiples items de forma masiva

Permite crear varios items rápidamente con las siguientes características:
- Tipo TEXT por defecto
- label = content (mismo valor)
- Tags compartidos para todos los items
- Campos dinámicos según cantidad deseada
- Validación: ignora campos vacíos
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QScrollArea,
    QWidget, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from views.widgets.tag_group_selector import TagGroupSelector

logger = logging.getLogger(__name__)


class BulkItemDialog(QDialog):
    """
    Dialog para crear múltiples items de forma masiva

    Features:
    - Spinner para ajustar cantidad de items (1-50)
    - Campos dinámicos que se crean/destruyen según spinner
    - Tags compartidos entre todos los items
    - Validación: ignora campos vacíos automáticamente
    - Tipo TEXT fijo (editable después individualmente)
    """

    def __init__(self, category_name: str, db_path: str = None, parent=None):
        """
        Inicializar diálogo de creación masiva

        Args:
            category_name: Nombre de la categoría para mostrar en título
            db_path: Path a la base de datos para TagGroupSelector
            parent: Widget padre
        """
        super().__init__(parent)
        self.category_name = category_name
        self.db_path = db_path
        self.item_inputs: List[QLineEdit] = []  # Lista de campos de items

        self.setWindowTitle(f"=Ý Crear Items Masivamente - {category_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.setup_ui()
        self.apply_styles()

        logger.info(f"[BULK_DIALOG] Opened for category: {category_name}")

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # === HEADER ===
        header_label = QLabel("Crea múltiples items de forma rápida")
        header_label.setStyleSheet("font-size: 13px; color: #aaaaaa;")
        layout.addWidget(header_label)

        # === SPINNER DE CANTIDAD ===
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Número de items:"))

        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(50)
        self.quantity_spinbox.setValue(5)  # Default: 5 items
        self.quantity_spinbox.setFixedWidth(80)
        self.quantity_spinbox.valueChanged.connect(self.on_quantity_changed)

        quantity_layout.addWidget(self.quantity_spinbox)
        quantity_layout.addStretch()
        layout.addLayout(quantity_layout)

        # === SCROLL AREA PARA ITEMS ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(400)

        # Widget contenedor para los campos de items
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setSpacing(10)

        scroll.setWidget(self.items_container)
        layout.addWidget(scroll, stretch=1)

        # === CAMPO DE TAGS ===
        tags_label = QLabel("Tags (opcional):")
        tags_label.setStyleSheet("font-size: 12px; margin-top: 5px;")
        layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3 (separados por comas)")
        layout.addWidget(self.tags_input)

        # Tag Group Selector (optional) - wrapped in scroll area
        if self.db_path:
            try:
                self.tag_group_selector = TagGroupSelector(self.db_path, self)
                self.tag_group_selector.tags_changed.connect(self.on_tag_group_changed)

                # Create scroll area for tag group selector
                tags_scroll_area = QScrollArea()
                tags_scroll_area.setWidget(self.tag_group_selector)
                tags_scroll_area.setWidgetResizable(True)
                tags_scroll_area.setFixedHeight(120)  # Fixed height with scroll
                tags_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                tags_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                tags_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
                tags_scroll_area.setStyleSheet("""
                    QScrollArea {
                        border: 1px solid #3d3d3d;
                        border-radius: 4px;
                        background-color: #2d2d2d;
                    }
                    QScrollBar:vertical {
                        background-color: #2d2d2d;
                        width: 12px;
                        border-radius: 6px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: #5a5a5a;
                        border-radius: 6px;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background-color: #007acc;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                """)

                layout.addWidget(tags_scroll_area)
            except Exception as e:
                logger.warning(f"Could not initialize TagGroupSelector: {e}")
                self.tag_group_selector = None
        else:
            self.tag_group_selector = None

        # === SELECTOR DE COLOR ===
        color_label = QLabel("Color (opcional):")
        color_label.setStyleSheet("font-size: 12px; margin-top: 10px;")
        layout.addWidget(color_label)

        # Definir colores disponibles (hex)
        self.colors = {
            "Sin color": None,
            "🔴 Rojo": "#FF4444",
            "🟢 Verde": "#44FF44",
            "🔵 Azul": "#4444FF",
            "🟡 Amarillo": "#FFDD44",
            "🟠 Naranja": "#FF8844",
            "🟣 Morado": "#AA44FF",
            "🌸 Rosa": "#FF44AA",
            "🔷 Cyan": "#44FFFF"
        }

        # Crear QComboBox para selección de color
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.colors.keys())
        self.color_combo.setCurrentIndex(0)  # Default: "Sin color"
        self.color_combo.currentIndexChanged.connect(self.on_color_changed)

        layout.addWidget(self.color_combo)

        # === INFO ===
        info_label = QLabel("9 Tipo: TEXT | label = content | Editable después individualmente")
        info_label.setStyleSheet("font-size: 11px; color: #888888; font-style: italic;")
        layout.addWidget(info_label)

        # === BOTONES ===
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setFixedWidth(100)
        cancel_button.clicked.connect(self.reject)

        self.create_button = QPushButton("Crear Items")
        self.create_button.setFixedWidth(120)
        self.create_button.clicked.connect(self.accept_dialog)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(self.create_button)

        layout.addLayout(buttons_layout)

        # Crear los campos iniciales (5 por defecto)
        self.create_item_fields(5)

        logger.debug(f"[BULK_DIALOG] UI setup complete with {len(self.item_inputs)} initial fields")

    def create_item_fields(self, count: int):
        """
        Crear campos de input para items

        Args:
            count: Número de campos a crear
        """
        # Limpiar campos existentes (layouts y widgets)
        while self.items_layout.count():
            layout_item = self.items_layout.takeAt(0)
            if layout_item.layout():
                # Es un layout, limpiar sus widgets primero
                layout = layout_item.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                layout_item.layout().deleteLater()
            elif layout_item.widget():
                layout_item.widget().deleteLater()

        self.item_inputs.clear()

        # Crear nuevos campos
        for i in range(count):
            field_layout = QHBoxLayout()

            label = QLabel(f"Item {i+1}:")
            label.setFixedWidth(60)
            label.setStyleSheet("font-weight: bold;")

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Nombre del item {i+1}")

            # Enter en el último campo incrementa el spinner
            if i == count - 1:
                line_edit.returnPressed.connect(self.on_last_field_enter)

            field_layout.addWidget(label)
            field_layout.addWidget(line_edit)

            self.items_layout.addLayout(field_layout)
            self.item_inputs.append(line_edit)

        # Focus en el primer campo
        if self.item_inputs:
            self.item_inputs[0].setFocus()

        logger.debug(f"[BULK_DIALOG] Created {count} item fields")

    def on_tag_group_changed(self, tags: list):
        """Handle tag group selector changes"""
        try:
            # Actualizar el campo de tags con los tags seleccionados
            if tags:
                self.tags_input.setText(", ".join(tags))
            else:
                self.tags_input.setText("")
            logger.debug(f"Tags updated from tag group selector: {tags}")
        except Exception as e:
            logger.error(f"Error updating tags from tag group selector: {e}")

    def on_quantity_changed(self, value: int):
        """
        Callback cuando cambia el spinner de cantidad

        Args:
            value: Nueva cantidad de items
        """
        logger.debug(f"[BULK_DIALOG] Quantity changed to: {value}")

        # Guardar valores existentes
        existing_values = [edit.text() for edit in self.item_inputs]

        # Recrear campos
        self.create_item_fields(value)

        # Restaurar valores previos (hasta donde sea posible)
        for i, value_text in enumerate(existing_values):
            if i < len(self.item_inputs):
                self.item_inputs[i].setText(value_text)

    def on_last_field_enter(self):
        """Callback cuando se presiona Enter en el último campo"""
        current_value = self.quantity_spinbox.value()
        if current_value < self.quantity_spinbox.maximum():
            self.quantity_spinbox.setValue(current_value + 1)
            logger.debug("[BULK_DIALOG] Enter pressed on last field, incrementing quantity")

    def get_items_data(self) -> List[Dict]:
        """
        Extraer datos de items no vacíos

        Returns:
            Lista de diccionarios con datos de items:
            [{"label": "...", "tags": [...]}, ...]
        """
        items = []

        # Procesar tags
        tags_str = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

        # Extraer items con contenido
        for i, line_edit in enumerate(self.item_inputs):
            label = line_edit.text().strip()
            if label:  # Ignorar campos vacíos
                items.append({
                    "label": label,
                    "tags": tags.copy()  # Copiar tags para todos
                })
                logger.debug(f"[BULK_DIALOG] Item {i+1}: '{label}' with tags: {tags}")

        logger.info(f"[BULK_DIALOG] Extracted {len(items)} non-empty items (ignored {len(self.item_inputs) - len(items)} empty fields)")

        return items

    def validate(self) -> bool:
        """
        Validar que al menos 1 campo tenga contenido

        Returns:
            True si hay al menos un item, False en caso contrario
        """
        for line_edit in self.item_inputs:
            if line_edit.text().strip():
                return True

        QMessageBox.warning(
            self,
            "Validación",
            "Debes ingresar al menos un item.\n\nTip: Llena los campos con los nombres de los items que deseas crear."
        )
        logger.warning("[BULK_DIALOG] Validation failed: no items entered")
        return False

    def accept_dialog(self):
        """Validar y aceptar el diálogo"""
        if self.validate():
            items_data = self.get_items_data()
            logger.info(f"[BULK_DIALOG] Dialog accepted with {len(items_data)} items")
            self.accept()

    def apply_styles(self):
        """Aplicar estilos CSS al diálogo"""

        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Estilo para el spinner
        self.quantity_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #3a3a3a;
                border: none;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #0d7377;
            }
            QSpinBox::up-arrow {
                width: 10px;
                height: 10px;
            }
            QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)

        # Estilo para campos de items y tags
        input_style = """
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0d7377;
                background-color: #323232;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """

        self.tags_input.setStyleSheet(input_style)

        for line_edit in self.item_inputs:
            line_edit.setStyleSheet(input_style)

        # Estilo para QComboBox de colores
        combo_style = """
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #0d7377;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #0d7377;
                selection-color: #ffffff;
                border: 1px solid #555555;
                outline: none;
            }
        """
        self.color_combo.setStyleSheet(combo_style)

        # Estilo para scroll area
        scroll_style = """
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #0d7377;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #14a2a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.setStyleSheet(scroll_style)

        # Estilo para botones
        cancel_button = self.findChild(QPushButton, "")
        buttons = self.findChildren(QPushButton)

        for button in buttons:
            if button.text() == "Cancelar":
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3a;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-size: 13px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #4a4a4a;
                    }
                    QPushButton:pressed {
                        background-color: #2a2a2a;
                    }
                """)
            elif button.text() == "Crear Items":
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #0d7377;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-size: 13px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #14a2a8;
                    }
                    QPushButton:pressed {
                        background-color: #0a5c5f;
                    }
                """)

        logger.debug("[BULK_DIALOG] Styles applied successfully")

    def on_color_changed(self, index: int):
        """
        Callback cuando cambia la selección de color

        Args:
            index: Índice del item seleccionado en el QComboBox
        """
        selected_text = self.color_combo.currentText()
        color_hex = self.colors.get(selected_text)
        logger.debug(f"[BULK_DIALOG] Color changed to: {selected_text} ({color_hex})")

    def get_selected_color(self) -> str:
        """
        Obtener el color seleccionado

        Returns:
            Código hexadecimal del color o None si no hay color
        """
        selected_text = self.color_combo.currentText()
        return self.colors.get(selected_text)
