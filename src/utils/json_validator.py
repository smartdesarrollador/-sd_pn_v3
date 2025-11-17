"""
Validador de JSON para bulk import usando JSON Schema.

Este módulo valida que el JSON importado cumpla con:
1. Sintaxis JSON válida
2. Estructura esperada (schema)
3. Validaciones de negocio (categoría existe, tipos válidos, etc.)
"""
import json
import logging
from typing import Dict, Any, List

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema no está instalado. Validación limitada disponible.")

from models.bulk_item_data import ValidationResult, BulkItemData, BulkItemDefaults

logger = logging.getLogger(__name__)


class BulkJSONValidator:
    """
    Validador de estructura JSON para bulk import de items.

    Utiliza JSON Schema para validación estructural y agrega
    validaciones adicionales de negocio.
    """

    # Schema JSON completo para validación
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["category_id", "items"],
        "properties": {
            "category_id": {
                "type": "integer",
                "minimum": 1,
                "description": "ID de categoría existente en BD"
            },
            "defaults": {
                "type": "object",
                "description": "Valores por defecto para todos los items",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["TEXT", "URL", "CODE", "PATH"]
                    },
                    "tags": {"type": "string"},
                    "is_favorite": {"type": "integer", "enum": [0, 1]},
                    "is_sensitive": {"type": "integer", "enum": [0, 1]},
                    "is_list": {"type": "integer", "enum": [0, 1]},
                    "list_group": {"type": "string"},
                    "icon": {"type": "string"},
                    "color": {
                        "type": "string",
                        "pattern": "^#[0-9A-Fa-f]{6}$"
                    },
                    "description": {"type": "string"},
                    "working_dir": {"type": "string"},
                    "badge": {"type": "string"}
                },
                "additionalProperties": False
            },
            "items": {
                "type": "array",
                "minItems": 1,
                "maxItems": 500,
                "items": {
                    "type": "object",
                    "required": ["label", "content"],
                    "properties": {
                        "label": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 200
                        },
                        "content": {
                            "type": "string",
                            "minLength": 1
                        },
                        "description": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["TEXT", "URL", "CODE", "PATH"]
                        },
                        "tags": {"type": "string"},
                        "icon": {"type": "string"},
                        "color": {
                            "type": "string",
                            "pattern": "^#[0-9A-Fa-f]{6}$"
                        },
                        "is_favorite": {"type": "integer", "enum": [0, 1]},
                        "is_sensitive": {"type": "integer", "enum": [0, 1]},
                        "is_list": {"type": "integer", "enum": [0, 1]},
                        "list_group": {"type": "string"},
                        "orden_lista": {"type": "integer", "minimum": 0},
                        "working_dir": {"type": "string"},
                        "badge": {"type": "string"}
                    },
                    "additionalProperties": False
                }
            }
        },
        "additionalProperties": False
    }

    @staticmethod
    def validate_json_string(json_str: str) -> ValidationResult:
        """
        Valida un string JSON completo.

        Realiza validación en 3 niveles:
        1. Sintaxis JSON válida
        2. Estructura contra schema
        3. Validaciones de negocio

        Args:
            json_str: String con el JSON a validar

        Returns:
            ValidationResult con resultado de la validación
        """
        result = ValidationResult(is_valid=True)

        # Nivel 1: Validar sintaxis JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            result.add_error(f"JSON mal formado: {str(e)}")
            logger.error(f"Error parsing JSON: {e}")
            return result

        # Nivel 2: Validar contra schema (solo si jsonschema está disponible)
        if JSONSCHEMA_AVAILABLE:
            try:
                validate(instance=data, schema=BulkJSONValidator.SCHEMA)
            except ValidationError as e:
                # Hacer el mensaje de error más legible
                error_path = " -> ".join(str(p) for p in e.path) if e.path else "raíz"
                result.add_error(f"Error en {error_path}: {e.message}")
                logger.error(f"Schema validation error: {e.message}")
                return result
        else:
            # Validación básica sin jsonschema
            basic_errors = BulkJSONValidator._basic_validation(data)
            for error in basic_errors:
                result.add_error(error)
            if result.errors:
                return result

        # Nivel 3: Validaciones adicionales de negocio
        BulkJSONValidator._business_validations(data, result)

        # Contar items
        result.items_count = len(data.get('items', []))

        logger.info(f"JSON validation {'passed' if result.is_valid else 'failed'} - {result.items_count} items")

        return result

    @staticmethod
    def _basic_validation(data: Dict[str, Any]) -> List[str]:
        """
        Validación básica cuando jsonschema no está disponible.

        Args:
            data: Diccionario parseado del JSON

        Returns:
            Lista de errores encontrados
        """
        errors = []

        # Campos requeridos
        if 'category_id' not in data:
            errors.append("Campo requerido 'category_id' no encontrado")
        elif not isinstance(data['category_id'], int) or data['category_id'] < 1:
            errors.append("'category_id' debe ser un entero >= 1")

        if 'items' not in data:
            errors.append("Campo requerido 'items' no encontrado")
        elif not isinstance(data['items'], list):
            errors.append("'items' debe ser un array")
        elif len(data['items']) == 0:
            errors.append("'items' no puede estar vacío")
        elif len(data['items']) > 500:
            errors.append(f"'items' tiene {len(data['items'])} elementos (máximo: 500)")

        # Validar cada item
        if isinstance(data.get('items'), list):
            for i, item in enumerate(data['items']):
                if not isinstance(item, dict):
                    errors.append(f"Item {i} no es un objeto")
                    continue

                if 'label' not in item:
                    errors.append(f"Item {i}: campo 'label' requerido")
                elif not isinstance(item['label'], str) or not item['label'].strip():
                    errors.append(f"Item {i}: 'label' debe ser un string no vacío")

                if 'content' not in item:
                    errors.append(f"Item {i}: campo 'content' requerido")
                elif not isinstance(item['content'], str) or not item['content'].strip():
                    errors.append(f"Item {i}: 'content' debe ser un string no vacío")

        return errors

    @staticmethod
    def _business_validations(data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validaciones de negocio adicionales.

        Args:
            data: Diccionario parseado del JSON
            result: ValidationResult donde agregar errores/warnings
        """
        # Validar defaults si existe
        if 'defaults' in data:
            defaults_dict = data['defaults']

            # Warning si defaults está vacío
            if not defaults_dict:
                result.add_warning("'defaults' está vacío, los items usarán valores por defecto del sistema")

        # Detectar labels duplicados
        items = data.get('items', [])
        labels = [item.get('label', '') for item in items]
        duplicates = [label for label in set(labels) if labels.count(label) > 1 and label]

        if duplicates:
            result.add_warning(
                f"Labels duplicados encontrados: {', '.join(duplicates[:5])}..."
                if len(duplicates) > 5 else f"Labels duplicados: {', '.join(duplicates)}"
            )

        # Validar cada item con BulkItemData
        for i, item_dict in enumerate(items):
            try:
                # Crear instancia temporal para validar
                item = BulkItemData(
                    label=item_dict.get('label', ''),
                    content=item_dict.get('content', ''),
                    type=item_dict.get('type', 'TEXT'),
                    tags=item_dict.get('tags', ''),
                    description=item_dict.get('description'),
                    icon=item_dict.get('icon'),
                    color=item_dict.get('color'),
                    is_favorite=item_dict.get('is_favorite', 0),
                    is_sensitive=item_dict.get('is_sensitive', 0),
                    is_list=item_dict.get('is_list', 0),
                    list_group=item_dict.get('list_group'),
                    orden_lista=item_dict.get('orden_lista'),
                    working_dir=item_dict.get('working_dir'),
                    badge=item_dict.get('badge')
                )

                # Validar item
                item_errors = item.validate()
                for error in item_errors:
                    result.add_error(f"Item {i} ({item.label}): {error}")

            except Exception as e:
                result.add_error(f"Item {i}: Error al validar - {str(e)}")

        # Warning si hay muchos items sensibles
        sensitive_count = sum(1 for item in items if item.get('is_sensitive', 0) == 1)
        if sensitive_count > 0:
            result.add_warning(f"{sensitive_count} items marcados como sensibles (serán encriptados)")

        # Warning si hay muchos items
        if len(items) > 100:
            result.add_warning(f"Importando {len(items)} items - puede tomar varios segundos")

    @staticmethod
    def validate_category_exists(category_id: int, db_manager) -> bool:
        """
        Valida que una categoría existe en la BD.

        Args:
            category_id: ID de la categoría
            db_manager: Instancia de DBManager

        Returns:
            True si existe, False si no
        """
        try:
            category = db_manager.get_category_by_id(category_id)
            return category is not None
        except Exception as e:
            logger.error(f"Error checking category existence: {e}")
            return False

    @staticmethod
    def quick_validate(json_str: str) -> bool:
        """
        Validación rápida solo de sintaxis JSON.

        Útil para feedback en tiempo real mientras el usuario escribe.

        Args:
            json_str: String con JSON

        Returns:
            True si es JSON válido sintácticamente
        """
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False
