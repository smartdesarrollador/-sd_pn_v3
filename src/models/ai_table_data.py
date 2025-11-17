"""
Modelos de datos para creación de tablas con IA.

Este módulo contiene las dataclasses que representan:
- Configuración de tablas
- Estructura de columnas
- Datos completos de tabla
- Resultados de validación
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class TableColumnConfig:
    """
    Configuración de una columna de tabla.

    Attributes:
        name: Nombre de la columna (ej: "NOMBRE", "EMAIL")
        type: Tipo de columna ("TEXT" o "URL")
        is_sensitive: Si contiene datos sensibles (cifrado)
        description: Descripción opcional de la columna
    """
    name: str
    type: str = 'TEXT'  # TEXT | URL
    is_sensitive: bool = False
    description: Optional[str] = None

    def __post_init__(self):
        """Valida que el tipo sea válido."""
        if self.type not in ('TEXT', 'URL'):
            self.type = 'TEXT'


@dataclass
class TableConfigData:
    """
    Configuración general de la tabla.

    Attributes:
        table_name: Nombre único de la tabla
        category_id: ID de la categoría destino
        tags: Lista de tags opcionales
        auto_detect_sensitive: Habilitar detección automática de datos sensibles
        auto_detect_urls: Habilitar detección automática de URLs
    """
    table_name: str
    category_id: int
    tags: List[str] = field(default_factory=list)
    auto_detect_sensitive: bool = True
    auto_detect_urls: bool = True


@dataclass
class TableStructureData:
    """
    Estructura de la tabla (definición de columnas).

    Attributes:
        columns: Lista de configuraciones de columnas
    """
    columns: List[TableColumnConfig]

    def get_column_names(self) -> List[str]:
        """Retorna lista de nombres de columnas."""
        return [col.name for col in self.columns]

    def get_sensitive_indices(self) -> List[int]:
        """Retorna índices de columnas sensibles."""
        return [i for i, col in enumerate(self.columns) if col.is_sensitive]

    def get_url_indices(self) -> List[int]:
        """Retorna índices de columnas tipo URL."""
        return [i for i, col in enumerate(self.columns) if col.type == 'URL']


@dataclass
class AITableData:
    """
    Datos completos de tabla generada por IA.

    Contiene toda la información necesaria para crear una tabla:
    configuración, estructura y datos.

    Attributes:
        table_config: Configuración general
        table_structure: Definición de columnas
        table_data: Matriz de datos (List[List[str]])
        rows_count: Número de filas (auto-calculado)
        cols_count: Número de columnas (auto-calculado)
        filled_cells_count: Número de celdas con datos (auto-calculado)
    """
    table_config: TableConfigData
    table_structure: TableStructureData
    table_data: List[List[str]]  # Matriz de datos

    # Metadata (auto-calculada)
    rows_count: int = 0
    cols_count: int = 0
    filled_cells_count: int = 0

    def __post_init__(self):
        """Calcula metadata automáticamente."""
        self.rows_count = len(self.table_data)
        self.cols_count = len(self.table_structure.columns)

        # Contar celdas llenas
        self.filled_cells_count = sum(
            1 for row in self.table_data
            for cell in row
            if cell and str(cell).strip()
        )

    def get_fill_percentage(self) -> float:
        """
        Calcula porcentaje de celdas llenas.

        Returns:
            Porcentaje entre 0 y 100
        """
        total_cells = self.rows_count * self.cols_count
        if total_cells == 0:
            return 0.0
        return (self.filled_cells_count / total_cells) * 100

    def validate_data_consistency(self) -> tuple[bool, List[str]]:
        """
        Valida que los datos sean consistentes con la estructura.

        Returns:
            Tuple (is_valid, errors)
        """
        errors = []

        # Verificar que todas las filas tengan el mismo número de columnas
        expected_cols = self.cols_count
        for i, row in enumerate(self.table_data):
            if len(row) != expected_cols:
                errors.append(
                    f"Fila {i+1} tiene {len(row)} columnas, "
                    f"esperadas {expected_cols}"
                )

        is_valid = len(errors) == 0
        return is_valid, errors


@dataclass
class AITablePromptConfig:
    """
    Configuración para generación de prompt de IA.

    Attributes:
        table_name: Nombre de la tabla a crear
        category_id: ID de categoría
        category_name: Nombre de categoría (para mostrar en prompt)
        user_context: Contexto/instrucciones del usuario
        expected_rows: Número de filas esperado
        expected_cols: Número de columnas esperado
        columns_config: Configuración de columnas (nombre, es_url, es_sensible)
        tags: Tags opcionales
        auto_detect_sensitive: Habilitar auto-detección de sensibles (DEPRECATED)
        auto_detect_urls: Habilitar auto-detección de URLs (DEPRECATED)
    """
    table_name: str
    category_id: int
    category_name: str
    user_context: str
    expected_rows: int = 10
    expected_cols: int = 4
    columns_config: List[dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    auto_detect_sensitive: bool = False  # Deprecated - siempre False
    auto_detect_urls: bool = False  # Deprecated - siempre False

    def __post_init__(self):
        """Valida valores."""
        if self.expected_rows < 1:
            self.expected_rows = 1
        elif self.expected_rows > 100:
            self.expected_rows = 100

        if self.expected_cols < 1:
            self.expected_cols = 1
        elif self.expected_cols > 20:
            self.expected_cols = 20


@dataclass
class TableValidationResult:
    """
    Resultado de validación de JSON de tabla.

    Attributes:
        is_valid: Si el JSON es válido
        errors: Lista de errores encontrados
        warnings: Lista de advertencias (no bloquean)
        dimensions: Dimensiones detectadas (rows, cols)
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    dimensions: Optional[Dict[str, int]] = None

    def has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Retorna True si hay advertencias."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """
        Retorna resumen de validación.

        Returns:
            String con resumen
        """
        if self.is_valid:
            summary = "✓ JSON válido"
            if self.dimensions:
                summary += f" - {self.dimensions['rows']}×{self.dimensions['cols']}"
            if self.has_warnings():
                summary += f" ({len(self.warnings)} advertencias)"
            return summary
        else:
            return f"✗ JSON inválido - {len(self.errors)} errores"
