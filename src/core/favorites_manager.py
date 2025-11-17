"""
Favorites Manager - Gestión de items favoritos
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FavoritesManager:
    """Gestor de items favoritos"""

    def __init__(self, db_path: str = "widget_sidebar.db"):
        """Inicializar manager"""
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ==================== CRUD Básico ====================

    def mark_as_favorite(self, item_id: int, order: int = 0) -> bool:
        """Marcar item como favorito"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Si order es 0, asignar el siguiente disponible
            if order == 0:
                order = self.get_next_order_index()

            cursor.execute("""
                UPDATE items
                SET is_favorite = 1,
                    favorite_order = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (order, item_id))

            conn.commit()
            conn.close()

            logger.info(f"Item {item_id} marked as favorite with order {order}")
            return True

        except Exception as e:
            logger.error(f"Error marking item {item_id} as favorite: {e}")
            return False

    def unmark_favorite(self, item_id: int) -> bool:
        """Desmarcar item como favorito"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE items
                SET is_favorite = 0,
                    favorite_order = 0,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (item_id,))

            conn.commit()
            conn.close()

            logger.info(f"Item {item_id} unmarked as favorite")
            return True

        except Exception as e:
            logger.error(f"Error unmarking item {item_id} as favorite: {e}")
            return False

    def toggle_favorite(self, item_id: int) -> bool:
        """Alternar estado de favorito (retorna True si ahora ES favorito)"""
        try:
            # Verificar estado actual
            if self.is_favorite(item_id):
                self.unmark_favorite(item_id)
                return False
            else:
                self.mark_as_favorite(item_id)
                return True

        except Exception as e:
            logger.error(f"Error toggling favorite for item {item_id}: {e}")
            return False

    def is_favorite(self, item_id: int) -> bool:
        """Verificar si item es favorito"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT is_favorite FROM items WHERE id = ?
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return result['is_favorite'] == 1
            return False

        except Exception as e:
            logger.error(f"Error checking if item {item_id} is favorite: {e}")
            return False

    # ==================== Listado ====================

    def get_all_favorites(self, limit: Optional[int] = None) -> List[Dict]:
        """Obtener todos los favoritos ordenados"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT * FROM items
                WHERE is_favorite = 1
                ORDER BY favorite_order ASC, use_count DESC
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            favorites = [dict(row) for row in results]
            logger.info(f"Retrieved {len(favorites)} favorites")
            return favorites

        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []

    def get_favorites_by_category(self, category_id: int) -> List[Dict]:
        """Obtener favoritos de una categoría específica"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM items
                WHERE is_favorite = 1 AND category_id = ?
                ORDER BY favorite_order ASC, use_count DESC
            """, (category_id,))

            results = cursor.fetchall()
            conn.close()

            favorites = [dict(row) for row in results]
            logger.info(f"Retrieved {len(favorites)} favorites for category {category_id}")
            return favorites

        except Exception as e:
            logger.error(f"Error getting favorites by category: {e}")
            return []

    def get_favorites_count(self) -> int:
        """Contar total de favoritos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as count FROM items WHERE is_favorite = 1
            """)

            result = cursor.fetchone()
            conn.close()

            count = result['count'] if result else 0
            return count

        except Exception as e:
            logger.error(f"Error counting favorites: {e}")
            return 0

    # ==================== Ordenamiento ====================

    def reorder_favorite(self, item_id: int, new_order: int) -> bool:
        """Cambiar orden de un favorito"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE items
                SET favorite_order = ?,
                    updated_at = datetime('now')
                WHERE id = ? AND is_favorite = 1
            """, (new_order, item_id))

            conn.commit()
            conn.close()

            logger.info(f"Item {item_id} reordered to position {new_order}")
            return True

        except Exception as e:
            logger.error(f"Error reordering item {item_id}: {e}")
            return False

    def reorder_favorites(self, item_ids: List[int]) -> bool:
        """Reordenar múltiples favoritos (drag & drop)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Asignar orden basado en posición en la lista
            for order, item_id in enumerate(item_ids, start=1):
                cursor.execute("""
                    UPDATE items
                    SET favorite_order = ?,
                        updated_at = datetime('now')
                    WHERE id = ? AND is_favorite = 1
                """, (order, item_id))

            conn.commit()
            conn.close()

            logger.info(f"Reordered {len(item_ids)} favorites")
            return True

        except Exception as e:
            logger.error(f"Error reordering favorites: {e}")
            return False

    def auto_order_favorites(self, by: str = "use_count") -> bool:
        """Auto-ordenar favoritos por criterio"""
        try:
            valid_criteria = ["use_count", "last_used", "label"]
            if by not in valid_criteria:
                logger.error(f"Invalid ordering criteria: {by}")
                return False

            conn = self._get_connection()
            cursor = conn.cursor()

            # Obtener favoritos ordenados por criterio
            order_clause = f"{by} DESC" if by != "label" else "label ASC"

            cursor.execute(f"""
                SELECT id FROM items
                WHERE is_favorite = 1
                ORDER BY {order_clause}
            """)

            results = cursor.fetchall()
            item_ids = [row['id'] for row in results]

            # Actualizar orden
            for order, item_id in enumerate(item_ids, start=1):
                cursor.execute("""
                    UPDATE items
                    SET favorite_order = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (order, item_id))

            conn.commit()
            conn.close()

            logger.info(f"Auto-ordered {len(item_ids)} favorites by {by}")
            return True

        except Exception as e:
            logger.error(f"Error auto-ordering favorites: {e}")
            return False

    # ==================== Análisis ====================

    def get_next_order_index(self) -> int:
        """Obtener siguiente índice de orden disponible"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MAX(favorite_order) as max_order
                FROM items
                WHERE is_favorite = 1
            """)

            result = cursor.fetchone()
            conn.close()

            max_order = result['max_order'] if result and result['max_order'] else 0
            return max_order + 1

        except Exception as e:
            logger.error(f"Error getting next order index: {e}")
            return 1

    def get_favorite_stats(self) -> Dict:
        """Estadísticas de favoritos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total favoritos
            cursor.execute("SELECT COUNT(*) as total FROM items WHERE is_favorite = 1")
            total = cursor.fetchone()['total']

            # Favorito más usado
            cursor.execute("""
                SELECT id, label, badge, use_count
                FROM items
                WHERE is_favorite = 1
                ORDER BY use_count DESC
                LIMIT 1
            """)
            most_used = cursor.fetchone()

            # Favorito menos usado
            cursor.execute("""
                SELECT id, label, badge, use_count
                FROM items
                WHERE is_favorite = 1
                ORDER BY use_count ASC
                LIMIT 1
            """)
            least_used = cursor.fetchone()

            # Uso promedio
            cursor.execute("""
                SELECT AVG(use_count) as avg_use
                FROM items
                WHERE is_favorite = 1
            """)
            avg_use = cursor.fetchone()['avg_use'] or 0

            conn.close()

            return {
                'total': total,
                'most_used': dict(most_used) if most_used else None,
                'least_used': dict(least_used) if least_used else None,
                'average_use': round(avg_use, 2)
            }

        except Exception as e:
            logger.error(f"Error getting favorite stats: {e}")
            return {
                'total': 0,
                'most_used': None,
                'least_used': None,
                'average_use': 0
            }

    def clear_all_favorites(self) -> int:
        """Quitar todos los favoritos (retorna cantidad removida)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Contar antes de limpiar
            cursor.execute("SELECT COUNT(*) as count FROM items WHERE is_favorite = 1")
            count = cursor.fetchone()['count']

            # Limpiar
            cursor.execute("""
                UPDATE items
                SET is_favorite = 0,
                    favorite_order = 0,
                    updated_at = datetime('now')
                WHERE is_favorite = 1
            """)

            conn.commit()
            conn.close()

            logger.info(f"Cleared {count} favorites")
            return count

        except Exception as e:
            logger.error(f"Error clearing favorites: {e}")
            return 0
