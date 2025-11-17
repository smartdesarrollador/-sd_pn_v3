"""
Motor de filtrado avanzado para categorías

Este módulo implementa la lógica de filtrado de categorías basándose en
múltiples criterios como estado, popularidad, fechas, atributos y ordenamiento.

Filtros soportados:
- Estado: activas, inactivas, predefinidas, personalizadas, ancladas
- Popularidad: rangos de items, usos totales, accesos
- Fechas: creación, actualización, último acceso
- Ordenamiento: alfabético, popularidad, fecha, accesos, anclado
"""

import sqlite3
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Importar Category model
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.models.category import Category

logger = logging.getLogger(__name__)


@dataclass
class FilterStats:
    """Estadísticas de resultados de filtrado"""
    total_categories: int
    filtered_categories: int
    active_filters_count: int
    execution_time_ms: float


class CategoryFilterEngine:
    """
    Motor de filtrado avanzado para categorías

    Características:
    - Generación dinámica de queries SQL
    - Soporte para múltiples filtros combinados
    - Estadísticas de resultados
    - Optimización con índices
    """

    def __init__(self, db_path: str, cache_enabled: bool = True, cache_max_size: int = 100):
        """
        Inicializar el motor de filtrado

        Args:
            db_path: Ruta a la base de datos SQLite
            cache_enabled: Si está habilitado el caché de resultados
            cache_max_size: Tamaño máximo del caché (número de entradas)
        """
        self.db_path = db_path
        self.last_query = None
        self.last_params = None
        self.last_stats = None

        # Sistema de caché
        self.cache_enabled = cache_enabled
        self.cache_max_size = cache_max_size
        self._result_cache: Dict[str, List[Category]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def apply_filters(self, filters: Dict[str, Any]) -> List[Category]:
        """
        Aplicar filtros a las categorías

        Args:
            filters: Diccionario con los filtros a aplicar

        Returns:
            Lista de categorías que cumplen los filtros

        Ejemplo de filters:
        {
            'is_active': True,
            'is_predefined': False,
            'is_pinned': True,
            'item_count_min': 5,
            'item_count_max': 50,
            'total_uses_min': 100,
            'created_after': '2025-01-01',
            'order_by': 'total_uses',
            'order_direction': 'DESC'
        }
        """
        start_time = datetime.now()

        # Verificar caché
        filter_hash = None
        if self.cache_enabled:
            filter_hash = self._hash_filters(filters)

            if filter_hash in self._result_cache:
                self._cache_hits += 1
                cached_result = self._result_cache[filter_hash]

                # Calcular estadísticas (más rápido desde caché)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds() * 1000

                active_filters = sum(1 for v in filters.values() if v is not None and v != '')

                # Reutilizar stats pero actualizar tiempo de ejecución
                if self.last_stats:
                    self.last_stats = FilterStats(
                        total_categories=self.last_stats.total_categories,
                        filtered_categories=len(cached_result),
                        active_filters_count=active_filters,
                        execution_time_ms=execution_time
                    )

                logger.info(f"Cache HIT: Returning {len(cached_result)} categories from cache "
                           f"({execution_time:.2f}ms, hits: {self._cache_hits}, "
                           f"misses: {self._cache_misses})")

                return cached_result

            else:
                self._cache_misses += 1
                logger.debug(f"Cache MISS: Executing query "
                            f"(hits: {self._cache_hits}, misses: {self._cache_misses})")

        try:
            # Construir query dinámicamente
            query, params = self.build_query(filters)
            self.last_query = query
            self.last_params = params

            # Ejecutar query
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            logger.debug(f"Executing query: {query}")
            logger.debug(f"Parameters: {params}")

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convertir a objetos Category
            categories = []
            for row in rows:
                category = Category(
                    category_id=str(row['id']),
                    name=row['name'],
                    icon=row['icon'] or '',
                    order_index=row['order_index'],
                    is_active=bool(row['is_active']),
                    is_predefined=bool(row['is_predefined']),
                    color=row['color'],
                    badge=row['badge']
                )

                # Agregar atributos extendidos
                category.item_count = row['item_count'] or 0
                category.total_uses = row['total_uses'] or 0
                category.last_accessed = row['last_accessed']
                category.access_count = row['access_count'] or 0
                category.is_pinned = bool(row['is_pinned'])
                category.pinned_order = row['pinned_order'] or 0
                category.created_at = row['created_at']
                category.updated_at = row['updated_at']

                categories.append(category)

            # Obtener total de categorías sin filtro
            cursor.execute("SELECT COUNT(*) as total FROM categories")
            total_count = cursor.fetchone()['total']

            conn.close()

            # Calcular estadísticas
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            active_filters = sum(1 for v in filters.values() if v is not None and v != '')

            self.last_stats = FilterStats(
                total_categories=total_count,
                filtered_categories=len(categories),
                active_filters_count=active_filters,
                execution_time_ms=execution_time
            )

            logger.info(f"Filter applied: {len(categories)}/{total_count} categories, "
                       f"{active_filters} filters, {execution_time:.2f}ms")

            # Guardar en caché
            if self.cache_enabled and filter_hash:
                self._add_to_cache(filter_hash, categories)

            return categories

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            import traceback
            traceback.print_exc()
            return []

    def build_query(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Construir query SQL dinámicamente basado en filtros

        Args:
            filters: Diccionario con filtros activos

        Returns:
            Tupla (query_sql, parametros)
        """
        # Query base
        query_parts = ["SELECT * FROM categories"]
        where_conditions = []
        params = []

        # === FILTROS DE ESTADO ===

        # is_active
        if 'is_active' in filters and filters['is_active'] is not None:
            where_conditions.append("is_active = ?")
            params.append(1 if filters['is_active'] else 0)

        # is_predefined
        if 'is_predefined' in filters and filters['is_predefined'] is not None:
            where_conditions.append("is_predefined = ?")
            params.append(1 if filters['is_predefined'] else 0)

        # is_pinned
        if 'is_pinned' in filters and filters['is_pinned'] is not None:
            where_conditions.append("is_pinned = ?")
            params.append(1 if filters['is_pinned'] else 0)

        # === FILTROS DE POPULARIDAD ===

        # item_count (rango)
        if 'item_count_min' in filters and filters['item_count_min'] is not None:
            where_conditions.append("item_count >= ?")
            params.append(filters['item_count_min'])

        if 'item_count_max' in filters and filters['item_count_max'] is not None:
            where_conditions.append("item_count <= ?")
            params.append(filters['item_count_max'])

        # total_uses (rango)
        if 'total_uses_min' in filters and filters['total_uses_min'] is not None:
            where_conditions.append("total_uses >= ?")
            params.append(filters['total_uses_min'])

        if 'total_uses_max' in filters and filters['total_uses_max'] is not None:
            where_conditions.append("total_uses <= ?")
            params.append(filters['total_uses_max'])

        # access_count (rango)
        if 'access_count_min' in filters and filters['access_count_min'] is not None:
            where_conditions.append("access_count >= ?")
            params.append(filters['access_count_min'])

        if 'access_count_max' in filters and filters['access_count_max'] is not None:
            where_conditions.append("access_count <= ?")
            params.append(filters['access_count_max'])

        # === FILTROS DE FECHAS ===

        # created_at
        if 'created_after' in filters and filters['created_after']:
            where_conditions.append("created_at >= ?")
            params.append(filters['created_after'])

        if 'created_before' in filters and filters['created_before']:
            where_conditions.append("created_at <= ?")
            params.append(filters['created_before'])

        # updated_at
        if 'updated_after' in filters and filters['updated_after']:
            where_conditions.append("updated_at >= ?")
            params.append(filters['updated_after'])

        if 'updated_before' in filters and filters['updated_before']:
            where_conditions.append("updated_at <= ?")
            params.append(filters['updated_before'])

        # last_accessed
        if 'accessed_after' in filters and filters['accessed_after']:
            where_conditions.append("last_accessed >= ?")
            params.append(filters['accessed_after'])

        if 'accessed_before' in filters and filters['accessed_before']:
            where_conditions.append("last_accessed <= ?")
            params.append(filters['accessed_before'])

        # Categorías no accedidas
        if 'never_accessed' in filters and filters['never_accessed']:
            where_conditions.append("last_accessed IS NULL")

        # === FILTROS DE COLOR Y BADGE ===

        # has_color
        if 'has_color' in filters and filters['has_color'] is not None:
            if filters['has_color']:
                where_conditions.append("color IS NOT NULL AND color != ''")
            else:
                where_conditions.append("(color IS NULL OR color = '')")

        # has_badge
        if 'has_badge' in filters and filters['has_badge'] is not None:
            if filters['has_badge']:
                where_conditions.append("badge IS NOT NULL AND badge != ''")
            else:
                where_conditions.append("(badge IS NULL OR badge = '')")

        # color_value (color específico)
        if 'color_value' in filters and filters['color_value']:
            where_conditions.append("color = ?")
            params.append(filters['color_value'])

        # === BÚSQUEDA POR NOMBRE ===

        if 'search_text' in filters and filters['search_text']:
            where_conditions.append("name LIKE ?")
            params.append(f"%{filters['search_text']}%")

        # === CONSTRUIR WHERE CLAUSE ===

        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))

        # === ORDENAMIENTO ===

        order_by = filters.get('order_by', 'order_index')
        order_direction = filters.get('order_direction', 'ASC')

        # Validar order_by
        valid_order_fields = [
            'name', 'order_index', 'item_count', 'total_uses',
            'access_count', 'created_at', 'updated_at', 'last_accessed',
            'pinned_order'
        ]

        if order_by not in valid_order_fields:
            order_by = 'order_index'

        # Validar direction
        if order_direction.upper() not in ['ASC', 'DESC']:
            order_direction = 'ASC'

        # Orden especial: ancladas primero
        if filters.get('pinned_first', False):
            query_parts.append("ORDER BY is_pinned DESC, pinned_order ASC, "
                             f"{order_by} {order_direction}")
        else:
            query_parts.append(f"ORDER BY {order_by} {order_direction}")

        # === LÍMITE ===

        if 'limit' in filters and filters['limit']:
            query_parts.append("LIMIT ?")
            params.append(filters['limit'])

        # Construir query final
        final_query = " ".join(query_parts)

        return final_query, params

    def get_filter_stats(self) -> Optional[FilterStats]:
        """
        Obtener estadísticas del último filtrado

        Returns:
            FilterStats con información del último filtrado o None
        """
        return self.last_stats

    def get_available_colors(self) -> List[str]:
        """
        Obtener lista de colores únicos usados en categorías

        Returns:
            Lista de colores (hex) únicos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT color
                FROM categories
                WHERE color IS NOT NULL AND color != ''
                ORDER BY color
            """)

            colors = [row[0] for row in cursor.fetchall()]
            conn.close()

            return colors

        except Exception as e:
            logger.error(f"Error getting colors: {e}")
            return []

    def get_date_range(self) -> Dict[str, Optional[str]]:
        """
        Obtener rango de fechas de las categorías

        Returns:
            Diccionario con fechas mínimas y máximas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    MIN(created_at) as min_created,
                    MAX(created_at) as max_created,
                    MIN(updated_at) as min_updated,
                    MAX(updated_at) as max_updated,
                    MIN(last_accessed) as min_accessed,
                    MAX(last_accessed) as max_accessed
                FROM categories
            """)

            row = cursor.fetchone()
            conn.close()

            return {
                'min_created': row[0],
                'max_created': row[1],
                'min_updated': row[2],
                'max_updated': row[3],
                'min_accessed': row[4],
                'max_accessed': row[5]
            }

        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return {}

    def get_popularity_stats(self) -> Dict[str, int]:
        """
        Obtener estadísticas de popularidad

        Returns:
            Diccionario con estadísticas min/max/avg
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    MIN(item_count) as min_items,
                    MAX(item_count) as max_items,
                    AVG(item_count) as avg_items,
                    MIN(total_uses) as min_uses,
                    MAX(total_uses) as max_uses,
                    AVG(total_uses) as avg_uses,
                    MIN(access_count) as min_access,
                    MAX(access_count) as max_access,
                    AVG(access_count) as avg_access
                FROM categories
            """)

            row = cursor.fetchone()
            conn.close()

            return {
                'min_items': int(row[0] or 0),
                'max_items': int(row[1] or 0),
                'avg_items': int(row[2] or 0),
                'min_uses': int(row[3] or 0),
                'max_uses': int(row[4] or 0),
                'avg_uses': int(row[5] or 0),
                'min_access': int(row[6] or 0),
                'max_access': int(row[7] or 0),
                'avg_access': int(row[8] or 0)
            }

        except Exception as e:
            logger.error(f"Error getting popularity stats: {e}")
            return {}

    def clear_cache(self):
        """Limpiar caché de resultados"""
        self._result_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.last_query = None
        self.last_params = None
        self.last_stats = None
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del caché

        Returns:
            Diccionario con estadísticas del caché
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self._result_cache),
            'cache_max_size': self.cache_max_size,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate
        }

    def _hash_filters(self, filters: Dict[str, Any]) -> str:
        """
        Generar hash único para una combinación de filtros

        Args:
            filters: Diccionario de filtros

        Returns:
            Hash MD5 del diccionario de filtros
        """
        # Convertir a JSON ordenado para consistencia
        filter_json = json.dumps(filters, sort_keys=True, default=str)

        # Generar hash MD5
        hash_obj = hashlib.md5(filter_json.encode('utf-8'))
        return hash_obj.hexdigest()

    def _add_to_cache(self, filter_hash: str, categories: List[Category]) -> None:
        """
        Agregar resultado al caché

        Args:
            filter_hash: Hash del filtro
            categories: Lista de categorías a cachear
        """
        # Si el caché está lleno, eliminar entrada más antigua (FIFO)
        if len(self._result_cache) >= self.cache_max_size:
            # Obtener primera clave (más antigua)
            oldest_key = next(iter(self._result_cache))
            del self._result_cache[oldest_key]
            logger.debug(f"Cache full, removed oldest entry: {oldest_key[:8]}...")

        # Agregar al caché
        self._result_cache[filter_hash] = categories
        logger.debug(f"Added to cache: {filter_hash[:8]}... ({len(categories)} categories)")


# Función de utilidad para crear filtros predefinidos
def create_preset_filters() -> Dict[str, Dict[str, Any]]:
    """
    Crear filtros predefinidos comunes

    Returns:
        Diccionario con filtros predefinidos
    """
    return {
        'activas': {
            'is_active': True
        },
        'inactivas': {
            'is_active': False
        },
        'predefinidas': {
            'is_predefined': True
        },
        'personalizadas': {
            'is_predefined': False
        },
        'ancladas': {
            'is_pinned': True,
            'order_by': 'pinned_order',
            'order_direction': 'ASC'
        },
        'populares': {
            'is_active': True,
            'item_count_min': 5,
            'order_by': 'total_uses',
            'order_direction': 'DESC',
            'limit': 10
        },
        'vacias': {
            'item_count_max': 0
        },
        'recientes': {
            'order_by': 'created_at',
            'order_direction': 'DESC',
            'limit': 10
        },
        'actualizadas_recientemente': {
            'order_by': 'updated_at',
            'order_direction': 'DESC',
            'limit': 10
        },
        'nunca_accedidas': {
            'never_accessed': True
        }
    }
