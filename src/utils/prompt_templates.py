"""
Templates para generación de prompts de IA.

Este módulo genera prompts personalizados que se le dan a modelos de IA
(ChatGPT, Claude, etc.) para que generen JSON con items en el formato esperado.
"""
from typing import Dict, Any


class PromptTemplate:
    """
    Generador de prompts personalizados para IAs.

    Los prompts incluyen:
    - Estructura JSON exacta esperada
    - Contexto de la categoría y configuración
    - Reglas y restricciones
    - Contexto del usuario (qué necesita)
    """

    # Template principal para generación de items
    MAIN_TEMPLATE = """Genera un archivo JSON para Widget Sidebar siguiendo EXACTAMENTE esta estructura:

{{
  "category_id": {category_id},
  "defaults": {{
    "type": "{item_type}",
    "tags": "{tags}",
    "is_favorite": {is_favorite},
    "is_sensitive": {is_sensitive}{list_defaults}{optional_defaults}
  }},
  "items": [
    {{
      "label": "nombre corto descriptivo del paso",
      "content": "comando/url/texto completo aquí",
      "description": "descripción opcional del item"
    }},
    {{
      "label": "otro paso",
      "content": "otro comando/contenido",
      "description": "otra descripción"
    }}
  ]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXTO DE LA TAREA:
📁 Categoría: {category_name} (ID: {category_id})
📝 Tipo de items: {item_type} ({item_type_desc})
🏷️ Tags por defecto: {tags_display}
⭐ Favoritos por defecto: {is_favorite_text}
🔒 Sensibles por defecto: {is_sensitive_text}{list_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGLAS IMPORTANTES:

1. ESTRUCTURA:
   - Cada item DEBE tener "label" (max 200 caracteres) y "content" (requerido)
   - El "label" debe ser descriptivo pero conciso
   - El "content" debe ser el comando/url/texto completo y funcional

2. PERSONALIZACIÓN POR ITEM:
   - Puedes sobreescribir "type", "tags", "is_favorite", "is_sensitive" en items individuales
   - Ejemplo: si un item específico necesita ser CODE aunque el default sea TEXT
   - Los valores individuales tienen prioridad sobre "defaults"{list_rules}

3. CANTIDAD:
   - Genera entre 1 y 50 items según la complejidad del contexto
   - Para tareas simples: 5-10 items
   - Para tareas complejas: 15-30 items
   - Para flujos completos: 30-50 items

4. CALIDAD DEL CONTENIDO:
   - Para tipo CODE: comandos funcionales y completos (no pseudocódigo)
   - Para tipo URL: URLs completas y válidas (https://...)
   - Para tipo PATH: rutas absolutas o relativas válidas
   - Para tipo TEXT: texto útil y relevante

5. FORMATO JSON:
   - NO agregues comentarios en el JSON (no es válido)
   - NO agregues texto antes o después del JSON
   - USA comillas dobles, NO comillas simples
   - Escapa caracteres especiales correctamente (\\n, \\t, \\", etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LO QUE EL USUARIO NECESITA:
{user_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional antes o después.
El JSON debe empezar con {{ y terminar con }}.
"""

    # Template alternativo más simple para usuarios básicos
    SIMPLE_TEMPLATE = """Genera un JSON con pasos/items para "{category_name}".

Formato:
{{
  "category_id": {category_id},
  "items": [
    {{"label": "nombre paso 1", "content": "contenido paso 1"}},
    {{"label": "nombre paso 2", "content": "contenido paso 2"}}
  ]
}}

Lo que necesito:
{user_context}

Responde solo con el JSON, sin explicaciones.
"""

    # Descripciones de tipos de items
    ITEM_TYPE_DESCRIPTIONS = {
        'TEXT': 'Texto plano, notas, descripciones generales',
        'URL': 'Enlaces web, URLs de documentación, recursos online',
        'CODE': 'Comandos de terminal, scripts, código ejecutable',
        'PATH': 'Rutas de archivos o directorios en el sistema'
    }

    # Ejemplos por tipo
    ITEM_TYPE_EXAMPLES = {
        'TEXT': 'Ejemplo: "label": "Nota importante", "content": "Recordar hacer backup antes de deploy"',
        'URL': 'Ejemplo: "label": "Docs React", "content": "https://react.dev/learn"',
        'CODE': 'Ejemplo: "label": "Instalar deps", "content": "npm install"',
        'PATH': 'Ejemplo: "label": "Config nginx", "content": "/etc/nginx/nginx.conf"'
    }

    @staticmethod
    def generate(config: Dict[str, Any], simple: bool = False) -> str:
        """
        Genera prompt personalizado basado en configuración.

        Args:
            config: Diccionario con configuración del wizard
                - category_id: int
                - category_name: str
                - item_type: str (TEXT, URL, CODE, PATH)
                - tags: str
                - is_favorite: int (0 o 1)
                - is_sensitive: int (0 o 1)
                - user_context: str (opcional)
                - icon: str (opcional)
                - color: str (opcional)
                - working_dir: str (opcional)
            simple: Si True, usa template simplificado

        Returns:
            String con el prompt generado
        """
        # Usar template simple si se solicita
        if simple:
            return PromptTemplate.SIMPLE_TEMPLATE.format(
                category_id=config['category_id'],
                category_name=config['category_name'],
                user_context=config.get('user_context', 'No especificado')
            )

        # Preparar valores con defaults
        item_type = config.get('item_type', 'TEXT')
        tags = config.get('tags', '')
        is_favorite = config.get('is_favorite', 0)
        is_sensitive = config.get('is_sensitive', 0)
        is_list = config.get('is_list', 0)
        list_group = config.get('list_group', '')
        user_context = config.get('user_context', 'No especificado')

        # Descripción del tipo
        item_type_desc = PromptTemplate.ITEM_TYPE_DESCRIPTIONS.get(item_type, 'Tipo genérico')

        # Formatear tags para display
        tags_display = f'"{tags}"' if tags else 'Ninguno'

        # Textos legibles para booleans
        is_favorite_text = 'SÍ - Los items se marcarán como favoritos automáticamente' if is_favorite else 'NO'
        is_sensitive_text = (
            'SÍ - Los items se encriptarán (usar para contraseñas, API keys, etc.)'
            if is_sensitive
            else 'NO'
        )

        # Configurar secciones de lista
        list_defaults = ''
        list_context = ''
        list_rules = ''

        if is_list == 1:
            list_defaults = f',\n    "is_list": 1,\n    "list_group": "{list_group}"'
            list_context = f'\n📝 Lista secuencial: SÍ - Grupo "{list_group}" (los items se crearán en orden)'
            list_rules = """
   - IMPORTANTE: Como se creará una lista, NO necesitas incluir "is_list" ni "list_group" en cada item
   - El sistema asignará automáticamente el orden secuencial (orden_lista: 1, 2, 3, ...)
   - Los items se ejecutarán/mostrarán en el orden en que aparezcan en el array"""

        # Agregar defaults opcionales si existen
        optional_defaults_parts = []

        if config.get('icon'):
            optional_defaults_parts.append(f',\n    "icon": "{config["icon"]}"')

        if config.get('color'):
            optional_defaults_parts.append(f',\n    "color": "{config["color"]}"')

        if config.get('working_dir'):
            optional_defaults_parts.append(f',\n    "working_dir": "{config["working_dir"]}"')

        optional_defaults = ''.join(optional_defaults_parts)

        # Generar prompt
        prompt = PromptTemplate.MAIN_TEMPLATE.format(
            category_id=config['category_id'],
            category_name=config['category_name'],
            item_type=item_type,
            item_type_desc=item_type_desc,
            tags=tags,
            tags_display=tags_display,
            is_favorite=is_favorite,
            is_sensitive=is_sensitive,
            is_favorite_text=is_favorite_text,
            is_sensitive_text=is_sensitive_text,
            list_defaults=list_defaults,
            list_context=list_context,
            list_rules=list_rules,
            user_context=user_context,
            optional_defaults=optional_defaults
        )

        return prompt

    @staticmethod
    def generate_example_json(config: Dict[str, Any]) -> str:
        """
        Genera un ejemplo de JSON para mostrar al usuario.

        Útil para mostrar en la UI antes de copiar el prompt.

        Args:
            config: Configuración del wizard

        Returns:
            String con JSON de ejemplo
        """
        item_type = config.get('item_type', 'TEXT')
        example_items = []

        # Generar ejemplos según el tipo
        if item_type == 'CODE':
            example_items = [
                {
                    "label": "Clonar repositorio",
                    "content": "git clone https://github.com/user/repo.git",
                    "description": "Clonar el repositorio desde GitHub"
                },
                {
                    "label": "Instalar dependencias",
                    "content": "npm install",
                    "description": "Instalar paquetes npm"
                },
                {
                    "label": "Ejecutar en desarrollo",
                    "content": "npm run dev",
                    "description": "Iniciar servidor de desarrollo"
                }
            ]
        elif item_type == 'URL':
            example_items = [
                {
                    "label": "Documentación oficial",
                    "content": "https://docs.example.com",
                    "description": "Docs del proyecto"
                },
                {
                    "label": "Dashboard producción",
                    "content": "https://app.example.com/dashboard",
                    "description": "Panel de control"
                }
            ]
        elif item_type == 'PATH':
            example_items = [
                {
                    "label": "Configuración Nginx",
                    "content": "/etc/nginx/nginx.conf",
                    "description": "Archivo de configuración principal"
                },
                {
                    "label": "Logs de aplicación",
                    "content": "/var/log/app/error.log",
                    "description": "Archivo de logs de errores"
                }
            ]
        else:  # TEXT
            example_items = [
                {
                    "label": "Nota importante",
                    "content": "Recordar hacer backup antes de cualquier cambio en producción",
                    "description": "Procedimiento de seguridad"
                },
                {
                    "label": "Contacto soporte",
                    "content": "support@example.com - Disponible 24/7",
                    "description": "Información de contacto"
                }
            ]

        example = {
            "category_id": config['category_id'],
            "defaults": {
                "type": item_type,
                "tags": config.get('tags', ''),
                "is_favorite": config.get('is_favorite', 0),
                "is_sensitive": config.get('is_sensitive', 0)
            },
            "items": example_items
        }

        # Agregar campos de lista si is_list=1
        if config.get('is_list', 0) == 1:
            example["defaults"]["is_list"] = 1
            example["defaults"]["list_group"] = config.get('list_group', '')

        import json
        return json.dumps(example, indent=2, ensure_ascii=False)

    @staticmethod
    def get_tips_for_type(item_type: str) -> str:
        """
        Retorna tips específicos según el tipo de item.

        Args:
            item_type: Tipo de item (TEXT, URL, CODE, PATH)

        Returns:
            String con tips
        """
        tips = {
            'TEXT': """
Tips para items tipo TEXT:
• Ideal para notas, recordatorios, instrucciones
• Puede ser multilínea usando \\n
• Útil para documentación interna
• Ejemplo: instrucciones de configuración, contactos, procedimientos
            """.strip(),

            'URL': """
Tips para items tipo URL:
• Debe ser URL completa: https://...
• Útil para documentación, dashboards, recursos
• El widget abrirá el link en el navegador
• Ejemplo: docs oficiales, paneles de control, repos GitHub
            """.strip(),

            'CODE': """
Tips para items tipo CODE:
• Comandos de terminal listos para ejecutar
• El widget copiará al portapapeles para ejecutar
• Puede incluir scripts multilínea
• Usa "working_dir" para especificar directorio de ejecución
• Ejemplo: comandos git, npm, docker, despliegues
            """.strip(),

            'PATH': """
Tips para items tipo PATH:
• Rutas absolutas o relativas a archivos/directorios
• Útil para configuraciones, logs, recursos del sistema
• El widget puede abrir el explorador de archivos
• Ejemplo: /etc/nginx/nginx.conf, ~/.bashrc, C:\\Program Files\\...
            """.strip()
        }

        return tips.get(item_type, "Tipo de item genérico")
