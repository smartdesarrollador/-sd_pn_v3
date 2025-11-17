"""
Tag Group Editor Dialog - Formulario para crear/editar Tag Groups
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QColorDialog, QMessageBox,
    QCompleter, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.tag_groups_manager import TagGroupsManager

logger = logging.getLogger(__name__)

# Lista de emojis comunes para iconos
EMOJI_OPTIONS = [
    "🏷️", "🐍", "🔴", "⚛️", "🐳", "📦", "💻", "🌐", "🔧", "⚙️",
    "📱", "🎨", "🔒", "🔑", "🗄️", "📊", "🚀", "⭐", "🔥", "💎",
    "🎯", "📚", "🧪", "🔬", "🏗️", "🛠️", "📝", "📄", "💡", "🎓"
]


class TagChip(QFrame):
    """Widget para mostrar un tag como chip/badge"""

    def __init__(self, tag_text: str, color: str = "#007acc", parent=None):
        super().__init__(parent)
        self.tag_text = tag_text
        self.color = color
        self.init_ui()

    def init_ui(self):
        """Inicializar UI del chip"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 12px;
                padding: 6px 12px;
            }}
            QLabel {{
                color: white;
                font-size: 9pt;
                font-weight: bold;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        tag_label = QLabel(f"🏷️ {self.tag_text}")
        layout.addWidget(tag_label)


class TagGroupEditorDialog(QDialog):
    """Diálogo para crear o editar Tag Groups"""

    def __init__(self, db_path: str, group_id: int = None, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.group_id = group_id  # None = crear nuevo, int = editar existente
        self.manager = TagGroupsManager(self.db_path)
        self.current_color = "#007acc"
        self.current_icon = "🏷️"
        self.init_ui()

        # Si es edición, cargar datos
        if self.group_id:
            self.load_group_data()

    def init_ui(self):
        """Inicializar UI"""
        title = "✏️ Editar Grupo de Tags" if self.group_id else "🆕 Nuevo Grupo de Tags"
        self.setWindowTitle(title)
        self.setMinimumSize(600, 650)
        self.setMaximumSize(700, 800)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 8px;
                color: #cccccc;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton#cancelButton {
                background-color: #505050;
            }
            QPushButton#cancelButton:hover {
                background-color: #656565;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel(title)
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3e3e42;")
        main_layout.addWidget(separator)

        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # Nombre
        name_label = QLabel("Nombre del Grupo *")
        name_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Python Backend, React Frontend...")
        self.name_input.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.name_input)

        # Icono y Color en la misma fila
        icon_color_layout = QHBoxLayout()

        # Icono
        icon_layout = QVBoxLayout()
        icon_label = QLabel("Icono")
        icon_label.setStyleSheet("font-weight: bold;")
        icon_layout.addWidget(icon_label)

        self.icon_button = QPushButton(self.current_icon)
        self.icon_button.setFixedSize(60, 60)
        self.icon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 32pt;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(self.current_color, -20)};
            }}
        """)
        self.icon_button.clicked.connect(self.show_icon_selector)
        icon_layout.addWidget(self.icon_button)
        icon_layout.addStretch()

        icon_color_layout.addLayout(icon_layout)
        icon_color_layout.addSpacing(20)

        # Color
        color_layout = QVBoxLayout()
        color_label = QLabel("Color")
        color_label.setStyleSheet("font-weight: bold;")
        color_layout.addWidget(color_label)

        self.color_button = QPushButton("Seleccionar Color")
        self.color_button.setFixedHeight(60)
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(self.current_color, -20)};
            }}
        """)
        self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()

        icon_color_layout.addLayout(color_layout, 1)

        form_layout.addLayout(icon_color_layout)

        # Tags
        tags_label = QLabel("Tags (separados por coma) *")
        tags_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Ej: python, fastapi, api, pydantic, database")
        self.tags_input.textChanged.connect(self.validate_form)
        self.tags_input.textChanged.connect(self.update_tags_preview)
        form_layout.addWidget(self.tags_input)

        # Sugerencia de tags
        tags_hint = QLabel("💡 Consejo: Usa tags cortos y descriptivos. Puedes agregar de 2 a 20 tags.")
        tags_hint.setStyleSheet("color: #808080; font-size: 8pt; font-style: italic;")
        form_layout.addWidget(tags_hint)

        # Vista previa de tags
        preview_label = QLabel("Vista Previa de Tags:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(preview_label)

        # Container para chips de preview
        self.tags_preview_container = QWidget()
        self.tags_preview_layout = QHBoxLayout(self.tags_preview_container)
        self.tags_preview_layout.setContentsMargins(0, 5, 0, 5)
        self.tags_preview_layout.setSpacing(8)
        self.tags_preview_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addWidget(self.tags_preview_container)

        # Mensaje inicial de preview
        self.preview_placeholder = QLabel("Los tags aparecerán aquí...")
        self.preview_placeholder.setStyleSheet("color: #606060; font-style: italic;")
        self.tags_preview_layout.addWidget(self.preview_placeholder)

        # Descripción
        desc_label = QLabel("Descripción (opcional)")
        desc_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe para qué se usa este grupo de tags...")
        self.description_input.setMaximumHeight(80)
        form_layout.addWidget(self.description_input)

        form_layout.addStretch()

        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, 1)

        # Mensaje de validación
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: #ff6b6b; font-size: 9pt;")
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        main_layout.addWidget(self.validation_label)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedHeight(35)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("💾 Guardar")
        self.save_btn.setFixedHeight(35)
        self.save_btn.clicked.connect(self.save_group)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addLayout(buttons_layout)

    def load_group_data(self):
        """Cargar datos del grupo existente para edición"""
        try:
            group = self.manager.get_group(self.group_id)
            if not group:
                QMessageBox.warning(self, "Error", "No se pudo cargar el grupo")
                self.reject()
                return

            # Llenar campos
            self.name_input.setText(group['name'])
            self.tags_input.setText(group['tags'])
            if group.get('description'):
                self.description_input.setPlainText(group['description'])

            # Color e icono
            self.current_color = group.get('color', '#007acc')
            self.current_icon = group.get('icon', '🏷️')
            self.update_icon_color_buttons()

        except Exception as e:
            logger.error(f"Error loading group data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{str(e)}")

    def show_icon_selector(self):
        """Mostrar selector de emojis para el icono"""
        # Crear diálogo simple con grid de emojis
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Icono")
        dialog.setMinimumSize(400, 350)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)

        label = QLabel("Selecciona un emoji:")
        label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(label)

        # Scroll area para emojis
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        emojis_widget = QWidget()
        emojis_layout = QHBoxLayout(emojis_widget)
        emojis_layout.setSpacing(5)

        # Crear botones de emojis con wrapping
        from PyQt6.QtWidgets import QGridLayout
        emojis_widget_grid = QWidget()
        grid_layout = QGridLayout(emojis_widget_grid)
        grid_layout.setSpacing(5)

        for idx, emoji in enumerate(EMOJI_OPTIONS):
            btn = QPushButton(emoji)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 24pt;
                    background-color: #3c3c3c;
                    border: 2px solid #5a5a5a;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #007acc;
                    border-color: #007acc;
                }
            """)
            btn.clicked.connect(lambda checked, e=emoji: self.select_icon(e, dialog))
            row = idx // 8
            col = idx % 8
            grid_layout.addWidget(btn, row, col)

        scroll.setWidget(emojis_widget_grid)
        layout.addWidget(scroll)

        dialog.exec()

    def select_icon(self, emoji: str, dialog: QDialog):
        """Seleccionar un icono"""
        self.current_icon = emoji
        self.update_icon_color_buttons()
        dialog.accept()

    def select_color(self):
        """Abrir selector de color"""
        color = QColorDialog.getColor(QColor(self.current_color), self, "Seleccionar Color")
        if color.isValid():
            self.current_color = color.name()
            self.update_icon_color_buttons()
            self.update_tags_preview()

    def update_icon_color_buttons(self):
        """Actualizar los botones de icono y color"""
        self.icon_button.setText(self.current_icon)
        self.icon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 32pt;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(self.current_color, -20)};
            }}
        """)

        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(self.current_color, -20)};
            }}
        """)
        self.color_button.setText(f"Color: {self.current_color}")

    def adjust_color(self, color_hex: str, delta: int) -> str:
        """Ajustar brillo de un color"""
        try:
            color = QColor(color_hex)
            h, s, v, a = color.getHsv()
            v = max(0, min(255, v + delta))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return color_hex

    def update_tags_preview(self):
        """Actualizar vista previa de tags"""
        # Limpiar preview
        while self.tags_preview_layout.count():
            child = self.tags_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        tags_text = self.tags_input.text().strip()
        if not tags_text:
            # Mostrar placeholder
            self.preview_placeholder = QLabel("Los tags aparecerán aquí...")
            self.preview_placeholder.setStyleSheet("color: #606060; font-style: italic;")
            self.tags_preview_layout.addWidget(self.preview_placeholder)
            return

        # Crear chips para cada tag
        tags_list = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

        if tags_list:
            # Mostrar primeros 8 tags
            for tag in tags_list[:8]:
                chip = TagChip(tag, self.current_color)
                self.tags_preview_layout.addWidget(chip)

            if len(tags_list) > 8:
                more_label = QLabel(f"+{len(tags_list) - 8} más")
                more_label.setStyleSheet("""
                    color: #808080;
                    font-size: 9pt;
                    font-style: italic;
                    padding: 0 8px;
                """)
                self.tags_preview_layout.addWidget(more_label)

            self.tags_preview_layout.addStretch()

    def validate_form(self):
        """Validar formulario en tiempo real"""
        name = self.name_input.text().strip()
        tags = self.tags_input.text().strip()

        errors = []

        # Validar nombre
        if not name:
            errors.append("El nombre es requerido")
        elif len(name) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")

        # Validar tags
        if not tags:
            errors.append("Debes agregar al menos un tag")
        else:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tags_list) < 2:
                errors.append("Debes agregar al menos 2 tags")
            elif len(tags_list) > 20:
                errors.append("Máximo 20 tags permitidos")

            # Validar tags con el manager
            is_valid, message = self.manager.validate_tags(tags)
            if not is_valid:
                errors.append(message)

        # Mostrar errores o habilitar botón
        if errors:
            self.validation_label.setText("⚠️ " + " | ".join(errors))
            self.validation_label.show()
            self.save_btn.setEnabled(False)
        else:
            self.validation_label.hide()
            self.save_btn.setEnabled(True)

    def save_group(self):
        """Guardar el grupo de tags"""
        try:
            name = self.name_input.text().strip()
            tags = self.tags_input.text().strip()
            description = self.description_input.toPlainText().strip()

            if self.group_id:
                # Actualizar existente
                success = self.manager.update_group(
                    self.group_id,
                    name=name,
                    tags=tags,
                    description=description if description else None,
                    color=self.current_color,
                    icon=self.current_icon
                )

                if success:
                    self.accept()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se pudo actualizar el grupo. Verifica que el nombre no esté duplicado."
                    )
            else:
                # Crear nuevo
                group_id = self.manager.create_group(
                    name=name,
                    tags=tags,
                    description=description if description else None,
                    color=self.current_color,
                    icon=self.current_icon
                )

                if group_id:
                    self.accept()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se pudo crear el grupo. Verifica que el nombre no esté duplicado."
                    )

        except Exception as e:
            logger.error(f"Error saving tag group: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{str(e)}")


if __name__ == "__main__":
    """Test del diálogo"""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)

    # Test crear nuevo
    db_path = Path(__file__).parent.parent.parent.parent / "widget_sidebar.db"
    dialog = TagGroupEditorDialog(str(db_path))
    dialog.show()

    sys.exit(app.exec())
