"""
Templates para generación de prompts de IA para tablas.

Este módulo genera prompts personalizados que se copian a ChatGPT, Claude u otras IAs
para obtener JSON estructurado con datos de tablas.

ACTUALIZADO: Ahora usa configuración manual de columnas (sin auto-detección)
"""
import json
from typing import Dict


class AITablePromptTemplate:
    """Generador de prompts para creación de tablas con IA."""

    MAIN_TEMPLATE = """Genera un JSON para crear una tabla en Widget Sidebar siguiendo EXACTAMENTE esta estructura:

{{
  "table_config": {{
    "table_name": "{table_name}",
    "category_id": {category_id},
    "tags": {tags_json}
  }},
  "table_structure": {{
    "columns": [
{columns_definition}
    ]
  }},
  "table_data": [
    {data_example}
  ]
}}

CONFIGURACIÓN DE LA TABLA:
- Nombre de tabla: {table_name}
- Categoría: {category_name} (ID: {category_id})
- Número de filas esperado: {expected_rows}
- Número de columnas: {expected_cols}
- Tags: {tags_str}

ESTRUCTURA DE COLUMNAS REQUERIDA:
{columns_details}

CONTEXTO DEL USUARIO:
{user_context}

INSTRUCCIONES CRÍTICAS - SIGUE EXACTAMENTE:

1. ESTRUCTURA JSON:
   - Usa el esquema exacto mostrado arriba
   - NO agregues campos adicionales
   - NO omitas campos requeridos
   - NO agregues comentarios en el JSON

2. COLUMNAS:
   - Genera EXACTAMENTE {expected_cols} columnas
   - Usa los nombres de columna especificados arriba
   - Respeta los tipos de cada columna (TEXT o URL)
   - Las columnas marcadas como is_sensitive: true se cifrarán automáticamente (no agregues prefijos como "secret_")
   - Las columnas marcadas como URL deben contener URLs válidas
   - IMPORTANTE: Genera datos reales según el CONTEXTO DEL USUARIO, no inventes formatos de secretos

3. DATOS:
   - Genera EXACTAMENTE {expected_rows} filas de datos
   - Cada fila debe tener EXACTAMENTE {expected_cols} valores
   - Los datos deben ser coherentes entre sí y seguir el CONTEXTO DEL USUARIO
   - Los datos deben ser realistas y útiles según lo solicitado
   - Todos los valores deben ser strings
   - NO agregues prefijos como "secret_", "api_key_", etc. a menos que el contexto lo requiera explícitamente

4. TIPOS DE DATOS SEGÚN COLUMNA:
{column_type_rules}

5. VALIDACIÓN:
   - Verifica que todas las filas tengan el mismo número de columnas
   - Verifica que no haya valores null o undefined
   - Verifica que el JSON sea válido (sin comas finales, etc.)

EJEMPLO DE FORMATO DE UNA FILA:
{data_example}

IMPORTANTE: Responde SOLO con el JSON válido, sin explicaciones antes o después."""

    @staticmethod
    def generate(config: Dict) -> str:
        """
        Genera un prompt personalizado basado en la configuración.

        Args:
            config: Diccionario con configuración del prompt (AITablePromptConfig)

        Returns:
            String con el prompt completo y personalizado
        """
        # Tags
        tags_json = json.dumps(config.get('tags', []), ensure_ascii=False)
        tags_str = ', '.join(config.get('tags', [])) if config.get('tags') else 'ninguno'

        # Obtener configuración de columnas
        columns_config = config.get('columns_config', [])
        expected_cols = config.get('expected_cols', len(columns_config))

        # Generar definición de columnas para el JSON
        columns_definition = []
        for i, col in enumerate(columns_config):
            col_type = "URL" if col.get('is_url', False) else "TEXT"
            is_sensitive = str(col.get('is_sensitive', False)).lower()

            col_def = f"""      {{
        "name": "{col['name']}",
        "type": "{col_type}",
        "is_sensitive": {is_sensitive},
        "description": "Descripción de {col['name']}"
      }}"""
            if i < len(columns_config) - 1:
                col_def += ","
            columns_definition.append(col_def)

        columns_definition_str = "\n".join(columns_definition)

        # Generar detalles de columnas
        columns_details = []
        for i, col in enumerate(columns_config):
            col_name = col['name']
            col_type = "URL" if col.get('is_url', False) else "TEXT"
            is_sensitive = col.get('is_sensitive', False)

            details = f"  Columna {i+1}: '{col_name}'"
            details += f" (Tipo: {col_type}"

            if is_sensitive:
                details += ", SENSIBLE - debe contener datos secretos"
            details += ")"

            columns_details.append(details)

        columns_details_str = "\n".join(columns_details)

        # Generar reglas de tipo de datos por columna
        column_type_rules = []
        for i, col in enumerate(columns_config):
            col_name = col['name']
            if col.get('is_url', False):
                rule = f"   - '{col_name}': URLs válidas (ej: https://example.com)"
            elif col.get('is_sensitive', False):
                rule = f"   - '{col_name}': Datos apropiados para este campo (se marcarán como sensibles y se cifrarán)"
            else:
                rule = f"   - '{col_name}': Texto apropiado para este campo"

            column_type_rules.append(rule)

        column_type_rules_str = "\n".join(column_type_rules)

        # Generar ejemplo de fila
        data_example_values = []
        for col in columns_config:
            if col.get('is_url', False):
                data_example_values.append('"https://example.com"')
            else:
                # Para columnas sensibles y normales, usar el nombre como guía
                data_example_values.append(f'"{col["name"]} ejemplo"')

        data_example = "[" + ", ".join(data_example_values) + "]"

        # Formatear el prompt con todos los valores
        prompt = AITablePromptTemplate.MAIN_TEMPLATE.format(
            table_name=config.get('table_name', 'MiTabla'),
            category_id=config.get('category_id', 1),
            category_name=config.get('category_name', 'General'),
            tags_json=tags_json,
            tags_str=tags_str,
            expected_rows=config.get('expected_rows', 10),
            expected_cols=expected_cols,
            columns_definition=columns_definition_str,
            columns_details=columns_details_str,
            column_type_rules=column_type_rules_str,
            data_example=data_example,
            user_context=config.get('user_context', '')
        )

        return prompt

    @staticmethod
    def generate_schema_only() -> str:
        """
        Genera solo el esquema JSON de ejemplo.

        Returns:
            String con esquema JSON básico
        """
        return """{
  "table_config": {
    "table_name": "NOMBRE_TABLA",
    "category_id": ID_CATEGORIA,
    "tags": ["tag1", "tag2"]
  },
  "table_structure": {
    "columns": [
      {
        "name": "NOMBRE_COLUMNA",
        "type": "TEXT|URL",
        "is_sensitive": false,
        "description": "Descripción de la columna"
      }
    ]
  },
  "table_data": [
    ["valor_col1", "valor_col2", "..."]
  ]
}"""
