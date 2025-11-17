"""
Tag Groups Manager - Gestión de plantillas de tags reutilizables
Fecha: 2025-11-05

Este módulo maneja las operaciones CRUD para Tag Groups (grupos de tags),
que son plantillas reutilizables de conjuntos de tags relacionados.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TagGroupsManager:
    """Gestor de Tag Groups (plantillas de tags)"""

    def __init__(self, db_path: str):
        """
        Inicializar el gestor de Tag Groups

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        logger.info("TagGroupsManager initialized")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Obtener conexión a la base de datos

        Returns:
            Conexión SQLite
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ========== CREATE ==========

    def create_group(
        self,
        name: str,
        tags: str,
        description: Optional[str] = None,
        color: str = "#007acc",
        icon: str = "🏷️",
        is_active: bool = True
    ) -> Optional[int]:
        """
        Crear un nuevo Tag Group

        Args:
            name: Nombre del grupo (único)
            tags: Tags separados por comas (ej: "python,fastapi,api")
            description: Descripción opcional
            color: Color en formato hex (default: #007acc)
            icon: Emoji o icono (default: 🏷️)
            is_active: Si el grupo está activo (default: True)

        Returns:
            ID del grupo creado, o None si falló
        """
        try:
            # Validaciones
            if not name or not name.strip():
                logger.error("Name is required")
                return None

            if not tags or not tags.strip():
                logger.error("Tags are required")
                return None

            # Limpiar tags (quitar espacios extra)
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if not tags_list:
                logger.error("At least one valid tag is required")
                return None

            clean_tags = ','.join(tags_list)

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tag_groups (name, description, tags, color, icon, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name.strip(), description, clean_tags, color, icon, is_active))

            group_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Tag group created: {name} (ID: {group_id})")
            return group_id

        except sqlite3.IntegrityError as e:
            logger.error(f"Tag group with name '{name}' already exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating tag group: {e}", exc_info=True)
            return None

    # ========== READ ==========

    def get_all_groups(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Obtener todos los Tag Groups

        Args:
            active_only: Si True, solo devuelve grupos activos

        Returns:
            Lista de grupos como diccionarios
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if active_only:
                cursor.execute("""
                    SELECT * FROM tag_groups
                    WHERE is_active = 1
                    ORDER BY name ASC
                """)
            else:
                cursor.execute("""
                    SELECT * FROM tag_groups
                    ORDER BY name ASC
                """)

            rows = cursor.fetchall()
            conn.close()

            groups = [dict(row) for row in rows]
            logger.debug(f"Retrieved {len(groups)} tag groups")
            return groups

        except Exception as e:
            logger.error(f"Error getting tag groups: {e}", exc_info=True)
            return []

    def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un Tag Group por ID

        Args:
            group_id: ID del grupo

        Returns:
            Diccionario con datos del grupo, o None si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tag_groups
                WHERE id = ?
            """, (group_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            else:
                logger.warning(f"Tag group not found: {group_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting tag group {group_id}: {e}", exc_info=True)
            return None

    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener un Tag Group por nombre

        Args:
            name: Nombre del grupo

        Returns:
            Diccionario con datos del grupo, o None si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tag_groups
                WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting tag group by name '{name}': {e}", exc_info=True)
            return None

    def search_groups(self, query: str) -> List[Dict[str, Any]]:
        """
        Buscar Tag Groups por nombre, descripción o tags

        Args:
            query: Texto a buscar

        Returns:
            Lista de grupos que coinciden con la búsqueda
        """
        try:
            if not query or not query.strip():
                return self.get_all_groups()

            conn = self._get_connection()
            cursor = conn.cursor()

            search_pattern = f"%{query.strip()}%"

            cursor.execute("""
                SELECT * FROM tag_groups
                WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
                ORDER BY name ASC
            """, (search_pattern, search_pattern, search_pattern))

            rows = cursor.fetchall()
            conn.close()

            groups = [dict(row) for row in rows]
            logger.debug(f"Found {len(groups)} groups matching '{query}'")
            return groups

        except Exception as e:
            logger.error(f"Error searching tag groups: {e}", exc_info=True)
            return []

    def get_tags_as_list(self, group_id: int) -> List[str]:
        """
        Obtener los tags de un grupo como lista

        Args:
            group_id: ID del grupo

        Returns:
            Lista de tags individuales
        """
        group = self.get_group(group_id)
        if not group or not group.get('tags'):
            return []

        return [tag.strip() for tag in group['tags'].split(',') if tag.strip()]

    # ========== UPDATE ==========

    def update_group(
        self,
        group_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Actualizar un Tag Group existente

        Args:
            group_id: ID del grupo a actualizar
            name: Nuevo nombre (opcional)
            description: Nueva descripción (opcional)
            tags: Nuevos tags (opcional)
            color: Nuevo color (opcional)
            icon: Nuevo icono (opcional)
            is_active: Nuevo estado activo (opcional)

        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Verificar que el grupo existe
            group = self.get_group(group_id)
            if not group:
                logger.error(f"Tag group {group_id} not found")
                return False

            # Construir query dinámica con solo los campos que se van a actualizar
            updates = []
            params = []

            if name is not None and name.strip():
                updates.append("name = ?")
                params.append(name.strip())

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if tags is not None:
                # Limpiar tags
                tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                if tags_list:
                    clean_tags = ','.join(tags_list)
                    updates.append("tags = ?")
                    params.append(clean_tags)
                else:
                    logger.error("At least one valid tag is required")
                    return False

            if color is not None:
                updates.append("color = ?")
                params.append(color)

            if icon is not None:
                updates.append("icon = ?")
                params.append(icon)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)

            # Agregar updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")

            if not updates:
                logger.warning("No fields to update")
                return False

            # Agregar group_id al final de los parámetros
            params.append(group_id)

            conn = self._get_connection()
            cursor = conn.cursor()

            query = f"""
                UPDATE tag_groups
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected > 0:
                logger.info(f"Tag group updated: {group_id}")
                return True
            else:
                logger.warning(f"No changes made to tag group {group_id}")
                return False

        except sqlite3.IntegrityError as e:
            logger.error(f"Tag group name conflict during update: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating tag group {group_id}: {e}", exc_info=True)
            return False

    # ========== DELETE ==========

    def delete_group(self, group_id: int) -> bool:
        """
        Eliminar un Tag Group

        Args:
            group_id: ID del grupo a eliminar

        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM tag_groups
                WHERE id = ?
            """, (group_id,))

            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected > 0:
                logger.info(f"Tag group deleted: {group_id}")
                return True
            else:
                logger.warning(f"Tag group {group_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting tag group {group_id}: {e}", exc_info=True)
            return False

    def soft_delete_group(self, group_id: int) -> bool:
        """
        Soft delete: marcar un Tag Group como inactivo

        Args:
            group_id: ID del grupo

        Returns:
            True si la operación fue exitosa
        """
        return self.update_group(group_id, is_active=False)

    # ========== ESTADÍSTICAS ==========

    def get_group_usage_count(self, group_id: int) -> int:
        """
        Obtener el número de items que usan tags de este grupo

        Args:
            group_id: ID del grupo

        Returns:
            Número de items que contienen al menos un tag del grupo
        """
        try:
            group = self.get_group(group_id)
            if not group or not group.get('tags'):
                return 0

            tags_list = self.get_tags_as_list(group_id)
            if not tags_list:
                return 0

            conn = self._get_connection()
            cursor = conn.cursor()

            # Construir condiciones de búsqueda para cada tag
            # Buscamos items que contengan cualquiera de los tags del grupo
            conditions = []
            params = []

            for tag in tags_list:
                # Buscar el tag exacto en el campo tags
                # El campo tags puede ser: "tag1,tag2,tag3"
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

            query = f"""
                SELECT COUNT(DISTINCT id) as count
                FROM items
                WHERE ({' OR '.join(conditions)})
            """

            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()

            count = result['count'] if result else 0
            logger.debug(f"Tag group {group_id} usage count: {count}")
            return count

        except Exception as e:
            logger.error(f"Error getting usage count for tag group {group_id}: {e}", exc_info=True)
            return 0

    def get_all_groups_with_usage(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los Tag Groups con sus estadísticas de uso

        Returns:
            Lista de grupos con campo 'usage_count' agregado
        """
        groups = self.get_all_groups()

        for group in groups:
            group['usage_count'] = self.get_group_usage_count(group['id'])

        return groups

    # ========== UTILIDADES ==========

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de Tag Groups

        Returns:
            Diccionario con estadísticas
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total de grupos
            cursor.execute("SELECT COUNT(*) as count FROM tag_groups")
            total = cursor.fetchone()['count']

            # Grupos activos
            cursor.execute("SELECT COUNT(*) as count FROM tag_groups WHERE is_active = 1")
            active = cursor.fetchone()['count']

            # Grupos inactivos
            inactive = total - active

            # Total de tags únicos
            cursor.execute("SELECT tags FROM tag_groups WHERE is_active = 1")
            rows = cursor.fetchall()
            all_tags = set()
            for row in rows:
                if row['tags']:
                    tags_list = [tag.strip() for tag in row['tags'].split(',')]
                    all_tags.update(tags_list)

            conn.close()

            stats = {
                'total_groups': total,
                'active_groups': active,
                'inactive_groups': inactive,
                'unique_tags': len(all_tags),
                'all_tags': sorted(list(all_tags))
            }

            logger.debug(f"Tag groups statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting tag groups statistics: {e}", exc_info=True)
            return {
                'total_groups': 0,
                'active_groups': 0,
                'inactive_groups': 0,
                'unique_tags': 0,
                'all_tags': []
            }

    def validate_tags(self, tags: str) -> tuple[bool, str]:
        """
        Validar formato de tags

        Args:
            tags: String de tags separados por comas

        Returns:
            Tupla (es_válido, mensaje)
        """
        if not tags or not tags.strip():
            return False, "Tags cannot be empty"

        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        if not tags_list:
            return False, "At least one valid tag is required"

        # Validar que no haya tags duplicados
        if len(tags_list) != len(set(tags_list)):
            return False, "Duplicate tags found"

        # Validar longitud de tags
        for tag in tags_list:
            if len(tag) > 50:
                return False, f"Tag '{tag}' is too long (max 50 characters)"

        return True, f"{len(tags_list)} tags valid"


if __name__ == "__main__":
    """
    Pruebas básicas del TagGroupsManager
    """
    import sys
    from pathlib import Path

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Determinar ruta de la base de datos
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "widget_sidebar.db"

    print(f"\n{'='*60}")
    print("  TAG GROUPS MANAGER - PRUEBAS")
    print(f"{'='*60}\n")
    print(f"Database: {db_path}\n")

    if not Path(db_path).exists():
        print("❌ Database file not found")
        sys.exit(1)

    manager = TagGroupsManager(str(db_path))

    print("1. Get all groups:")
    groups = manager.get_all_groups()
    for group in groups:
        print(f"   - {group['name']} ({group['id']}): {group['tags']}")

    print("\n2. Statistics:")
    stats = manager.get_statistics()
    print(f"   - Total groups: {stats['total_groups']}")
    print(f"   - Active groups: {stats['active_groups']}")
    print(f"   - Unique tags: {stats['unique_tags']}")

    print("\n3. Search test:")
    results = manager.search_groups("python")
    print(f"   Found {len(results)} groups matching 'python'")

    print("\n✅ Tests completed!")
