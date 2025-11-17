"""
Smart Collection Editor Dialog - Formulario para crear/editar Smart Collections
Incluye múltiples filtros: tags, tipo, categoría, estado, fechas, búsqueda
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QFrame, QColorDialog, QMessageBox,
    QComboBox, QCheckBox, QDateEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.smart_collections_manager import SmartCollectionsManager
from database.db_manager import DBManager

logger = logging.getLogger(__name__)

# Lista de emojis comunes para iconos de colecciones
COLLECTION_EMOJI_OPTIONS = [
    "🔍", "🐍", "🔴", "⚛️", "🐳", "📦", "💻", "🌐", "🔗", "⚙️",
    "📱", "🎨", "🔒", "🔑", "🗄️", "📊", "🚀", "⭐", "⚠️", "💎",
    "🎯", "📚", "🧪", "🔬", "🏗️", "🛠️", "📝", "📄", "💡", "🎓"
]


class SmartCollectionEditorDialog(QDialog):
    """Diálogo para crear o editar Smart Collections"""

    def __init__(self, db_path: str, collection_id: int = None, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.collection_id = collection_id  # None = crear nuevo, int = editar existente
        self.manager = SmartCollectionsManager(self.db_path)
        self.db = DBManager(self.db_path)
        self.current_color = "#00d4ff"
        self.current_icon = "🔍"

        # Timer para actualizar preview con delay
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview_count)

        self.init_ui()

        # Si es edición, cargar datos
        if self.collection_id:
            self.load_collection_data()
        else:
            # Preview inicial
            self.update_preview_count()

    def init_ui(self):
        """Inicializar UI"""
        title = "✏️ Editar Colección Inteligente" if self.collection_id else "🆕 Nueva Colección Inteligente"
        self.setWindowTitle(title)
        self.setMinimumSize(700, 750)
        self.setMaximumSize(800, 850)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #3c3c3c;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 6px;
                color: #cccccc;
                font-size: 10pt;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #007acc;
            }
            QCheckBox {
                color: #cccccc;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
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
            QPushButton#cancelButton {
                background-color: #505050;
            }
            QPushButton#cancelButton:hover {
                background-color: #656565;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
        separator.setStyleSheet("background-color: #3e3e42;")
        main_layout.addWidget(separator)

        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # ========== SECCIÓN 1: Información Básica ==========
        basic_group = QGroupBox("📋 Información Básica")
        basic_layout = QVBoxLayout()
        basic_layout.setSpacing(10)

        # Nombre
        name_layout = QVBoxLayout()
        name_label = QLabel("Nombre *")
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: APIs Python Activas, URLs Laravel...")
        self.name_input.textChanged.connect(self.validate_form)
        self.name_input.textChanged.connect(self.schedule_preview_update)
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)

        # Icono y Color
        icon_color_layout = QHBoxLayout()

        # Icono
        icon_layout = QVBoxLayout()
        icon_label = QLabel("Icono")
        icon_layout.addWidget(icon_label)
        self.icon_button = QPushButton(self.current_icon)
        self.icon_button.setFixedSize(60, 60)
        self.icon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 32pt;
                border-radius: 8px;
            }}
        """)
        self.icon_button.clicked.connect(self.show_icon_selector)
        icon_layout.addWidget(self.icon_button)
        icon_color_layout.addLayout(icon_layout)

        icon_color_layout.addSpacing(15)

        # Color
        color_layout = QVBoxLayout()
        color_label = QLabel("Color")
        color_layout.addWidget(color_label)
        self.color_button = QPushButton("Seleccionar Color")
        self.color_button.setFixedHeight(60)
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
            }}
        """)
        self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        icon_color_layout.addLayout(color_layout, 1)

        basic_layout.addLayout(icon_color_layout)

        # Descripción
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Descripción (opcional)")
        desc_layout.addWidget(desc_label)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Describe qué filtra esta colección...")
        desc_layout.addWidget(self.description_input)
        basic_layout.addLayout(desc_layout)

        basic_group.setLayout(basic_layout)
        form_layout.addWidget(basic_group)

        # ========== SECCIÓN 2: Filtros de Tags ==========
        tags_group = QGroupBox("🏷️ Filtros de Tags")
        tags_layout = QVBoxLayout()
        tags_layout.setSpacing(10)

        # Tags a incluir
        include_layout = QVBoxLayout()
        include_label = QLabel("Tags a incluir (debe tener al menos uno de estos):")
        include_layout.addWidget(include_label)
        self.tags_include_input = QLineEdit()
        self.tags_include_input.setPlaceholderText("python, fastapi, api (separados por comas)")
        self.tags_include_input.textChanged.connect(self.schedule_preview_update)
        include_layout.addWidget(self.tags_include_input)
        tags_layout.addLayout(include_layout)

        # Tags a excluir
        exclude_layout = QVBoxLayout()
        exclude_label = QLabel("Tags a excluir (NO debe tener ninguno de estos):")
        exclude_layout.addWidget(exclude_label)
        self.tags_exclude_input = QLineEdit()
        self.tags_exclude_input.setPlaceholderText("deprecated, legacy, old (separados por comas)")
        self.tags_exclude_input.textChanged.connect(self.schedule_preview_update)
        exclude_layout.addWidget(self.tags_exclude_input)
        tags_layout.addLayout(exclude_layout)

        tags_group.setLayout(tags_layout)
        form_layout.addWidget(tags_group)

        # ========== SECCIÓN 3: Tipo de Item ==========
        type_group = QGroupBox("📝 Tipo de Item")
        type_layout = QVBoxLayout()
        type_layout.setSpacing(8)

        type_hint = QLabel("Selecciona el tipo de item (dejar en 'Todos' para no filtrar):")
        type_hint.setStyleSheet("color: #808080; font-size: 9pt;")
        type_layout.addWidget(type_hint)

        self.item_type_combo = QComboBox()
        self.item_type_combo.addItem("Todos", None)
        self.item_type_combo.addItem("CODE - Comandos/Scripts", "CODE")
        self.item_type_combo.addItem("URL - Enlaces", "URL")
        self.item_type_combo.addItem("PATH - Rutas de archivos", "PATH")
        self.item_type_combo.addItem("TEXT - Texto general", "TEXT")
        self.item_type_combo.currentIndexChanged.connect(self.schedule_preview_update)
        type_layout.addWidget(self.item_type_combo)

        type_group.setLayout(type_layout)
        form_layout.addWidget(type_group)

        # ========== SECCIÓN 4: Categoría ==========
        category_group = QGroupBox("📁 Categoría")
        category_layout = QVBoxLayout()
        category_layout.setSpacing(8)

        category_hint = QLabel("Filtrar por categoría específica:")
        category_hint.setStyleSheet("color: #808080; font-size: 9pt;")
        category_layout.addWidget(category_hint)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Todas las categorías", None)
        # Cargar categorías
        self.load_categories()
        self.category_combo.currentIndexChanged.connect(self.schedule_preview_update)
        category_layout.addWidget(self.category_combo)

        category_group.setLayout(category_layout)
        form_layout.addWidget(category_group)

        # ========== SECCIÓN 5: Estados Booleanos ==========
        states_group = QGroupBox("⚡ Filtros de Estado")
        states_layout = QVBoxLayout()
        states_layout.setSpacing(8)

        self.favorite_check = QCheckBox("Solo items marcados como favoritos")
        self.favorite_check.stateChanged.connect(self.schedule_preview_update)
        states_layout.addWidget(self.favorite_check)

        self.sensitive_check = QCheckBox("Solo items sensibles (cifrados)")
        self.sensitive_check.stateChanged.connect(self.schedule_preview_update)
        states_layout.addWidget(self.sensitive_check)

        self.active_check = QCheckBox("Solo items activos")
        self.active_check.stateChanged.connect(self.schedule_preview_update)
        states_layout.addWidget(self.active_check)

        self.archived_check = QCheckBox("Solo items archivados")
        self.archived_check.stateChanged.connect(self.schedule_preview_update)
        states_layout.addWidget(self.archived_check)

        states_group.setLayout(states_layout)
        form_layout.addWidget(states_group)

        # ========== SECCIÓN 6: Búsqueda de Texto ==========
        search_group = QGroupBox("🔎 Búsqueda de Texto")
        search_layout = QVBoxLayout()
        search_layout.setSpacing(8)

        search_hint = QLabel("Buscar texto en nombre o contenido del item:")
        search_hint.setStyleSheet("color: #808080; font-size: 9pt;")
        search_layout.addWidget(search_hint)

        self.search_text_input = QLineEdit()
        self.search_text_input.setPlaceholderText("Ej: authenticate, login, etc.")
        self.search_text_input.textChanged.connect(self.schedule_preview_update)
        search_layout.addWidget(self.search_text_input)

        search_group.setLayout(search_layout)
        form_layout.addWidget(search_group)

        # ========== SECCIÓN 7: Rango de Fechas ==========
        dates_group = QGroupBox("📅 Rango de Fechas")
        dates_layout = QVBoxLayout()
        dates_layout.setSpacing(10)

        dates_hint = QLabel("Filtrar por fecha de creación del item:")
        dates_hint.setStyleSheet("color: #808080; font-size: 9pt;")
        dates_layout.addWidget(dates_hint)

        # Fecha desde
        from_layout = QHBoxLayout()
        from_label = QLabel("Desde:")
        from_layout.addWidget(from_label)
        self.date_from_check = QCheckBox("Activar")
        self.date_from_check.stateChanged.connect(self.on_date_from_toggled)
        from_layout.addWidget(self.date_from_check)
        self.date_from_input = QDateEdit()
        self.date_from_input.setDate(QDate.currentDate().addMonths(-1))
        self.date_from_input.setCalendarPopup(True)
        self.date_from_input.setEnabled(False)
        self.date_from_input.dateChanged.connect(self.schedule_preview_update)
        from_layout.addWidget(self.date_from_input, 1)
        dates_layout.addLayout(from_layout)

        # Fecha hasta
        to_layout = QHBoxLayout()
        to_label = QLabel("Hasta:")
        to_layout.addWidget(to_label)
        self.date_to_check = QCheckBox("Activar")
        self.date_to_check.stateChanged.connect(self.on_date_to_toggled)
        to_layout.addWidget(self.date_to_check)
        self.date_to_input = QDateEdit()
        self.date_to_input.setDate(QDate.currentDate())
        self.date_to_input.setCalendarPopup(True)
        self.date_to_input.setEnabled(False)
        self.date_to_input.dateChanged.connect(self.schedule_preview_update)
        to_layout.addWidget(self.date_to_input, 1)
        dates_layout.addLayout(to_layout)

        dates_group.setLayout(dates_layout)
        form_layout.addWidget(dates_group)

        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, 1)

        # Vista previa de conteo
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("""
            background-color: #252526;
            border: 2px solid #007acc;
            border-radius: 6px;
            padding: 12px;
            font-size: 11pt;
            font-weight: bold;
            color: #00d4ff;
        """)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.preview_label)

        # Mensaje de validación
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: #ff6b6b; font-size: 9pt;")
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
        self.save_btn.clicked.connect(self.save_collection)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addLayout(buttons_layout)

    def load_categories(self):
        """Cargar categorías en el combo"""
        try:
            categories = self.db.get_all_categories()
            for category in categories:
                icon = category.icon if hasattr(category, 'icon') and category.icon else "📁"
                self.category_combo.addItem(f"{icon} {category.name}", category.id)
        except Exception as e:
            logger.error(f"Error loading categories: {e}")

    def on_date_from_toggled(self, state):
        """Manejar activación/desactivación de fecha desde"""
        self.date_from_input.setEnabled(state == Qt.CheckState.Checked.value)
        self.schedule_preview_update()

    def on_date_to_toggled(self, state):
        """Manejar activación/desactivación de fecha hasta"""
        self.date_to_input.setEnabled(state == Qt.CheckState.Checked.value)
        self.schedule_preview_update()

    def show_icon_selector(self):
        """Mostrar selector de emojis"""
        from PyQt6.QtWidgets import QGridLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Icono")
        dialog.setMinimumSize(400, 350)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)
        label = QLabel("Selecciona un emoji:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        emojis_widget = QWidget()
        grid_layout = QGridLayout(emojis_widget)

        for idx, emoji in enumerate(COLLECTION_EMOJI_OPTIONS):
            btn = QPushButton(emoji)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 24pt;
                    background-color: #3c3c3c;
                    border: 2px solid #5a5a5a;
                }
                QPushButton:hover {
                    background-color: #007acc;
                }
            """)
            btn.clicked.connect(lambda checked, e=emoji: self.select_icon(e, dialog))
            grid_layout.addWidget(btn, idx // 8, idx % 8)

        scroll.setWidget(emojis_widget)
        layout.addWidget(scroll)
        dialog.exec()

    def select_icon(self, emoji: str, dialog: QDialog):
        """Seleccionar icono"""
        self.current_icon = emoji
        self.update_icon_color_buttons()
        dialog.accept()

    def select_color(self):
        """Seleccionar color"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.update_icon_color_buttons()

    def update_icon_color_buttons(self):
        """Actualizar botones de icono y color"""
        self.icon_button.setText(self.current_icon)
        self.icon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                font-size: 32pt;
                border-radius: 8px;
            }}
        """)
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
            }}
        """)
        self.color_button.setText(f"Color: {self.current_color}")

    def schedule_preview_update(self):
        """Programar actualización de preview con delay"""
        self.preview_timer.stop()
        self.preview_timer.start(500)  # 500ms delay

    def update_preview_count(self):
        """Actualizar contador de preview"""
        try:
            # Crear colección temporal con los filtros actuales
            temp_collection = self.get_filter_data()

            # Ejecutar filtros
            items = self.manager._execute_filters(temp_collection)
            count = len(items)

            # Actualizar label
            self.preview_label.setText(f"📊 Vista previa: {count} items coinciden con estos filtros")

        except Exception as e:
            logger.error(f"Error updating preview: {e}")
            self.preview_label.setText("📊 Vista previa: Error al calcular")

    def get_filter_data(self) -> dict:
        """Obtener datos de los filtros actuales"""
        return {
            'name': self.name_input.text().strip(),
            'tags_include': self.tags_include_input.text().strip() or None,
            'tags_exclude': self.tags_exclude_input.text().strip() or None,
            'category_id': self.category_combo.currentData(),
            'item_type': self.item_type_combo.currentData(),
            'is_favorite': True if self.favorite_check.isChecked() else None,
            'is_sensitive': True if self.sensitive_check.isChecked() else None,
            'is_active_filter': True if self.active_check.isChecked() else None,
            'is_archived_filter': True if self.archived_check.isChecked() else None,
            'search_text': self.search_text_input.text().strip() or None,
            'date_from': self.date_from_input.date().toString("yyyy-MM-dd") if self.date_from_check.isChecked() else None,
            'date_to': self.date_to_input.date().toString("yyyy-MM-dd") if self.date_to_check.isChecked() else None,
        }

    def validate_form(self):
        """Validar formulario"""
        name = self.name_input.text().strip()

        if not name:
            self.validation_label.setText("⚠️ El nombre es requerido")
            self.validation_label.show()
            self.save_btn.setEnabled(False)
            return False

        if len(name) < 3:
            self.validation_label.setText("⚠️ El nombre debe tener al menos 3 caracteres")
            self.validation_label.show()
            self.save_btn.setEnabled(False)
            return False

        self.validation_label.hide()
        self.save_btn.setEnabled(True)
        return True

    def load_collection_data(self):
        """Cargar datos de colección existente"""
        try:
            collection = self.manager.get_collection(self.collection_id)
            if not collection:
                QMessageBox.warning(self, "Error", "No se pudo cargar la colección")
                self.reject()
                return

            # Información básica
            self.name_input.setText(collection['name'])
            if collection.get('description'):
                self.description_input.setText(collection['description'])
            self.current_color = collection.get('color', '#00d4ff')
            self.current_icon = collection.get('icon', '🔍')
            self.update_icon_color_buttons()

            # Tags
            if collection.get('tags_include'):
                self.tags_include_input.setText(collection['tags_include'])
            if collection.get('tags_exclude'):
                self.tags_exclude_input.setText(collection['tags_exclude'])

            # Tipo
            if collection.get('item_type'):
                for i in range(self.item_type_combo.count()):
                    if self.item_type_combo.itemData(i) == collection['item_type']:
                        self.item_type_combo.setCurrentIndex(i)
                        break

            # Categoría
            if collection.get('category_id'):
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == collection['category_id']:
                        self.category_combo.setCurrentIndex(i)
                        break

            # Estados
            if collection.get('is_favorite'):
                self.favorite_check.setChecked(True)
            if collection.get('is_sensitive'):
                self.sensitive_check.setChecked(True)
            if collection.get('is_active_filter'):
                self.active_check.setChecked(True)
            if collection.get('is_archived_filter'):
                self.archived_check.setChecked(True)

            # Búsqueda
            if collection.get('search_text'):
                self.search_text_input.setText(collection['search_text'])

            # Fechas
            if collection.get('date_from'):
                self.date_from_check.setChecked(True)
                self.date_from_input.setDate(QDate.fromString(collection['date_from'], "yyyy-MM-dd"))
            if collection.get('date_to'):
                self.date_to_check.setChecked(True)
                self.date_to_input.setDate(QDate.fromString(collection['date_to'], "yyyy-MM-dd"))

        except Exception as e:
            logger.error(f"Error loading collection data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{str(e)}")

    def save_collection(self):
        """Guardar colección"""
        try:
            if not self.validate_form():
                return

            filter_data = self.get_filter_data()

            if self.collection_id:
                # Actualizar
                success = self.manager.update_collection(
                    self.collection_id,
                    name=filter_data['name'],
                    description=self.description_input.text().strip() or None,
                    icon=self.current_icon,
                    color=self.current_color,
                    **{k: v for k, v in filter_data.items() if k not in ['name']}
                )
                if success:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar la colección")
            else:
                # Crear
                collection_id = self.manager.create_collection(
                    name=filter_data['name'],
                    description=self.description_input.text().strip() or None,
                    icon=self.current_icon,
                    color=self.current_color,
                    **{k: v for k, v in filter_data.items() if k not in ['name']}
                )
                if collection_id:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear la colección")

        except Exception as e:
            logger.error(f"Error saving collection: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{str(e)}")


if __name__ == "__main__":
    """Test del diálogo"""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    logging.basicConfig(level=logging.DEBUG)

    db_path = Path(__file__).parent.parent.parent.parent / "widget_sidebar.db"
    dialog = SmartCollectionEditorDialog(str(db_path))
    dialog.show()

    sys.exit(app.exec())
