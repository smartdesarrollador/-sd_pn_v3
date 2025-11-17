"""
Table Validator
Utilidades de validación para tablas de items

Proporciona métodos estáticos para validar:
- Nombres de tabla
- Datos de tabla
- Contenido de celdas
- Nombres de columnas
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import sys

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class TableValidator:
    """
    Clase utilitaria con métodos estáticos para validación de tablas.

    No requiere instanciación, todos los métodos son estáticos.
    """

    # Constantes de validación
    MAX_TABLE_NAME_LENGTH = 100
    MAX_CELL_LENGTH = 5000
    MIN_ROWS = 1
    MAX_ROWS = 100
    MIN_COLS = 1
    MAX_COLS = 20

    # Regex para nombre de tabla (mayúsculas, minúsculas, números, guiones y guiones bajos)
    TABLE_NAME_PATTERN = r'^[A-Za-z0-9_\-]+$'

    # Nombres de tabla reservados (SQL keywords)
    RESERVED_NAMES = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'FROM', 'WHERE', 'JOIN',
        'INNER', 'OUTER', 'LEFT', 'RIGHT', 'ON', 'AS', 'AND', 'OR', 'NOT',
        'NULL', 'IS', 'IN', 'BETWEEN', 'LIKE', 'ORDER', 'BY', 'GROUP',
        'HAVING', 'DISTINCT', 'UNION', 'ALL', 'EXISTS', 'CASE', 'WHEN',
        'THEN', 'ELSE', 'END', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
        'CONSTRAINT', 'DEFAULT', 'CHECK', 'UNIQUE', 'COUNT', 'SUM', 'AVG',
        'MIN', 'MAX'
    }

    @staticmethod
    def validate_table_name(
        name: str,
        existing_tables: Optional[List[str]] = None,
        exclude_table: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Valida que un nombre de tabla sea válido.

        Reglas:
        - No puede estar vacío
        - Máximo 100 caracteres
        - Solo letras mayúsculas, números, guiones y guiones bajos
        - No puede ser palabra reservada SQL
        - Debe ser único (si se proporciona lista de existentes)

        Args:
            name: Nombre a validar
            existing_tables: Lista opcional de nombres de tablas existentes
            exclude_table: Nombre a excluir de validación de unicidad (para edición)

        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        # Validar vacío
        if not name or not name.strip():
            return False, "El nombre de la tabla no puede estar vacío"

        # Eliminar espacios
        name = name.strip()

        # Validar longitud
        if len(name) > TableValidator.MAX_TABLE_NAME_LENGTH:
            return False, f"El nombre no puede exceder {TableValidator.MAX_TABLE_NAME_LENGTH} caracteres"

        # Validar formato (mayúsculas, minúsculas, números, guiones, guiones bajos)
        if not re.match(TableValidator.TABLE_NAME_PATTERN, name):
            return False, "El nombre solo puede contener letras (mayúsculas o minúsculas), números, guiones (-) y guiones bajos (_)"

        # Validar no sea palabra reservada
        if name.upper() in TableValidator.RESERVED_NAMES:
            return False, f"'{name}' es una palabra reservada SQL y no puede usarse como nombre de tabla"

        # Validar unicidad (si se proporciona lista)
        if existing_tables:
            # Excluir tabla actual si se está editando
            if exclude_table and name == exclude_table:
                return True, ""

            # Verificar si ya existe
            if name in existing_tables:
                return False, f"Ya existe una tabla con el nombre '{name}'"

        return True, ""

    @staticmethod
    def validate_table_dimensions(rows: int, cols: int) -> Tuple[bool, str]:
        """
        Valida que las dimensiones de tabla estén en rangos permitidos.

        Args:
            rows: Número de filas
            cols: Número de columnas

        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        # Validar filas
        if rows < TableValidator.MIN_ROWS:
            return False, f"La tabla debe tener al menos {TableValidator.MIN_ROWS} fila(s)"

        if rows > TableValidator.MAX_ROWS:
            return False, f"La tabla no puede tener más de {TableValidator.MAX_ROWS} filas"

        # Validar columnas
        if cols < TableValidator.MIN_COLS:
            return False, f"La tabla debe tener al menos {TableValidator.MIN_COLS} columna(s)"

        if cols > TableValidator.MAX_COLS:
            return False, f"La tabla no puede tener más de {TableValidator.MAX_COLS} columnas"

        return True, ""

    @staticmethod
    def validate_table_data(
        table_data: List[List[str]],
        min_filled: int = 1
    ) -> Tuple[bool, str, int]:
        """
        Valida que los datos de tabla tengan al menos N celdas llenas.

        Args:
            table_data: Matriz de datos (lista de listas)
            min_filled: Mínimo de celdas llenas requeridas

        Returns:
            Tuple (is_valid: bool, error_message: str, filled_count: int)
        """
        if not table_data:
            return False, "Los datos de la tabla están vacíos", 0

        # Contar celdas llenas
        filled_count = 0
        for row in table_data:
            if not isinstance(row, list):
                return False, "Formato de datos inválido (debe ser lista de listas)", 0

            for cell in row:
                if cell and str(cell).strip():
                    filled_count += 1

        # Validar mínimo de celdas llenas
        if filled_count < min_filled:
            return False, f"Se requieren al menos {min_filled} celda(s) con datos (encontradas: {filled_count})", filled_count

        return True, "", filled_count

    @staticmethod
    def validate_column_names(
        column_names: List[str],
        num_cols: int
    ) -> Tuple[bool, str]:
        """
        Valida que los nombres de columnas sean válidos.

        Reglas:
        - Debe haber exactamente num_cols nombres
        - No pueden estar todos vacíos
        - No pueden tener duplicados

        Args:
            column_names: Lista de nombres de columnas
            num_cols: Número esperado de columnas

        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        # Validar cantidad
        if len(column_names) != num_cols:
            return False, f"Se esperaban {num_cols} nombres de columnas, se recibieron {len(column_names)}"

        # Validar que no estén todos vacíos
        non_empty = [name for name in column_names if name and name.strip()]
        if not non_empty:
            return False, "Debe proporcionar al menos un nombre de columna"

        # Validar duplicados (solo entre los no vacíos)
        seen = set()
        for name in column_names:
            if name and name.strip():
                name_upper = name.strip().upper()
                if name_upper in seen:
                    return False, f"Nombre de columna duplicado: '{name.strip()}'"
                seen.add(name_upper)

        return True, ""

    @staticmethod
    def sanitize_cell_content(content: str) -> str:
        """
        Limpia y normaliza contenido de celda.

        Operaciones:
        - Convierte a string
        - Elimina espacios al inicio/final
        - Reemplaza múltiples espacios por uno solo
        - Limita longitud a MAX_CELL_LENGTH

        Args:
            content: Contenido a sanitizar

        Returns:
            Contenido sanitizado
        """
        if not content:
            return ""

        # Convertir a string
        content = str(content)

        # Eliminar espacios al inicio/final
        content = content.strip()

        # Reemplazar múltiples espacios consecutivos por uno solo
        content = re.sub(r'\s+', ' ', content)

        # Limitar longitud
        if len(content) > TableValidator.MAX_CELL_LENGTH:
            content = content[:TableValidator.MAX_CELL_LENGTH]
            logger.warning(f"Cell content truncated to {TableValidator.MAX_CELL_LENGTH} characters")

        return content

    @staticmethod
    def sanitize_table_data(table_data: List[List[str]]) -> List[List[str]]:
        """
        Sanitiza todos los datos de una tabla.

        Args:
            table_data: Matriz de datos original

        Returns:
            Matriz de datos sanitizada
        """
        sanitized = []

        for row in table_data:
            sanitized_row = []
            for cell in row:
                sanitized_cell = TableValidator.sanitize_cell_content(cell)
                sanitized_row.append(sanitized_cell)
            sanitized.append(sanitized_row)

        return sanitized

    @staticmethod
    def validate_complete_table_config(
        table_name: str,
        rows: int,
        cols: int,
        column_names: List[str],
        table_data: List[List[str]],
        existing_tables: Optional[List[str]] = None,
        min_filled: int = 1
    ) -> Tuple[bool, List[str]]:
        """
        Validación completa de configuración de tabla.

        Combina todas las validaciones en una sola función.

        Args:
            table_name: Nombre de la tabla
            rows: Número de filas
            cols: Número de columnas
            column_names: Lista de nombres de columnas
            table_data: Matriz de datos
            existing_tables: Lista opcional de tablas existentes
            min_filled: Mínimo de celdas llenas

        Returns:
            Tuple (is_valid: bool, errors: List[str])
        """
        errors = []

        # Validar nombre
        is_valid_name, error_msg = TableValidator.validate_table_name(
            table_name,
            existing_tables
        )
        if not is_valid_name:
            errors.append(f"Nombre: {error_msg}")

        # Validar dimensiones
        is_valid_dims, error_msg = TableValidator.validate_table_dimensions(rows, cols)
        if not is_valid_dims:
            errors.append(f"Dimensiones: {error_msg}")

        # Validar nombres de columnas
        is_valid_cols, error_msg = TableValidator.validate_column_names(column_names, cols)
        if not is_valid_cols:
            errors.append(f"Columnas: {error_msg}")

        # Validar datos
        is_valid_data, error_msg, filled_count = TableValidator.validate_table_data(
            table_data,
            min_filled
        )
        if not is_valid_data:
            errors.append(f"Datos: {error_msg}")

        # Retornar resultado
        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def get_validation_summary(
        table_name: str,
        rows: int,
        cols: int,
        column_names: List[str],
        table_data: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Genera un resumen completo de validación sin detener en errores.

        Útil para mostrar todos los problemas a la vez en la UI.

        Args:
            table_name: Nombre de la tabla
            rows: Número de filas
            cols: Número de columnas
            column_names: Lista de nombres de columnas
            table_data: Matriz de datos

        Returns:
            Dict con resultados de cada validación
        """
        summary = {
            'name': {'valid': True, 'errors': []},
            'dimensions': {'valid': True, 'errors': []},
            'columns': {'valid': True, 'errors': []},
            'data': {'valid': True, 'errors': [], 'filled_count': 0},
            'overall_valid': False
        }

        # Validar nombre
        is_valid, error_msg = TableValidator.validate_table_name(table_name)
        summary['name']['valid'] = is_valid
        if not is_valid:
            summary['name']['errors'].append(error_msg)

        # Validar dimensiones
        is_valid, error_msg = TableValidator.validate_table_dimensions(rows, cols)
        summary['dimensions']['valid'] = is_valid
        if not is_valid:
            summary['dimensions']['errors'].append(error_msg)

        # Validar columnas
        is_valid, error_msg = TableValidator.validate_column_names(column_names, cols)
        summary['columns']['valid'] = is_valid
        if not is_valid:
            summary['columns']['errors'].append(error_msg)

        # Validar datos
        is_valid, error_msg, filled_count = TableValidator.validate_table_data(table_data)
        summary['data']['valid'] = is_valid
        summary['data']['filled_count'] = filled_count
        if not is_valid:
            summary['data']['errors'].append(error_msg)

        # Validación general
        summary['overall_valid'] = (
            summary['name']['valid'] and
            summary['dimensions']['valid'] and
            summary['columns']['valid'] and
            summary['data']['valid']
        )

        return summary
