"""
Validador de JSON para tablas generadas por IA.

Valida que el JSON tenga la estructura correcta y datos coherentes.
"""
import json
import logging
from typing import Dict, Any

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available, using basic validation")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.ai_table_data import TableValidationResult

logger = logging.getLogger(__name__)


class AITableJSONValidator:
    """Validador de estructura JSON para tablas de IA."""

    # JSON Schema para validación
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["table_config", "table_structure", "table_data"],
        "properties": {
            "table_config": {
                "type": "object",
                "required": ["table_name", "category_id"],
                "properties": {
                    "table_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "category_id": {"type": "integer", "minimum": 1},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "auto_detect_sensitive": {"type": "boolean"},
                    "auto_detect_urls": {"type": "boolean"}
                }
            },
            "table_structure": {
                "type": "object",
                "required": ["columns"],
                "properties": {
                    "columns": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1, "maxLength": 50},
                                "type": {"enum": ["TEXT", "URL"]},
                                "is_sensitive": {"type": "boolean"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "table_data": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "items": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }

    @staticmethod
    def validate_json_string(json_str: str) -> TableValidationResult:
        """
        Valida string JSON de tabla.

        Args:
            json_str: String con JSON a validar

        Returns:
            TableValidationResult con resultado de validación

        Example:
            >>> json_str = '{"table_config": {...}, ...}'
            >>> result = AITableJSONValidator.validate_json_string(json_str)
            >>> if result.is_valid:
            ...     print("JSON válido!")
        """
        result = TableValidationResult(is_valid=False)

        # 1. Validar syntax JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            error_msg = f"JSON inválido: {str(e)}"
            result.errors.append(error_msg)
            logger.error(f"JSON parse error: {e}")
            return result

        # 2. Validar contra schema (si jsonschema está disponible)
        if JSONSCHEMA_AVAILABLE:
            try:
                validate(instance=data, schema=AITableJSONValidator.SCHEMA)
            except ValidationError as e:
                error_msg = f"Estructura inválida: {e.message}"
                result.errors.append(error_msg)
                logger.error(f"Schema validation error: {e.message}")
                return result
        else:
            # Validación básica manual
            validation_errors = AITableJSONValidator._basic_validation(data)
            if validation_errors:
                result.errors.extend(validation_errors)
                return result

        # 3. Validaciones adicionales
        try:
            # Verificar que todas las filas tengan el mismo número de columnas
            num_cols = len(data['table_structure']['columns'])
            for i, row in enumerate(data['table_data']):
                if len(row) != num_cols:
                    result.errors.append(
                        f"Fila {i+1} tiene {len(row)} columnas, "
                        f"esperadas {num_cols}"
                    )

            if result.errors:
                return result

            # Dimensiones
            rows_count = len(data['table_data'])
            result.dimensions = {
                'rows': rows_count,
                'cols': num_cols
            }

            # Warnings opcionales
            if num_cols > 10:
                result.warnings.append(
                    f"Tabla tiene {num_cols} columnas (muchas columnas pueden "
                    "dificultar la visualización)"
                )

            if rows_count > 50:
                result.warnings.append(
                    f"Tabla tiene {rows_count} filas (puede tardar en crearse)"
                )

            # Advertencia si hay muchas celdas vacías
            empty_cells = sum(
                1 for row in data['table_data']
                for cell in row
                if not cell or not str(cell).strip()
            )
            total_cells = rows_count * num_cols
            empty_percentage = (empty_cells / total_cells * 100) if total_cells > 0 else 0

            if empty_percentage > 30:
                result.warnings.append(
                    f"{empty_percentage:.1f}% de celdas vacías "
                    "(considera reducir filas/columnas)"
                )

            # Validación exitosa
            result.is_valid = True
            logger.info(f"JSON validated successfully: {rows_count}×{num_cols} table")

        except Exception as e:
            result.errors.append(f"Error en validación adicional: {str(e)}")
            logger.error(f"Additional validation error: {e}", exc_info=True)

        return result

    @staticmethod
    def _basic_validation(data: Dict[str, Any]) -> list:
        """
        Validación básica manual (cuando jsonschema no está disponible).

        Args:
            data: Diccionario parseado del JSON

        Returns:
            Lista de errores (vacía si es válido)
        """
        errors = []

        # Verificar campos requeridos de primer nivel
        if 'table_config' not in data:
            errors.append("Falta campo requerido: 'table_config'")
        if 'table_structure' not in data:
            errors.append("Falta campo requerido: 'table_structure'")
        if 'table_data' not in data:
            errors.append("Falta campo requerido: 'table_data'")

        if errors:
            return errors

        # Validar table_config
        config = data['table_config']
        if 'table_name' not in config or not config['table_name']:
            errors.append("table_config.table_name es requerido")
        if 'category_id' not in config or not isinstance(config['category_id'], int):
            errors.append("table_config.category_id debe ser un entero")

        # Validar table_structure
        structure = data['table_structure']
        if 'columns' not in structure:
            errors.append("table_structure.columns es requerido")
        elif not isinstance(structure['columns'], list):
            errors.append("table_structure.columns debe ser un array")
        elif len(structure['columns']) == 0:
            errors.append("table_structure.columns no puede estar vacío")
        elif len(structure['columns']) > 20:
            errors.append("table_structure.columns: máximo 20 columnas")
        else:
            # Validar cada columna
            for i, col in enumerate(structure['columns']):
                if not isinstance(col, dict):
                    errors.append(f"Columna {i+1} debe ser un objeto")
                    continue
                if 'name' not in col or not col['name']:
                    errors.append(f"Columna {i+1}: 'name' es requerido")
                if 'type' in col and col['type'] not in ('TEXT', 'URL'):
                    errors.append(f"Columna {i+1}: type debe ser 'TEXT' o 'URL'")

        # Validar table_data
        table_data = data['table_data']
        if not isinstance(table_data, list):
            errors.append("table_data debe ser un array")
        elif len(table_data) == 0:
            errors.append("table_data no puede estar vacío")
        elif len(table_data) > 100:
            errors.append("table_data: máximo 100 filas")
        else:
            # Validar que cada fila sea un array
            for i, row in enumerate(table_data):
                if not isinstance(row, list):
                    errors.append(f"Fila {i+1} debe ser un array")

        return errors

    @staticmethod
    def get_validation_summary(result: TableValidationResult) -> str:
        """
        Genera resumen legible de validación.

        Args:
            result: Resultado de validación

        Returns:
            String con resumen formateado
        """
        if result.is_valid:
            summary = "[OK] JSON VALIDO\n\n"
            if result.dimensions:
                summary += f"Dimensiones: {result.dimensions['rows']} filas × {result.dimensions['cols']} columnas\n"

            if result.warnings:
                summary += f"\n[!] Advertencias ({len(result.warnings)}):\n"
                for warning in result.warnings:
                    summary += f"  - {warning}\n"
        else:
            summary = "[ERROR] JSON INVALIDO\n\n"
            summary += f"Errores encontrados ({len(result.errors)}):\n"
            for error in result.errors:
                summary += f"  - {error}\n"

        return summary
