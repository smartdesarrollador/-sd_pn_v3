"""
Tag Groups Dialog - Gestión de grupos de tags reutilizables
Permite ver, crear, editar y eliminar Tag Groups
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.tag_groups_manager import TagGroupsManager

logger = logging.getLogger(__name__)


class TagGroupCard(QFrame):
    """Card widget para mostrar un Tag Group"""

    edit_clicked = pyqtSignal(int)  # group_id
    delete_clicked = pyqtSignal(int)  # group_id

    def __init__(self, group: dict, parent=None):
        super().__init__(parent)
        self.group = group
        self.init_ui()

    def init_ui(self):
        """Inicializar UI del card"""
        self.setObjectName("tagGroupCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            #tagGroupCard {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }
            #tagGroupCard:hover {
                background-color: #3e3e42;
                border-color: #007acc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header: icono + nombre + botones
        header_layout = QHBoxLayout()

        # Icono y nombre
        icon_label = QLabel(self.group.get('icon', '🏷️'))
        icon_label.setStyleSheet("font-size: 24pt; padding: 0; margin: 0;")
        header_layout.addWidget(icon_label)

        name_label = QLabel(self.group['name'])
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {self.group.get('color', '#007acc')}; padding-left: 8px;")
        header_layout.addWidget(name_label, 1)

        # Botones de acción
        edit_btn = QPushButton("📝")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Editar grupo")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.group['id']))
        header_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Eliminar grupo")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #a22810;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.group['id']))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Tags
        tags_text = self.group.get('tags', '')
        if tags_text:
            tags_container = QHBoxLayout()
            tags_container.setSpacing(6)

            tags_list = [tag.strip() for tag in tags_text.split(',')]

            # Mostrar primeros 6 tags
            display_tags = tags_list[:6]
            for tag in display_tags:
                tag_label = QLabel(f"🏷️ {tag}")
                tag_label.setStyleSheet("""
                    background-color: #3e3e42;
                    border: 1px solid #5a5a5a;
                    border-radius: 10px;
                    padding: 4px 10px;
                    color: #cccccc;
                    font-size: 9pt;
                """)
                tags_container.addWidget(tag_label)

            # Si hay más tags, mostrar contador
            if len(tags_list) > 6:
                more_label = QLabel(f"+{len(tags_list) - 6}")
                more_label.setStyleSheet("""
                    background-color: #505050;
                    border-radius: 10px;
                    padding: 4px 8px;
                    color: #ffffff;
                    font-size: 9pt;
                    font-weight: bold;
                """)
                tags_container.addWidget(more_label)

            tags_container.addStretch()
            layout.addLayout(tags_container)

        # Descripción
        if self.group.get('description'):
            desc_label = QLabel(self.group['description'])
            desc_label.setStyleSheet("color: #a0a0a0; font-size: 9pt; padding: 4px 0;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Estadísticas
        if 'usage_count' in self.group:
            stats_label = QLabel(f"📊 Usado en {self.group['usage_count']} items")
            stats_label.setStyleSheet("color: #808080; font-size: 8pt; font-style: italic;")
            layout.addWidget(stats_label)


class TagGroupsDialog(QDialog):
    """Diálogo principal para gestionar Tag Groups"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = self.get_db_path()
        self.manager = TagGroupsManager(self.db_path)
        self.init_ui()
        self.load_groups()

    def get_db_path(self) -> str:
        """Obtener ruta de la base de datos"""
        # Intentar obtener desde el parent si es posible
        if hasattr(self.parent(), 'controller'):
            if hasattr(self.parent().controller, 'config_manager'):
                return self.parent().controller.config_manager.db.db_path

        # Fallback: buscar en el directorio raíz del proyecto
        root_dir = Path(__file__).parent.parent.parent.parent
        return str(root_dir / "widget_sidebar.db")

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("🏷️ Gestión de Grupos de Tags")
        self.setMinimumSize(700, 600)
        self.setMaximumSize(900, 800)

        # Aplicar estilos generales
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 8px;
                color: #cccccc;
                font-size: 10pt;
            }
            QLineEdit:focus {
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
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🏷️ Grupos de Tags")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón nuevo grupo
        new_btn = QPushButton("➕ Nuevo Grupo")
        new_btn.setFixedHeight(35)
        new_btn.clicked.connect(self.create_new_group)
        header_layout.addWidget(new_btn)

        main_layout.addLayout(header_layout)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14pt;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar grupos por nombre, descripción o tags...")
        self.search_input.textChanged.connect(self.filter_groups)
        search_layout.addWidget(self.search_input)

        main_layout.addLayout(search_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3e3e42;")
        main_layout.addWidget(separator)

        # Área de scroll para los grupos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container para los cards
        self.groups_container = QWidget()
        self.groups_layout = QVBoxLayout(self.groups_container)
        self.groups_layout.setSpacing(10)
        self.groups_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.groups_container)
        main_layout.addWidget(scroll, 1)

        # Estadísticas generales
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            color: #808080;
            font-size: 9pt;
            padding: 8px;
            background-color: #252526;
            border-radius: 4px;
        """)
        main_layout.addWidget(self.stats_label)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_groups)
        buttons_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

    def load_groups(self, search_query: str = ""):
        """Cargar y mostrar grupos de tags"""
        try:
            # Limpiar container
            while self.groups_layout.count():
                child = self.groups_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Obtener grupos con estadísticas de uso
            if search_query:
                groups = self.manager.search_groups(search_query)
                # Agregar usage_count para cada grupo
                for group in groups:
                    group['usage_count'] = self.manager.get_group_usage_count(group['id'])
            else:
                groups = self.manager.get_all_groups_with_usage()

            # Crear cards
            if groups:
                for group in groups:
                    card = TagGroupCard(group, self)
                    card.edit_clicked.connect(self.edit_group)
                    card.delete_clicked.connect(self.delete_group)
                    self.groups_layout.addWidget(card)
            else:
                # Mensaje cuando no hay grupos
                no_groups_label = QLabel("No se encontraron grupos de tags")
                no_groups_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_groups_label.setStyleSheet("""
                    color: #808080;
                    font-size: 12pt;
                    padding: 40px;
                """)
                self.groups_layout.addWidget(no_groups_label)

            # Agregar stretch al final
            self.groups_layout.addStretch()

            # Actualizar estadísticas
            self.update_statistics()

        except Exception as e:
            logger.error(f"Error loading tag groups: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar grupos de tags:\n{str(e)}")

    def filter_groups(self):
        """Filtrar grupos según el texto de búsqueda"""
        search_query = self.search_input.text().strip()
        self.load_groups(search_query)

    def update_statistics(self):
        """Actualizar estadísticas generales"""
        try:
            stats = self.manager.get_statistics()
            stats_text = (
                f"📊 Total: {stats['total_groups']} grupos | "
                f"✅ Activos: {stats['active_groups']} | "
                f"🏷️ Tags únicos: {stats['unique_tags']}"
            )
            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats_label.setText("📊 Estadísticas no disponibles")

    def create_new_group(self):
        """Abrir diálogo para crear nuevo grupo"""
        try:
            # Importar aquí para evitar dependencias circulares
            from views.dialogs.tag_group_editor_dialog import TagGroupEditorDialog

            dialog = TagGroupEditorDialog(self.db_path, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Recargar grupos
                self.load_groups()
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Grupo de tags creado correctamente"
                )
        except Exception as e:
            logger.error(f"Error creating tag group: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al crear grupo:\n{str(e)}")

    def edit_group(self, group_id: int):
        """Abrir diálogo para editar grupo"""
        try:
            from views.dialogs.tag_group_editor_dialog import TagGroupEditorDialog

            dialog = TagGroupEditorDialog(self.db_path, group_id=group_id, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Recargar grupos
                self.load_groups()
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Grupo de tags actualizado correctamente"
                )
        except Exception as e:
            logger.error(f"Error editing tag group: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al editar grupo:\n{str(e)}")

    def delete_group(self, group_id: int):
        """Eliminar un grupo de tags"""
        try:
            # Obtener información del grupo
            group = self.manager.get_group(group_id)
            if not group:
                QMessageBox.warning(self, "Advertencia", "Grupo no encontrado")
                return

            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Estás seguro de que deseas eliminar el grupo '{group['name']}'?\n\n"
                f"Esto no afectará los items existentes que usan estos tags.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.manager.delete_group(group_id)
                if success:
                    self.load_groups()
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "Grupo eliminado correctamente"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo eliminar el grupo"
                    )
        except Exception as e:
            logger.error(f"Error deleting tag group: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al eliminar grupo:\n{str(e)}")


if __name__ == "__main__":
    """Test del diálogo"""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)

    dialog = TagGroupsDialog()
    dialog.show()

    sys.exit(app.exec())
