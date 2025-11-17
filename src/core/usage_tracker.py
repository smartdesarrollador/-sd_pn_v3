"""
Usage Tracker - Tracking de uso de items
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

import sqlite3
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UsageTracker:
    """Gestor de tracking de uso de items"""

    def __init__(self, db_path: str = "widget_sidebar.db"):
        """Inicializar tracker"""
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos con timeout aumentado"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)  # Aumentar timeout a 10 segundos
        conn.row_factory = sqlite3.Row
        # Configurar para mejorar concurrencia
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
        return conn

    # ==================== Registro de Uso ====================

    def track_usage(self, item_id: int, execution_time_ms: int = 0,
                    success: bool = True, error_message: Optional[str] = None) -> bool:
        """Registrar uso de un item con retry logic para evitar 'database is locked'"""
        max_retries = 3
        retry_delay = 0.1  # 100ms entre intentos

        for attempt in range(max_retries):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # 1. Incrementar use_count y actualizar last_used en items
                cursor.execute("""
                    UPDATE items
                    SET use_count = use_count + 1,
                        last_used = datetime('now'),
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (item_id,))

                # 2. Insertar registro en item_usage_history
                cursor.execute("""
                    INSERT INTO item_usage_history
                    (item_id, used_at, execution_time_ms, success, error_message)
                    VALUES (?, datetime('now'), ?, ?, ?)
                """, (item_id, execution_time_ms, 1 if success else 0, error_message))

                conn.commit()
                conn.close()

                logger.info(f"Tracked usage for item {item_id}: success={success}, time={execution_time_ms}ms")
                return True

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    # Retry en caso de database locked
                    logger.debug(f"Database locked, retry {attempt + 1}/{max_retries} for item {item_id}")
                    time.sleep(retry_delay * (attempt + 1))  # Backoff exponencial
                    continue
                else:
                    logger.error(f"Error tracking usage for item {item_id} after {attempt + 1} attempts: {e}")
                    return False
            except Exception as e:
                logger.error(f"Error tracking usage for item {item_id}: {e}")
                return False

        return False

    def track_execution_start(self, item_id: int) -> int:
        """Iniciar tracking de ejecución (retorna timestamp en ms)"""
        return int(time.time() * 1000)

    def track_execution_end(self, item_id: int, start_time: int,
                           success: bool = True, error: Optional[str] = None) -> bool:
        """Finalizar tracking de ejecución"""
        end_time = int(time.time() * 1000)
        execution_time = end_time - start_time

        return self.track_usage(item_id, execution_time, success, error)

    # ==================== Consultas Básicas ====================

    def get_use_count(self, item_id: int) -> int:
        """Obtener contador de usos de un item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT use_count FROM items WHERE id = ?
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            return result['use_count'] if result else 0

        except Exception as e:
            logger.error(f"Error getting use count for item {item_id}: {e}")
            return 0

    def get_last_used(self, item_id: int) -> Optional[str]:
        """Obtener fecha de último uso"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT last_used FROM items WHERE id = ?
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            return result['last_used'] if result else None

        except Exception as e:
            logger.error(f"Error getting last used for item {item_id}: {e}")
            return None

    # ==================== Historial ====================

    def get_usage_history(self, item_id: int, limit: int = 50) -> List[Dict]:
        """Obtener historial de uso de un item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM item_usage_history
                WHERE item_id = ?
                ORDER BY used_at DESC
                LIMIT ?
            """, (item_id, limit))

            results = cursor.fetchall()
            conn.close()

            history = [dict(row) for row in results]
            return history

        except Exception as e:
            logger.error(f"Error getting usage history for item {item_id}: {e}")
            return []

    def get_recent_history(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Obtener historial reciente de todos los items"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT h.*, i.label, i.badge
                FROM item_usage_history h
                JOIN items i ON h.item_id = i.id
                WHERE h.used_at >= datetime('now', '-' || ? || ' days')
                ORDER BY h.used_at DESC
                LIMIT ?
            """, (days, limit))

            results = cursor.fetchall()
            conn.close()

            history = [dict(row) for row in results]
            return history

        except Exception as e:
            logger.error(f"Error getting recent history: {e}")
            return []

    def get_today_usage(self) -> List[Dict]:
        """Obtener items usados hoy"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT h.*, i.label, i.badge
                FROM item_usage_history h
                JOIN items i ON h.item_id = i.id
                WHERE date(h.used_at) = date('now')
                ORDER BY h.used_at DESC
            """)

            results = cursor.fetchall()
            conn.close()

            history = [dict(row) for row in results]
            return history

        except Exception as e:
            logger.error(f"Error getting today usage: {e}")
            return []

    # ==================== Estadísticas ====================

    def get_total_executions(self) -> int:
        """Total de ejecuciones registradas"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as total FROM item_usage_history
            """)

            result = cursor.fetchone()
            conn.close()

            return result['total'] if result else 0

        except Exception as e:
            logger.error(f"Error getting total executions: {e}")
            return 0

    def get_total_executions_today(self) -> int:
        """Total de ejecuciones hoy"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as total
                FROM item_usage_history
                WHERE date(used_at) = date('now')
            """)

            result = cursor.fetchone()
            conn.close()

            return result['total'] if result else 0

        except Exception as e:
            logger.error(f"Error getting today executions: {e}")
            return 0

    def get_total_executions_week(self) -> int:
        """Total de ejecuciones esta semana"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as total
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-7 days')
            """)

            result = cursor.fetchone()
            conn.close()

            return result['total'] if result else 0

        except Exception as e:
            logger.error(f"Error getting week executions: {e}")
            return 0

    def get_average_execution_time(self, item_id: int) -> float:
        """Tiempo promedio de ejecución de un item (en segundos)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT AVG(execution_time_ms) as avg_time
                FROM item_usage_history
                WHERE item_id = ? AND success = 1
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            if result and result['avg_time']:
                return round(result['avg_time'] / 1000.0, 2)
            return 0.0

        except Exception as e:
            logger.error(f"Error getting average execution time for item {item_id}: {e}")
            return 0.0

    def get_success_rate(self, item_id: int) -> float:
        """Tasa de éxito de un item (0-100%)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM item_usage_history
                WHERE item_id = ?
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            if result and result['total'] > 0:
                return round((result['successful'] / result['total']) * 100, 2)
            return 100.0  # Si no hay registros, asumir 100%

        except Exception as e:
            logger.error(f"Error getting success rate for item {item_id}: {e}")
            return 100.0

    def get_error_count(self, item_id: int) -> int:
        """Cantidad de errores de un item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as errors
                FROM item_usage_history
                WHERE item_id = ? AND success = 0
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            return result['errors'] if result else 0

        except Exception as e:
            logger.error(f"Error getting error count for item {item_id}: {e}")
            return 0

    def get_last_error(self, item_id: int) -> Optional[Dict]:
        """Último error registrado de un item"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM item_usage_history
                WHERE item_id = ? AND success = 0
                ORDER BY used_at DESC
                LIMIT 1
            """, (item_id,))

            result = cursor.fetchone()
            conn.close()

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error getting last error for item {item_id}: {e}")
            return None

    # ==================== Análisis Temporal ====================

    def get_usage_by_hour(self, days: int = 7) -> List[Dict]:
        """Uso por hora del día"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    strftime('%H', used_at) as hour,
                    COUNT(*) as executions,
                    ROUND(AVG(execution_time_ms) / 1000.0, 2) as avg_time_seconds
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-' || ? || ' days')
                GROUP BY hour
                ORDER BY hour
            """, (days,))

            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting usage by hour: {e}")
            return []

    def get_usage_by_day(self, days: int = 30) -> List[Dict]:
        """Uso por día"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    date(used_at) as day,
                    COUNT(*) as executions,
                    COUNT(DISTINCT item_id) as unique_items,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
                FROM item_usage_history
                WHERE used_at >= datetime('now', '-' || ? || ' days')
                GROUP BY day
                ORDER BY day DESC
            """, (days,))

            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting usage by day: {e}")
            return []

    # ==================== Limpieza ====================

    def cleanup_old_history(self, days: int = 90) -> int:
        """Limpiar historial antiguo (retorna registros eliminados)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Contar antes de eliminar
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM item_usage_history
                WHERE used_at < datetime('now', '-' || ? || ' days')
            """, (days,))

            count = cursor.fetchone()['count']

            # Eliminar registros antiguos
            cursor.execute("""
                DELETE FROM item_usage_history
                WHERE used_at < datetime('now', '-' || ? || ' days')
            """, (days,))

            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {count} old history records")
            return count

        except Exception as e:
            logger.error(f"Error cleaning up old history: {e}")
            return 0

    def get_item_stats(self, item_id: int) -> Dict:
        """Estadísticas completas de un item"""
        try:
            return {
                'use_count': self.get_use_count(item_id),
                'last_used': self.get_last_used(item_id),
                'avg_execution_time': self.get_average_execution_time(item_id),
                'success_rate': self.get_success_rate(item_id),
                'error_count': self.get_error_count(item_id),
                'last_error': self.get_last_error(item_id)
            }

        except Exception as e:
            logger.error(f"Error getting item stats for {item_id}: {e}")
            return {}
