"""
Widget de contenido de tab para el Creador Masivo

Ensambla todos los widgets de FASE 3:
- ContextSelectorSection
- ProjectElementTagsSection
- ItemFieldsSection
- ItemTagsSection

Gestiona el flujo de datos y auto-guardado.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from src.views.widgets.context_selector_section import ContextSelectorSection
from src.views.widgets.project_element_tags_section import ProjectElementTagsSection
from src.views.widgets.item_fields_section import ItemFieldsSection
from src.views.widgets.category_selector_section import CategorySelectorSection
from src.views.widgets.special_tag_section import SpecialTagSection
from src.views.widgets.item_tags_section import ItemTagsSection
from src.models.item_draft import ItemDraft
import logging

logger = logging.getLogger(__name__)


class TabContentWidget(QWidget):
    """
    Widget de contenido para una pestaña del Creador Masivo

    Ensambla todas las secciones y gestiona el flujo de datos.

    Señales:
        data_changed: Emitida cuando cambian los datos (requiere auto-save)
        create_project_clicked: Solicitud de crear proyecto
        create_area_clicked: Solicitud de crear área
        create_category_clicked: Solicitud de crear categoría
        create_project_tag_clicked: Solicitud de crear tag de proyecto/área
        create_item_tag_clicked: Solicitud de crear tag de item
    """

    # Señales
    data_changed = pyqtSignal()  # Cambio de datos (trigger auto-save)
    create_project_clicked = pyqtSignal()
    create_area_clicked = pyqtSignal()
    create_category_clicked = pyqtSignal()
    create_project_tag_clicked = pyqtSignal()
    create_item_tag_clicked = pyqtSignal()

    def __init__(self, tab_id: str, tab_name: str = "Sin título", db_manager=None, tag_manager=None, parent=None):
        """
        Inicializa el widget de contenido de tab

        Args:
            tab_id: UUID del tab
            tab_name: Nombre del tab
            db_manager: Instancia de DBManager
            tag_manager: Instancia de ProjectElementTagManager
            parent: Widget padre
        """
        super().__init__(parent)
        self.tab_id = tab_id
        self.tab_name = tab_name
        self.db_manager = db_manager
        self.tag_manager = tag_manager
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Área scrollable para todo el contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)

        # Widget contenedor del contenido
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 1. Sección de Contexto (Proyecto, Área, Checkbox Lista)
        self.context_section = ContextSelectorSection()
        content_layout.addWidget(self.context_section)

        # Separador
        self._add_separator(content_layout)

        # 2. Sección de Tags de Proyecto/Área (condicional)
        self.project_tags_section = ProjectElementTagsSection()
        content_layout.addWidget(self.project_tags_section)

        # Separador
        self._add_separator(content_layout)

        # 3. Sección de Items (sin scroll interno)
        self.items_section = ItemFieldsSection()
        content_layout.addWidget(self.items_section)

        # Separador
        self._add_separator(content_layout)

        # 4. NUEVO: Categoría (movida aquí)
        self.category_section = CategorySelectorSection()
        content_layout.addWidget(self.category_section)

        # Separador
        self._add_separator(content_layout)

        # 5. NUEVO: Tag Especial
        self.special_tag_section = SpecialTagSection()
        content_layout.addWidget(self.special_tag_section)

        # Separador
        self._add_separator(content_layout)

        # 6. Tags de Items (opcionales)
        self.item_tags_section = ItemTagsSection()
        content_layout.addWidget(self.item_tags_section)

        # Stretch al final
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _add_separator(self, layout):
        """Agrega un separador horizontal al layout"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #333; min-height: 1px; max-height: 1px;")
        layout.addWidget(separator)

    def _connect_signals(self):
        """Conecta señales de los widgets hijos"""
        # Context section
        self.context_section.project_changed.connect(self._on_project_changed)
        self.context_section.area_changed.connect(self._on_area_changed)
        self.context_section.create_as_list_changed.connect(self._on_create_as_list_changed)
        self.context_section.list_name_changed.connect(self._on_data_changed)

        # Botones de creación (context)
        self.context_section.create_project_clicked.connect(self.create_project_clicked.emit)
        self.context_section.create_area_clicked.connect(self.create_area_clicked.emit)

        # Category section (NUEVO)
        self.category_section.category_changed.connect(self._on_data_changed)
        self.category_section.create_category_clicked.connect(self.create_category_clicked.emit)

        # Special tag section (NUEVO)
        self.special_tag_section.tag_changed.connect(self._on_data_changed)

        # Project tags section
        self.project_tags_section.tags_changed.connect(self._on_data_changed)
        self.project_tags_section.create_tag_clicked.connect(self.create_project_tag_clicked.emit)

        # Items section
        self.items_section.data_changed.connect(self._on_data_changed)

        # Item tags section
        self.item_tags_section.tags_changed.connect(self._on_data_changed)
        self.item_tags_section.create_tag_clicked.connect(self.create_item_tag_clicked.emit)

    def _on_project_changed(self, project_id: int | None):
        """Callback cuando cambia el proyecto"""
        # Mostrar/ocultar sección de tags de proyecto
        has_project_or_area = project_id is not None or self.context_section.get_area_id() is not None
        self.project_tags_section.show_for_project_or_area(has_project_or_area)

        # Cargar tags del proyecto seleccionado
        if project_id is not None and self.tag_manager:
            try:
                tags = self.tag_manager.get_tags_for_project(project_id)
                tag_names = [tag.name for tag in tags]
                self.project_tags_section.load_tags(tag_names)
                logger.debug(f"Cargados {len(tag_names)} tags para proyecto {project_id}")
            except Exception as e:
                logger.error(f"Error cargando tags del proyecto {project_id}: {e}")
        else:
            # Limpiar tags si no hay proyecto seleccionado
            self.project_tags_section.load_tags([])

        self._on_data_changed()

    def _on_area_changed(self, area_id: int | None):
        """Callback cuando cambia el área"""
        # Mostrar/ocultar sección de tags de área
        has_project_or_area = area_id is not None or self.context_section.get_project_id() is not None
        self.project_tags_section.show_for_project_or_area(has_project_or_area)

        # Cargar tags del área seleccionada
        if area_id is not None and self.tag_manager:
            try:
                # Intenta usar método get_tags_for_area si existe, o lista vacía
                if hasattr(self.tag_manager, 'get_tags_for_area'):
                    tags = self.tag_manager.get_tags_for_area(area_id)
                    # Verificar si devuelve objetos o dicts (si implementamos fallback a db directa)
                    tag_names = []
                    for tag in tags:
                        if hasattr(tag, 'name'):
                            tag_names.append(tag.name)
                        elif isinstance(tag, dict) and 'name' in tag:
                            tag_names.append(tag['name'])
                    
                    self.project_tags_section.load_tags(tag_names)
                    logger.debug(f"Cargados {len(tag_names)} tags para área {area_id}")
                else:
                    self.project_tags_section.load_tags([])
            except Exception as e:
                logger.error(f"Error cargando tags del área {area_id}: {e}")
        else:
            # Limpiar tags si no hay área seleccionada
            self.project_tags_section.load_tags([])

        self._on_data_changed()

    def _on_create_as_list_changed(self, is_list: bool):
        """Callback cuando cambia el checkbox de lista"""
        # Habilitar/deshabilitar tag especial según checkbox
        self.special_tag_section.set_enabled(not is_list)

        # Si se marca lista, limpiar tag especial
        if is_list:
            self.special_tag_section.clear()

        # Mostrar/ocultar flechas de ordenamiento en items
        self.items_section.set_create_as_list(is_list)

        self._on_data_changed()
        logger.debug(f"Crear como lista: {is_list} - Tag especial {'deshabilitado' if is_list else 'habilitado'}")

    def _on_data_changed(self):
        """Callback cuando cambian los datos (trigger auto-save)"""
        self.data_changed.emit()
        logger.debug(f"Datos cambiados en tab {self.tab_id}")

    def load_data(self, draft: ItemDraft):
        """
        Carga datos desde un ItemDraft

        Args:
            draft: Borrador con los datos
        """
        logger.info(f"Cargando datos en tab {self.tab_id}: {draft.tab_name}")

        # Cargar contexto
        self.context_section.set_project_id(draft.project_id)
        self.context_section.set_area_id(draft.area_id)
        self.context_section.set_create_as_list(draft.create_as_list)
        self.context_section.set_list_name(draft.list_name or '')

        # Cargar categoría (NUEVO)
        self.category_section.set_category_id(draft.category_id)

        # Cargar tags de proyecto/área
        if draft.project_element_tags:
            self.project_tags_section.set_selected_tags(draft.project_element_tags)

        # Cargar items (ahora son objetos ItemFieldData directamente)
        self.items_section.set_items_data(draft.items)

        # Cargar tag especial (NUEVO)
        if hasattr(draft, 'special_tag') and draft.special_tag:
            self.special_tag_section.set_tag(draft.special_tag)

        # Cargar tags de items
        if draft.item_tags:
            self.item_tags_section.set_selected_tags(draft.item_tags)

        logger.debug(f"Datos cargados: {draft.get_items_count()} items, categoría={draft.category_id}")

    def get_data(self) -> ItemDraft:
        """
        Obtiene los datos actuales como ItemDraft

        Returns:
            ItemDraft con los datos del tab
        """
        # Crear draft
        draft = ItemDraft(
            tab_id=self.tab_id,
            tab_name=self.tab_name,
            project_id=self.context_section.get_project_id(),
            area_id=self.context_section.get_area_id(),
            category_id=self.category_section.get_category_id(),  # NUEVO
            create_as_list=self.context_section.get_create_as_list(),
            list_name=self.context_section.get_list_name(),
            project_element_tags=self.project_tags_section.get_selected_tags(),
            special_tag=self.special_tag_section.get_tag(),  # NUEVO
            item_tags=self.item_tags_section.get_selected_tags()
        )

        # Agregar items (ahora son objetos ItemFieldData, no diccionarios)
        draft.items = self.items_section.get_non_empty_items()

        logger.debug(f"Datos obtenidos: {draft.get_items_count()} items válidos")
        return draft

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida todos los datos del tab

        Validaciones:
        1. Contexto (proyecto/área/lista)
        2. Categoría (OBLIGATORIO)
        3. Tags de proyecto (OBLIGATORIO si hay proyecto/área)
        4. Tag especial (OBLIGATORIO si hay proyecto/área Y NO es lista)
        5. Items (tipos válidos)
        6. Al menos 1 item con contenido
        7. Nombre de lista (si checkbox marcado)

        Returns:
            Tupla (is_valid, list of error_messages)
        """
        errors = []

        # 1. Validar contexto (proyecto/área/lista)
        valid_context, error_msg = self.context_section.validate()
        if not valid_context:
            errors.append(f"Contexto: {error_msg}")

        # 2. Validar categoría (OBLIGATORIO)
        valid_category, category_error = self.category_section.validate()
        if not valid_category:
            errors.append(f"Categoría: {category_error}")

        # Obtener estado para validaciones condicionales
        has_project_or_area = self.context_section.has_project_or_area()
        is_list = self.context_section.get_create_as_list()

        # 3. Validar tags de proyecto (OBLIGATORIO si hay proyecto/área)
        valid_project_tags, project_tags_error = self.project_tags_section.validate(has_project_or_area)
        if not valid_project_tags:
            errors.append(f"Tags de Proyecto: {project_tags_error}")

        # 4. Validar tag especial (OBLIGATORIO si hay proyecto/área Y NO es lista)
        valid_special_tag, special_tag_error = self.special_tag_section.validate(has_project_or_area, is_list)
        if not valid_special_tag:
            errors.append(f"Tag Especial: {special_tag_error}")

        # 5. Validar items (tipos válidos)
        valid_items, item_errors = self.items_section.validate_all()
        if not valid_items:
            for index, error_msg in item_errors:
                errors.append(f"Item {index + 1}: {error_msg}")

        # 6. Verificar que haya al menos 1 item con contenido
        if self.items_section.get_items_count() == 0:
            errors.append("Debe haber al menos 1 item con contenido")

        # 7. Nombre de lista (validado en context_section.validate())

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"Validación exitosa en tab {self.tab_id}")
        else:
            logger.warning(f"Validación fallida en tab {self.tab_id}: {len(errors)} errores")
            for error in errors:
                logger.debug(f"  - {error}")

        return is_valid, errors

    def clear_all(self):
        """Limpia todos los campos del tab"""
        self.context_section.clear()
        self.category_section.clear()  # NUEVO
        self.project_tags_section.clear_selection()
        self.items_section.clear_all_items()
        self.special_tag_section.clear()  # NUEVO
        self.item_tags_section.clear_selection()
        logger.debug(f"Tab {self.tab_id} limpiado")

    def set_tab_name(self, name: str):
        """
        Establece el nombre del tab

        Args:
            name: Nuevo nombre
        """
        self.tab_name = name
        logger.debug(f"Tab {self.tab_id} renombrado a: {name}")

    def get_tab_name(self) -> str:
        """Obtiene el nombre del tab"""
        return self.tab_name

    def get_tab_id(self) -> str:
        """Obtiene el ID del tab"""
        return self.tab_id

    def get_items_count(self) -> int:
        """Obtiene la cantidad de items con contenido"""
        return self.items_section.get_items_count()

    def load_available_projects(self, projects: list[tuple[int, str]]):
        """Carga proyectos disponibles en el selector"""
        self.context_section.load_projects(projects)

    def load_available_areas(self, areas: list[tuple[int, str]]):
        """Carga áreas disponibles en el selector"""
        self.context_section.load_areas(areas)

    def load_available_categories(self, categories: list[tuple[int, str]]):
        """Carga categorías disponibles en el selector"""
        self.category_section.load_categories(categories)

    def load_available_project_tags(self, tags: list[str]):
        """Carga tags de proyecto/área disponibles"""
        self.project_tags_section.load_tags(tags)

    def load_available_item_tags(self, tags: list[str]):
        """Carga tags de items disponibles"""
        self.item_tags_section.load_tags(tags)

    def __repr__(self) -> str:
        """Representación del widget"""
        items_count = self.get_items_count()
        return f"TabContentWidget(id={self.tab_id}, name='{self.tab_name}', items={items_count})"
