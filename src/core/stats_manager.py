"""
Stats Manager - Estadísticas y análisis de items
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class StatsManager:
    """Gestor de estadísticas y análisis de items"""

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

    # ==================== Items Populares ====================

    def get_most_used_items(self, limit: int = 10, days: Optional[int] = None, period: Optional[str] = None) -> List[Dict]:
        """Items más usados (global o en X días)

        Args:
            limit: Número máximo de items a retornar
            days: Número de días hacia atrás (para compatibilidad)
            period: Período de tiempo ('today', 'week', 'month', 'all') o None para global
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Mapear period a days si se especifica period
            if period:
                period_map = {
                    'today': 1,
                    'week': 7,
                    'month': 30,
                    'all': None
                }
                days = period_map.get(period, None)

            if days:
                # Uso reciente
                cursor.execute("""
                    SELECT i.*, COUNT(h.id) as recent_uses
                    FROM items i
                    LEFT JOIN item_usage_history h ON i.id = h.item_id
                        AND h.used_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY i.id
                    ORDER BY recent_uses DESC, i.use_count DESC
                    LIMIT ?
                """, (days, limit))
            else:
                # Global
                cursor.execute("""
                    SELECT * FROM items
                    WHERE use_count > 0
                    ORDER BY use_count DESC, last_used DESC
                    LIMIT ?
                """, (limit,))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting most used items: {e}")
            return []

    def get_trending_items(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Items en tendencia (más uso reciente vs histórico)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT i.*,
                       COUNT(h.id) as recent_uses,
                       CASE
                           WHEN i.use_count > 0
                           THEN ROUND(100.0 * COUNT(h.id) / i.use_count, 2)
                           ELSE 0
                       END as trend_percentage
                FROM items i
                LEFT JOIN item_usage_history h ON i.id = h.item_id
                    AND h.used_at >= datetime('now', '-' || ? || ' days')
                WHERE i.use_count > 0
                GROUP BY i.id
                HAVING recent_uses > 0
                ORDER BY trend_percentage DESC, recent_uses DESC
                LIMIT ?
            """, (days, limit))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting trending items: {e}")
            return []

    def get_top_items_by_category(self, category_id: int, limit: int = 5) -> List[Dict]:
        """Items más usados de una categoría"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM items
                WHERE category_id = ? AND use_count > 0
                ORDER BY use_count DESC, last_used DESC
                LIMIT ?
            """, (category_id, limit))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting top items by category: {e}")
            return []

    # ==================== Items Olvidados ====================

    def get_never_used_items(self) -> List[Dict]:
        """Items nunca usados"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *,
                       julianday('now') - julianday(created_at) as days_old
                FROM items
                WHERE use_count = 0 OR last_used IS NULL
                ORDER BY created_at DESC
            """)

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting never used items: {e}")
            return []

    def get_abandoned_items(self, days_threshold: int = 30, min_use_count: int = 3) -> List[Dict]:
        """Items abandonados (antes usados, ahora no)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *,
                       julianday('now') - julianday(last_used) as days_since_last_use
                FROM items
                WHERE use_count >= ?
                  AND last_used < datetime('now', '-' || ? || ' days')
                ORDER BY days_since_last_use DESC
            """, (min_use_count, days_threshold))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting abandoned items: {e}")
            return []

    def get_least_used_items(self, limit: int = 10) -> List[Dict]:
        """Items menos usados"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM items
                WHERE use_count > 0
                ORDER BY use_count ASC, created_at DESC
                LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting least used items: {e}")
            return []

    # ==================== Sugerencias Inteligentes ====================

    def suggest_favorites(self, limit: int = 5) -> List[Dict]:
        """Sugerir items que deberían ser favoritos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT i.*, COUNT(h.id) as uses_last_30_days
                FROM items i
                LEFT JOIN item_usage_history h ON i.id = h.item_id
                    AND h.used_at >= datetime('now', '-30 days')
                WHERE i.is_favorite = 0
                  AND i.use_count > 10
                GROUP BY i.id
                HAVING uses_last_30_days > 5
                ORDER BY uses_last_30_days DESC, i.use_count DESC
                LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error suggesting favorites: {e}")
            return []

    def suggest_cleanup(self, days_threshold: int = 60) -> List[Dict]:
        """Sugerir items para eliminar"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *,
                       julianday('now') - julianday(created_at) as days_old
                FROM items
                WHERE use_count = 0
                  AND created_at < datetime('now', '-' || ? || ' days')
                ORDER BY days_old DESC
            """, (days_threshold,))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error suggesting cleanup: {e}")
            return []

    def suggest_shortcuts(self, limit: int = 5) -> List[Dict]:
        """Sugerir items para asignar atajos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM items
                WHERE (shortcut IS NULL OR shortcut = '')
                  AND (is_favorite = 1 OR use_count > 20)
                ORDER BY use_count DESC, is_favorite DESC
                LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error suggesting shortcuts: {e}")
            return []

    # ==================== Estadísticas Generales ====================

    def get_dashboard_stats(self) -> Dict:
        """Estadísticas para dashboard principal"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total items
            cursor.execute("SELECT COUNT(*) as total FROM items")
            total_items = cursor.fetchone()['total']

            # Total ejecuciones
            cursor.execute("SELECT COUNT(*) as total FROM item_usage_history")
            total_executions = cursor.fetchone()['total']

            # Ejecuciones hoy
            cursor.execute("""
                SELECT COUNT(*) as total FROM item_usage_history
                WHERE date(used_at) = date('now')
            """)
            executions_today = cursor.fetchone()['total']

            # Ejecuciones esta semana
            cursor.execute("""
                SELECT COUNT(*) as total FROM item_usage_history
                WHERE used_at >= datetime('now', '-7 days')
            """)
            executions_week = cursor.fetchone()['total']

            # Favoritos
            cursor.execute("SELECT COUNT(*) as total FROM items WHERE is_favorite = 1")
            favorites_count = cursor.fetchone()['total']

            # Tasa de éxito
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM item_usage_history
            """)
            result = cursor.fetchone()
            success_rate = 100.0
            if result['total'] > 0:
                success_rate = (result['successful'] / result['total']) * 100

            conn.close()

            return {
                'total_items': total_items,
                'total_executions': total_executions,
                'executions_today': executions_today,
                'executions_week': executions_week,
                'favorites_count': favorites_count,
                'success_rate': round(success_rate, 2)
            }

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                'total_items': 0,
                'total_executions': 0,
                'executions_today': 0,
                'executions_week': 0,
                'favorites_count': 0,
                'success_rate': 100.0
            }

    def get_productivity_stats(self, days: int = 7) -> Dict:
        """Estadísticas de productividad"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Días con actividad
            cursor.execute("""
                SELECT COUNT(DISTINCT date(used_at)) as active_days
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-' || ? || ' days')
            """, (days,))
            active_days = cursor.fetchone()['active_days']

            # Total ejecuciones
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-' || ? || ' days')
            """, (days,))
            total_executions = cursor.fetchone()['total']

            # Promedio por día
            avg_per_day = round(total_executions / days, 2) if days > 0 else 0

            # Tiempo total ahorrado (estimado en segundos)
            cursor.execute("""
                SELECT SUM(execution_time_ms) / 1000.0 as total_time
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-' || ? || ' days')
            """, (days,))
            result = cursor.fetchone()
            total_time = result['total_time'] if result['total_time'] else 0

            conn.close()

            return {
                'days': days,
                'active_days': active_days,
                'total_executions': total_executions,
                'avg_executions_per_day': avg_per_day,
                'total_time_seconds': round(total_time, 2),
                'total_time_minutes': round(total_time / 60, 2)
            }

        except Exception as e:
            logger.error(f"Error getting productivity stats: {e}")
            return {}

    def get_usage_by_category(self) -> List[Dict]:
        """Uso por categoría"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    c.name as category,
                    c.badge,
                    COUNT(i.id) as item_count,
                    SUM(i.use_count) as total_uses,
                    ROUND(100.0 * SUM(i.use_count) /
                        (SELECT SUM(use_count) FROM items WHERE use_count > 0), 2) as percentage
                FROM categories c
                LEFT JOIN items i ON c.id = i.category_id
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY total_uses DESC
            """)

            results = cursor.fetchall()
            conn.close()

            categories = [dict(row) for row in results]
            return categories

        except Exception as e:
            logger.error(f"Error getting usage by category: {e}")
            return []

    # ==================== Análisis de Rendimiento ====================

    def get_slowest_items(self, limit: int = 10, min_executions: int = 5) -> List[Dict]:
        """Items más lentos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT i.id, i.label, i.badge,
                       COUNT(h.id) as executions,
                       ROUND(AVG(h.execution_time_ms) / 1000.0, 2) as avg_time_seconds
                FROM items i
                JOIN item_usage_history h ON i.id = h.item_id
                WHERE h.success = 1
                GROUP BY i.id
                HAVING executions >= ?
                ORDER BY avg_time_seconds DESC
                LIMIT ?
            """, (min_executions, limit))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting slowest items: {e}")
            return []

    def get_most_failing_items(self, limit: int = 10, min_executions: int = 5) -> List[Dict]:
        """Items con mayor tasa de error"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT i.id, i.label, i.badge,
                       COUNT(h.id) as total_executions,
                       SUM(CASE WHEN h.success = 0 THEN 1 ELSE 0 END) as failures,
                       ROUND(100.0 * SUM(CASE WHEN h.success = 0 THEN 1 ELSE 0 END) / COUNT(h.id), 2) as error_rate
                FROM items i
                JOIN item_usage_history h ON i.id = h.item_id
                GROUP BY i.id
                HAVING total_executions >= ? AND error_rate > 5
                ORDER BY error_rate DESC, failures DESC
                LIMIT ?
            """, (min_executions, limit))

            results = cursor.fetchall()
            conn.close()

            items = [dict(row) for row in results]
            return items

        except Exception as e:
            logger.error(f"Error getting most failing items: {e}")
            return []

    def get_health_report(self) -> Dict:
        """Reporte de salud del widget"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total items
            cursor.execute("SELECT COUNT(*) as total FROM items")
            total_items = cursor.fetchone()['total']

            # Items activos (usados últimos 30 días)
            cursor.execute("""
                SELECT COUNT(*) as active FROM items
                WHERE last_used >= datetime('now', '-30 days')
            """)
            active_items = cursor.fetchone()['active']

            # Items favoritos
            cursor.execute("SELECT COUNT(*) as favs FROM items WHERE is_favorite = 1")
            favorites = cursor.fetchone()['favs']

            # Ejecuciones hoy
            cursor.execute("""
                SELECT COUNT(*) as total FROM item_usage_history
                WHERE date(used_at) = date('now')
            """)
            executions_today = cursor.fetchone()['total']

            # Tasa de éxito hoy
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM item_usage_history
                WHERE date(used_at) = date('now')
            """)
            result = cursor.fetchone()
            success_rate_today = 100.0
            if result['total'] > 0:
                success_rate_today = (result['successful'] / result['total']) * 100

            # Items problemáticos
            cursor.execute("""
                SELECT COUNT(DISTINCT item_id) as problematic
                FROM (
                    SELECT item_id,
                           ROUND(100.0 * SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as error_rate
                    FROM item_usage_history
                    GROUP BY item_id
                    HAVING COUNT(*) >= 5 AND error_rate > 10
                )
            """)
            problematic_items = cursor.fetchone()['problematic']

            conn.close()

            # Calcular health score (0-100)
            health_score = 100
            if total_items > 0:
                active_percentage = (active_items / total_items) * 100
                if active_percentage < 50:
                    health_score -= 20
                elif active_percentage < 70:
                    health_score -= 10

            if success_rate_today < 90:
                health_score -= 15
            elif success_rate_today < 95:
                health_score -= 5

            if problematic_items > 3:
                health_score -= 15
            elif problematic_items > 0:
                health_score -= 5

            return {
                'health_score': max(0, health_score),
                'total_items': total_items,
                'active_items': active_items,
                'favorites': favorites,
                'executions_today': executions_today,
                'success_rate_today': round(success_rate_today, 2),
                'problematic_items': problematic_items,
                'status': 'excellent' if health_score >= 90 else 'good' if health_score >= 70 else 'warning' if health_score >= 50 else 'critical'
            }

        except Exception as e:
            logger.error(f"Error getting health report: {e}")
            return {}
