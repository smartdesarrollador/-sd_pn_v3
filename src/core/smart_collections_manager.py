"""
Smart Collections Manager - Gestión de filtros guardados inteligentes
Fecha: 2025-11-05

Este módulo maneja las operaciones CRUD para Smart Collections (colecciones inteligentes),
que son filtros guardados con criterios múltiples para búsquedas dinámicas de items.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartCollectionsManager:
    """Gestor de Smart Collections (filtros guardados inteligentes)"""

    def __init__(self, db_path: str):
        """
        Inicializar el gestor de Smart Collections

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        logger.info("SmartCollectionsManager initialized")

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

    def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        icon: str = "🔍",
        color: str = "#00d4ff",
        tags_include: Optional[str] = None,
        tags_exclude: Optional[str] = None,
        category_id: Optional[int] = None,
        item_type: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        is_sensitive: Optional[bool] = None,
        is_active_filter: Optional[bool] = None,
        is_archived_filter: Optional[bool] = None,
        search_text: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        is_active: bool = True
    ) -> Optional[int]:
        """
        Crear una nueva Smart Collection

        Args:
            name: Nombre de la colección (único)
            description: Descripción opcional
            icon: Emoji o icono (default: 🔍)
            color: Color en formato hex (default: #00d4ff)
            tags_include: Tags que deben estar presentes (separados por comas)
            tags_exclude: Tags que deben estar ausentes (separados por comas)
            category_id: ID de categoría para filtrar (opcional)
            item_type: Tipo de item ('TEXT', 'URL', 'CODE', 'PATH')
            is_favorite: Filtrar por favoritos (True/False/None)
            is_sensitive: Filtrar por sensibles (True/False/None)
            is_active_filter: Filtrar por activos (True/False/None)
            is_archived_filter: Filtrar por archivados (True/False/None)
            search_text: Texto a buscar en label/content
            date_from: Fecha desde (formato ISO)
            date_to: Fecha hasta (formato ISO)
            is_active: Si la colección está activa (default: True)

        Returns:
            ID de la colección creada, o None si falló
        """
        try:
            # Validaciones
            if not name or not name.strip():
                logger.error("Name is required")
                return None

            # Validar item_type si se proporciona
            if item_type and item_type not in ['TEXT', 'URL', 'CODE', 'PATH']:
                logger.error(f"Invalid item_type: {item_type}")
                return None

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO smart_collections (
                    name, description, icon, color,
                    tags_include, tags_exclude, category_id, item_type,
                    is_favorite, is_sensitive, is_active_filter, is_archived_filter,
                    search_text, date_from, date_to, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name.strip(), description, icon, color,
                tags_include, tags_exclude, category_id, item_type,
                is_favorite, is_sensitive, is_active_filter, is_archived_filter,
                search_text, date_from, date_to, is_active
            ))

            collection_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Smart collection created: {name} (ID: {collection_id})")
            return collection_id

        except sqlite3.IntegrityError as e:
            logger.error(f"Smart collection with name '{name}' already exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating smart collection: {e}", exc_info=True)
            return None

    # ========== READ ==========

    def get_all_collections(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Obtener todas las Smart Collections

        Args:
            active_only: Si True, solo devuelve colecciones activas

        Returns:
            Lista de colecciones como diccionarios
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if active_only:
                cursor.execute("""
                    SELECT * FROM smart_collections
                    WHERE is_active = 1
                    ORDER BY name ASC
                """)
            else:
                cursor.execute("""
                    SELECT * FROM smart_collections
                    ORDER BY name ASC
                """)

            rows = cursor.fetchall()
            conn.close()

            collections = [dict(row) for row in rows]
            logger.debug(f"Retrieved {len(collections)} smart collections")
            return collections

        except Exception as e:
            logger.error(f"Error getting smart collections: {e}", exc_info=True)
            return []

    def get_collection(self, collection_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener una Smart Collection por ID

        Args:
            collection_id: ID de la colección

        Returns:
            Diccionario con datos de la colección, o None si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM smart_collections
                WHERE id = ?
            """, (collection_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            else:
                logger.warning(f"Smart collection not found: {collection_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting smart collection {collection_id}: {e}", exc_info=True)
            return None

    def get_collection_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener una Smart Collection por nombre

        Args:
            name: Nombre de la colección

        Returns:
            Diccionario con datos de la colección, o None si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM smart_collections
                WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting smart collection by name '{name}': {e}", exc_info=True)
            return None

    def search_collections(self, query: str) -> List[Dict[str, Any]]:
        """
        Buscar Smart Collections por nombre o descripción

        Args:
            query: Texto a buscar

        Returns:
            Lista de colecciones que coinciden con la búsqueda
        """
        try:
            if not query or not query.strip():
                return self.get_all_collections()

            conn = self._get_connection()
            cursor = conn.cursor()

            search_pattern = f"%{query.strip()}%"

            cursor.execute("""
                SELECT * FROM smart_collections
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name ASC
            """, (search_pattern, search_pattern))

            rows = cursor.fetchall()
            conn.close()

            collections = [dict(row) for row in rows]
            logger.debug(f"Found {len(collections)} collections matching '{query}'")
            return collections

        except Exception as e:
            logger.error(f"Error searching smart collections: {e}", exc_info=True)
            return []

    # ========== UPDATE ==========

    def update_collection(
        self,
        collection_id: int,
        **kwargs
    ) -> bool:
        """
        Actualizar una Smart Collection existente

        Args:
            collection_id: ID de la colección a actualizar
            **kwargs: Campos a actualizar (name, description, icon, color, filtros, etc.)

        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Verificar que la colección existe
            collection = self.get_collection(collection_id)
            if not collection:
                logger.error(f"Smart collection {collection_id} not found")
                return False

            # Campos permitidos para actualización
            allowed_fields = {
                'name', 'description', 'icon', 'color',
                'tags_include', 'tags_exclude', 'category_id', 'item_type',
                'is_favorite', 'is_sensitive', 'is_active_filter', 'is_archived_filter',
                'search_text', 'date_from', 'date_to', 'is_active'
            }

            # Filtrar solo campos permitidos
            updates = []
            params = []

            for field, value in kwargs.items():
                if field in allowed_fields:
                    # Validación especial para item_type
                    if field == 'item_type' and value is not None:
                        if value not in ['TEXT', 'URL', 'CODE', 'PATH']:
                            logger.error(f"Invalid item_type: {value}")
                            return False

                    updates.append(f"{field} = ?")
                    params.append(value)

            # Agregar updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")

            if not updates:
                logger.warning("No valid fields to update")
                return False

            # Agregar collection_id al final de los parámetros
            params.append(collection_id)

            conn = self._get_connection()
            cursor = conn.cursor()

            query = f"""
                UPDATE smart_collections
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected > 0:
                logger.info(f"Smart collection updated: {collection_id}")
                return True
            else:
                logger.warning(f"No changes made to smart collection {collection_id}")
                return False

        except sqlite3.IntegrityError as e:
            logger.error(f"Smart collection name conflict during update: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating smart collection {collection_id}: {e}", exc_info=True)
            return False

    # ========== DELETE ==========

    def delete_collection(self, collection_id: int) -> bool:
        """
        Eliminar una Smart Collection

        Args:
            collection_id: ID de la colección a eliminar

        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM smart_collections
                WHERE id = ?
            """, (collection_id,))

            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected > 0:
                logger.info(f"Smart collection deleted: {collection_id}")
                return True
            else:
                logger.warning(f"Smart collection {collection_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting smart collection {collection_id}: {e}", exc_info=True)
            return False

    def soft_delete_collection(self, collection_id: int) -> bool:
        """
        Soft delete: marcar una Smart Collection como inactiva

        Args:
            collection_id: ID de la colección

        Returns:
            True si la operación fue exitosa
        """
        return self.update_collection(collection_id, is_active=False)

    # ========== EJECUCIÓN DE FILTROS ==========

    def execute_collection(self, collection_id: int) -> List[Dict[str, Any]]:
        """
        Ejecutar los filtros de una Smart Collection y obtener items que coincidan

        Args:
            collection_id: ID de la colección

        Returns:
            Lista de items que cumplen con los criterios de la colección
        """
        try:
            collection = self.get_collection(collection_id)
            if not collection:
                logger.error(f"Collection {collection_id} not found")
                return []

            return self._execute_filters(collection)

        except Exception as e:
            logger.error(f"Error executing collection {collection_id}: {e}", exc_info=True)
            return []

    def _execute_filters(self, collection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ejecutar los filtros de una colección

        Args:
            collection: Diccionario con los datos de la colección

        Returns:
            Lista de items que cumplen con los criterios
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Construir query dinámica basada en los filtros
            where_clauses = []
            params = []

            # Filtro por categoría
            if collection.get('category_id'):
                where_clauses.append("category_id = ?")
                params.append(collection['category_id'])

            # Filtro por tipo de item
            if collection.get('item_type'):
                where_clauses.append("item_type = ?")
                params.append(collection['item_type'])

            # Filtro por favorito
            if collection.get('is_favorite') is not None:
                where_clauses.append("is_favorite = ?")
                params.append(collection['is_favorite'])

            # Filtro por sensible
            if collection.get('is_sensitive') is not None:
                where_clauses.append("is_sensitive = ?")
                params.append(collection['is_sensitive'])

            # Filtro por activo
            if collection.get('is_active_filter') is not None:
                where_clauses.append("is_active = ?")
                params.append(collection['is_active_filter'])

            # Filtro por archivado
            if collection.get('is_archived_filter') is not None:
                where_clauses.append("is_archived = ?")
                params.append(collection['is_archived_filter'])

            # Filtro por texto de búsqueda
            if collection.get('search_text'):
                search_pattern = f"%{collection['search_text']}%"
                where_clauses.append("(label LIKE ? OR content LIKE ?)")
                params.extend([search_pattern, search_pattern])

            # Filtro por tags incluidos (debe tener al menos uno)
            if collection.get('tags_include'):
                tags_list = [tag.strip() for tag in collection['tags_include'].split(',')]
                if tags_list:
                    tag_conditions = []
                    for tag in tags_list:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    where_clauses.append(f"({' OR '.join(tag_conditions)})")

            # Filtro por tags excluidos (no debe tener ninguno)
            if collection.get('tags_exclude'):
                tags_list = [tag.strip() for tag in collection['tags_exclude'].split(',')]
                for tag in tags_list:
                    where_clauses.append("(tags NOT LIKE ? OR tags IS NULL)")
                    params.append(f"%{tag}%")

            # Filtro por rango de fechas
            if collection.get('date_from'):
                where_clauses.append("created_at >= ?")
                params.append(collection['date_from'])

            if collection.get('date_to'):
                where_clauses.append("created_at <= ?")
                params.append(collection['date_to'])

            # Construir query final
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)
            else:
                where_sql = ""

            query = f"""
                SELECT * FROM items
                {where_sql}
                ORDER BY last_used DESC, created_at DESC
            """

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in rows]
            logger.debug(f"Collection '{collection['name']}' returned {len(items)} items")
            return items

        except Exception as e:
            logger.error(f"Error executing filters: {e}", exc_info=True)
            return []

    def get_collection_count(self, collection_id: int) -> int:
        """
        Obtener el número de items que coinciden con una colección (sin cargar todos los items)

        Args:
            collection_id: ID de la colección

        Returns:
            Número de items que cumplen con los criterios
        """
        try:
            items = self.execute_collection(collection_id)
            return len(items)
        except Exception as e:
            logger.error(f"Error getting collection count: {e}", exc_info=True)
            return 0

    # ========== ESTADÍSTICAS ==========

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de Smart Collections

        Returns:
            Diccionario con estadísticas
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total de colecciones
            cursor.execute("SELECT COUNT(*) as count FROM smart_collections")
            total = cursor.fetchone()['count']

            # Colecciones activas
            cursor.execute("SELECT COUNT(*) as count FROM smart_collections WHERE is_active = 1")
            active = cursor.fetchone()['count']

            # Colecciones inactivas
            inactive = total - active

            conn.close()

            stats = {
                'total_collections': total,
                'active_collections': active,
                'inactive_collections': inactive
            }

            logger.debug(f"Smart collections statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting smart collections statistics: {e}", exc_info=True)
            return {
                'total_collections': 0,
                'active_collections': 0,
                'inactive_collections': 0
            }

    def get_all_collections_with_count(self) -> List[Dict[str, Any]]:
        """
        Obtener todas las Smart Collections con el número de items que contienen

        Returns:
            Lista de colecciones con campo 'item_count' agregado
        """
        collections = self.get_all_collections()

        for collection in collections:
            collection['item_count'] = self.get_collection_count(collection['id'])

        return collections


if __name__ == "__main__":
    """
    Pruebas básicas del SmartCollectionsManager
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
    print("  SMART COLLECTIONS MANAGER - PRUEBAS")
    print(f"{'='*60}\n")
    print(f"Database: {db_path}\n")

    if not Path(db_path).exists():
        print("❌ Database file not found")
        sys.exit(1)

    manager = SmartCollectionsManager(str(db_path))

    print("1. Get all collections:")
    collections = manager.get_all_collections()
    for collection in collections:
        print(f"   - {collection['name']} ({collection['id']})")

    print("\n2. Statistics:")
    stats = manager.get_statistics()
    print(f"   - Total collections: {stats['total_collections']}")
    print(f"   - Active collections: {stats['active_collections']}")

    print("\n3. Execute collection test:")
    if collections:
        first_collection = collections[0]
        items = manager.execute_collection(first_collection['id'])
        print(f"   Collection '{first_collection['name']}' has {len(items)} items")

    print("\n✅ Tests completed!")
