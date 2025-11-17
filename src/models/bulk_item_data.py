"""
Modelos de datos para creación masiva de items con IA.

Este módulo define las clases de datos (dataclasses) utilizadas para:
- Configurar valores por defecto para items en bulk
- Representar items individuales en el proceso de importación
- Configurar el wizard de creación masiva
- Reportar resultados de validación
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class BulkItemDefaults:
    """
    Valores por defecto que se aplicarán a todos los items en bulk import.

    Estos valores se pueden sobreescribir en cada item individual.
    Se usa el patrón de merge: item individual > defaults > system defaults.
    """
    type: str = 'TEXT'
    tags: str = ''
    is_favorite: int = 0
    is_sensitive: int = 0
    is_list: int = 0
    list_group: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    working_dir: Optional[str] = None
    badge: Optional[str] = None


@dataclass
class BulkItemData:
    """
    Datos de un item individual en el proceso de bulk import.

    Atributos:
        label: Nombre corto del item (requerido, max 200 caracteres)
        content: Contenido del item - comando/url/texto (requerido)
        type: Tipo de item (TEXT, URL, CODE, PATH)
        tags: Tags separados por coma
        description: Descripción opcional del item
        icon: Emoji icon opcional
        color: Color en formato hex (#RRGGBB)
        is_favorite: 1 si es favorito, 0 si no
        is_sensitive: 1 si debe encriptarse, 0 si no
        is_list: 1 si pertenece a una lista secuencial, 0 si no
        list_group: Nombre del grupo de lista (requerido si is_list=1)
        orden_lista: Orden del item en la lista (opcional, se auto-asigna)
        working_dir: Directorio de trabajo para comandos CODE
        badge: Badge opcional para el item
        selected: Flag para UI de previsualización (default True)
    """
    label: str
    content: str
    type: str = 'TEXT'
    tags: str = ''
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_favorite: int = 0
    is_sensitive: int = 0
    is_list: int = 0
    list_group: Optional[str] = None
    orden_lista: Optional[int] = None
    working_dir: Optional[str] = None
    badge: Optional[str] = None

    # Metadata para UI (no se guarda en BD)
    selected: bool = True

    def merge_defaults(self, defaults: BulkItemDefaults) -> None:
        """
        Merge con valores por defecto.

        Si un campo del item está vacío o es el valor por defecto,
        se reemplaza por el valor de defaults.

        Args:
            defaults: Objeto BulkItemDefaults con valores por defecto
        """
        # Type: solo merge si es TEXT (valor por defecto)
        if not self.type or self.type == 'TEXT':
            self.type = defaults.type

        # Tags: merge si está vacío
        if not self.tags:
            self.tags = defaults.tags

        # Booleans: merge si es 0 (False)
        if self.is_favorite == 0 and defaults.is_favorite:
            self.is_favorite = defaults.is_favorite
        if self.is_sensitive == 0 and defaults.is_sensitive:
            self.is_sensitive = defaults.is_sensitive
        if self.is_list == 0 and defaults.is_list:
            self.is_list = defaults.is_list

        # List group: merge solo si is_list=1 y está vacío
        if not self.list_group and defaults.list_group:
            self.list_group = defaults.list_group

        # Opcionales: merge solo si están vacíos
        if not self.icon and defaults.icon:
            self.icon = defaults.icon
        if not self.color and defaults.color:
            self.color = defaults.color
        if not self.description and defaults.description:
            self.description = defaults.description
        if not self.working_dir and defaults.working_dir:
            self.working_dir = defaults.working_dir
        if not self.badge and defaults.badge:
            self.badge = defaults.badge

    def validate(self) -> List[str]:
        """
        Valida que los datos del item sean correctos.

        Returns:
            Lista de errores encontrados (vacía si todo está ok)
        """
        errors = []

        # Label requerido
        if not self.label or not self.label.strip():
            errors.append("Label es requerido")
        elif len(self.label) > 200:
            errors.append(f"Label muy largo ({len(self.label)} caracteres, max 200)")

        # Content requerido
        if not self.content or not self.content.strip():
            errors.append("Content es requerido")

        # Type válido
        valid_types = ['TEXT', 'URL', 'CODE', 'PATH']
        if self.type not in valid_types:
            errors.append(f"Type inválido '{self.type}' (debe ser {', '.join(valid_types)})")

        # Color válido si existe
        if self.color:
            if not self.color.startswith('#') or len(self.color) != 7:
                errors.append(f"Color inválido '{self.color}' (debe ser #RRGGBB)")

        # is_favorite y is_sensitive deben ser 0 o 1
        if self.is_favorite not in [0, 1]:
            errors.append(f"is_favorite debe ser 0 o 1, no {self.is_favorite}")
        if self.is_sensitive not in [0, 1]:
            errors.append(f"is_sensitive debe ser 0 o 1, no {self.is_sensitive}")

        return errors


@dataclass
class BulkImportConfig:
    """
    Configuración para generación de prompt en el wizard.

    Esta clase encapsula toda la información necesaria para generar
    un prompt personalizado que se le dará a la IA.

    Atributos:
        category_id: ID de la categoría donde se crearán los items
        category_name: Nombre de la categoría (para mostrar en prompt)
        defaults: Valores por defecto para los items
        user_context: Contexto adicional del usuario (ej: "pasos para deploy VPS")
    """
    category_id: int
    category_name: str
    defaults: BulkItemDefaults
    user_context: str = ''


@dataclass
class ValidationResult:
    """
    Resultado de validación de JSON.

    Contiene información sobre si el JSON es válido y detalles
    de errores/warnings encontrados.

    Atributos:
        is_valid: True si el JSON pasó todas las validaciones
        errors: Lista de errores críticos que impiden el import
        warnings: Lista de warnings no críticos
        items_count: Cantidad de items encontrados en el JSON
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    items_count: int = 0

    def add_error(self, error: str) -> None:
        """Agrega un error y marca como inválido."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Agrega un warning (no afecta is_valid)."""
        self.warnings.append(warning)

    def get_summary(self) -> str:
        """Retorna resumen legible de la validación."""
        if self.is_valid:
            summary = f"✓ JSON válido - {self.items_count} items encontrados"
            if self.warnings:
                summary += f" ({len(self.warnings)} warnings)"
            return summary
        else:
            return f"✗ JSON inválido - {len(self.errors)} errores encontrados"


@dataclass
class BulkCreationResult:
    """
    Resultado de la creación masiva de items.

    Contiene estadísticas y detalles del proceso de inserción en BD.

    Atributos:
        success: True si al menos un item se creó exitosamente
        created_count: Cantidad de items creados
        failed_count: Cantidad de items que fallaron
        errors: Lista de mensajes de error
        category_id: ID de la categoría donde se crearon
        duration_ms: Duración de la operación en milisegundos
    """
    success: bool
    created_count: int = 0
    failed_count: int = 0
    errors: List[str] = field(default_factory=list)
    category_id: Optional[int] = None
    duration_ms: Optional[int] = None

    def add_error(self, error: str) -> None:
        """Agrega un error al resultado."""
        self.errors.append(error)
        self.failed_count += 1

    def get_summary(self) -> str:
        """Retorna resumen legible del resultado."""
        if self.success:
            msg = f"✓ {self.created_count} items creados exitosamente"
            if self.failed_count > 0:
                msg += f" ({self.failed_count} fallidos)"
            if self.duration_ms:
                msg += f" en {self.duration_ms}ms"
            return msg
        else:
            return f"✗ Creación falló - {len(self.errors)} errores"
