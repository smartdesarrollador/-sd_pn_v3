"""
Manager para creación de tablas con IA.

Este módulo coordina todo el proceso de creación de tablas mediante IA:
- Generación de prompts
- Validación de JSON
- Parseo de datos
- Auto-detección de tipos
- Creación en base de datos
"""
import json
import logging
from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.ai_table_data import (
    AITableData, TableConfigData, TableStructureData,
    TableColumnConfig, AITablePromptConfig, TableValidationResult
)
from utils.ai_table_prompt_templates import AITablePromptTemplate
from utils.ai_table_json_validator import AITableJSONValidator
from utils.column_type_detector import ColumnTypeDetector
from controllers.table_controller import TableController
from database.db_manager import DBManager

logger = logging.getLogger(__name__)


class AITableManager:
    """
    Manager para creación de tablas mediante IA.

    Coordina el flujo completo:
    1. Generación de prompt personalizado
    2. Validación de JSON recibido
    3. Parseo y auto-detección de tipos
    4. Creación en base de datos
    """

    def __init__(self, db_manager: DBManager):
        """
        Inicializa el manager.

        Args:
            db_manager: Instancia de DBManager para acceso a BD
        """
        self.db = db_manager
        self.table_controller = TableController(db_manager)
        self.validator = AITableJSONValidator()
        self.detector = ColumnTypeDetector()

        logger.info("AITableManager initialized")

    # ========== GENERACIÓN DE PROMPTS ==========

    def generate_prompt(self, config: AITablePromptConfig) -> str:
        """
        Genera prompt personalizado para IA.

        Args:
            config: Configuración del prompt (AITablePromptConfig)

        Returns:
            String con prompt formateado listo para copiar

        Example:
            >>> config = AITablePromptConfig(
            ...     table_name="CONTACTOS",
            ...     category_id=5,
            ...     category_name="Trabajo",
            ...     user_context="Genera 10 contactos",
            ...     expected_rows=10
            ... )
            >>> prompt = manager.generate_prompt(config)
        """
        config_dict = {
            'table_name': config.table_name,
            'category_id': config.category_id,
            'category_name': config.category_name,
            'user_context': config.user_context,
            'expected_rows': config.expected_rows,
            'tags': config.tags,
            'auto_detect_sensitive': config.auto_detect_sensitive,
            'auto_detect_urls': config.auto_detect_urls
        }

        prompt = AITablePromptTemplate.generate(config_dict)
        logger.info(
            f"Generated prompt for table '{config.table_name}' "
            f"({config.expected_rows} rows expected)"
        )
        return prompt

    # ========== VALIDACIÓN Y PARSEO ==========

    def validate_json(self, json_str: str) -> TableValidationResult:
        """
        Valida JSON de tabla.

        Args:
            json_str: String JSON a validar

        Returns:
            TableValidationResult con resultado y detalles

        Example:
            >>> json_str = '{"table_config": {...}, ...}'
            >>> result = manager.validate_json(json_str)
            >>> if result.is_valid:
            ...     print("JSON válido!")
        """
        logger.debug("Validating JSON...")
        result = self.validator.validate_json_string(json_str)

        if result.is_valid:
            logger.info(f"JSON validated successfully: {result.dimensions}")
        else:
            logger.warning(f"JSON validation failed: {len(result.errors)} errors")

        return result

    def parse_json(self, json_str: str) -> Tuple[AITableData, List[str]]:
        """
        Parsea JSON y retorna objeto AITableData.

        Proceso:
        1. Parse del JSON
        2. Creación de objetos tipados
        3. Auto-detección de tipos (si habilitada)
        4. Validación de consistencia

        Args:
            json_str: String JSON válido

        Returns:
            Tuple (AITableData o None, lista de errores)

        Example:
            >>> ai_table, errors = manager.parse_json(json_str)
            >>> if not errors:
            ...     print(f"Table: {ai_table.rows_count}x{ai_table.cols_count}")
        """
        errors = []

        try:
            # Parse JSON
            data = json.loads(json_str)
            logger.debug("JSON parsed successfully")

            # Parsear table_config
            config_dict = data['table_config']
            table_config = TableConfigData(
                table_name=config_dict['table_name'],
                category_id=config_dict['category_id'],
                tags=config_dict.get('tags', []),
                auto_detect_sensitive=config_dict.get('auto_detect_sensitive', True),
                auto_detect_urls=config_dict.get('auto_detect_urls', True)
            )

            # Parsear columns
            columns = []
            for col_dict in data['table_structure']['columns']:
                column = TableColumnConfig(
                    name=col_dict['name'],
                    type=col_dict.get('type', 'TEXT'),
                    is_sensitive=col_dict.get('is_sensitive', False),
                    description=col_dict.get('description')
                )
                columns.append(column)

            table_structure = TableStructureData(columns=columns)

            # Parsear table_data
            table_data = data['table_data']

            # NOTA: Auto-detección eliminada - ahora se usa configuración manual de columnas
            # Los tipos de columna (URL, sensible) vienen definidos en el JSON
            logger.info("Using manual column configuration (auto-detection disabled)")

            # Crear objeto completo
            ai_table = AITableData(
                table_config=table_config,
                table_structure=table_structure,
                table_data=table_data
            )

            # Validar consistencia de datos
            is_consistent, consistency_errors = ai_table.validate_data_consistency()
            if not is_consistent:
                errors.extend(consistency_errors)
                logger.error(f"Data consistency errors: {consistency_errors}")
                return None, errors

            logger.info(
                f"Parsed table successfully: {ai_table.rows_count}x{ai_table.cols_count}, "
                f"{ai_table.filled_cells_count} filled cells "
                f"({ai_table.get_fill_percentage():.1f}%)"
            )

            return ai_table, errors

        except KeyError as e:
            error_msg = f"Campo requerido faltante: {str(e)}"
            logger.error(f"Parse error - missing field: {e}")
            errors.append(error_msg)
            return None, errors

        except Exception as e:
            error_msg = f"Error al parsear JSON: {str(e)}"
            logger.error(f"Parse error: {e}", exc_info=True)
            errors.append(error_msg)
            return None, errors

    # ========== CREACIÓN EN BASE DE DATOS ==========

    def create_table_from_ai(self, ai_table: AITableData) -> Dict[str, Any]:
        """
        Crea tabla en BD desde objeto AITableData.

        Proceso:
        1. Validación de nombre único
        2. Preparación de datos
        3. Creación mediante TableController
        4. Logging de resultado

        Args:
            ai_table: Objeto con datos completos de tabla

        Returns:
            Dict con resultado:
                - success: bool
                - items_created: int
                - table_name: str
                - errors: List[str]
                - filled_cells: int

        Example:
            >>> result = manager.create_table_from_ai(ai_table)
            >>> if result['success']:
            ...     print(f"Created {result['items_created']} items")
        """
        try:
            logger.info(
                f"Creating table '{ai_table.table_config.table_name}' "
                f"with {ai_table.rows_count}x{ai_table.cols_count} dimensions"
            )

            # Preparar datos para TableController
            column_names = ai_table.table_structure.get_column_names()
            sensitive_columns = ai_table.table_structure.get_sensitive_indices()
            url_columns = ai_table.table_structure.get_url_indices()

            logger.debug(
                f"Column configuration: "
                f"{len(column_names)} total, "
                f"{len(sensitive_columns)} sensitive, "
                f"{len(url_columns)} URL"
            )

            # Crear tabla usando TableController
            result = self.table_controller.create_table(
                category_id=ai_table.table_config.category_id,
                table_name=ai_table.table_config.table_name,
                table_data=ai_table.table_data,
                column_names=column_names,
                tags=ai_table.table_config.tags,
                sensitive_columns=sensitive_columns,
                url_columns=url_columns
            )

            # Agregar información adicional al resultado
            if result.get('success'):
                result['filled_cells'] = ai_table.filled_cells_count
                result['fill_percentage'] = ai_table.get_fill_percentage()

                logger.info(
                    f"Table '{ai_table.table_config.table_name}' created successfully: "
                    f"{result['items_created']} items, "
                    f"{ai_table.filled_cells_count} filled cells "
                    f"({ai_table.get_fill_percentage():.1f}%)"
                )

            return result

        except Exception as e:
            error_msg = f"Error creating table from AI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'errors': [error_msg],
                'items_created': 0,
                'table_name': ai_table.table_config.table_name,
                'filled_cells': 0
            }

    # ========== UTILIDADES ==========

    def get_example_json(self) -> str:
        """
        Retorna JSON de ejemplo para mostrar al usuario.

        Returns:
            String con JSON formateado
        """
        return AITablePromptTemplate.get_example_json()

    def get_validation_summary(self, result: TableValidationResult) -> str:
        """
        Genera resumen legible de validación.

        Args:
            result: Resultado de validación

        Returns:
            String con resumen formateado
        """
        return self.validator.get_validation_summary(result)
