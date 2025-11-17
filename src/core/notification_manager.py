"""
Notification Manager - Gestor de notificaciones y sugerencias inteligentes
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """Gestor de notificaciones y sugerencias inteligentes"""

    def __init__(self, db_path: str = "widget_sidebar.db"):
        """Inicializar manager"""
        self.db_path = db_path

    def get_pending_notifications(self) -> List[Dict]:
        """Obtener notificaciones pendientes"""
        notifications = []

        try:
            # Importar managers
            from core.stats_manager import StatsManager
            from core.favorites_manager import FavoritesManager

            stats_manager = StatsManager(self.db_path)
            favorites_manager = FavoritesManager(self.db_path)

            # 1. Sugerencia de favoritos
            suggested_favs = stats_manager.suggest_favorites(limit=3)
            if suggested_favs:
                notifications.append({
                    'type': 'suggestion',
                    'category': 'favorites',
                    'title': '💡 Sugerencia de Favoritos',
                    'message': f"Tienes {len(suggested_favs)} items muy usados que podrían ser favoritos",
                    'action': 'show_favorite_suggestions',
                    'priority': 'medium',
                    'data': suggested_favs
                })

            # 2. Items nunca usados
            never_used = stats_manager.get_never_used_items()
            if len(never_used) > 5:
                notifications.append({
                    'type': 'alert',
                    'category': 'cleanup',
                    'title': '🧹 Items sin Usar',
                    'message': f"Tienes {len(never_used)} items que nunca has usado. ¿Eliminarlos?",
                    'action': 'show_cleanup_suggestions',
                    'priority': 'low',
                    'data': never_used
                })

            # 3. Items abandonados
            abandoned = stats_manager.get_abandoned_items(days_threshold=60, min_use_count=3)
            if len(abandoned) > 3:
                notifications.append({
                    'type': 'info',
                    'category': 'abandoned',
                    'title': '📦 Items Abandonados',
                    'message': f"{len(abandoned)} items que antes usabas ya no los ejecutas",
                    'action': 'show_abandoned_items',
                    'priority': 'low',
                    'data': abandoned
                })

            # 4. Items con errores frecuentes
            failing_items = self._get_failing_items(min_executions=10, min_error_rate=30)
            if failing_items:
                notifications.append({
                    'type': 'warning',
                    'category': 'errors',
                    'title': '⚠️ Items con Errores',
                    'message': f"{len(failing_items)} items fallan frecuentemente. ¿Revisarlos?",
                    'action': 'show_failing_items',
                    'priority': 'high',
                    'data': failing_items
                })

            # 5. Items lentos
            slow_items = self._get_slow_items(min_executions=10, min_avg_time_seconds=5)
            if slow_items:
                avg_time = sum(i['avg_time_seconds'] for i in slow_items) / len(slow_items)
                notifications.append({
                    'type': 'info',
                    'category': 'performance',
                    'title': '🐌 Items Lentos',
                    'message': f"{len(slow_items)} items tardan más de 5 segundos en ejecutar",
                    'action': 'show_slow_items',
                    'priority': 'medium',
                    'data': slow_items
                })

            # 6. Items populares sin atajos
            popular_no_shortcuts = self._get_popular_items_without_shortcuts(min_use_count=30)
            if popular_no_shortcuts:
                notifications.append({
                    'type': 'suggestion',
                    'category': 'shortcuts',
                    'title': '⌨️ Asignar Atajos',
                    'message': f"{len(popular_no_shortcuts)} items populares sin atajos de teclado",
                    'action': 'show_shortcut_suggestions',
                    'priority': 'low',
                    'data': popular_no_shortcuts
                })

            # Ordenar por prioridad
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            notifications.sort(key=lambda x: priority_order.get(x['priority'], 3))

            logger.info(f"Generated {len(notifications)} notifications")
            return notifications

        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []

    def _get_failing_items(self, min_executions: int = 10, min_error_rate: int = 30) -> List[Dict]:
        """Obtener items con alta tasa de error"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    i.id,
                    i.label,
                    i.badge,
                    COUNT(h.id) as total_executions,
                    SUM(CASE WHEN h.success = 0 THEN 1 ELSE 0 END) as error_count,
                    ROUND(100.0 * SUM(CASE WHEN h.success = 0 THEN 1 ELSE 0 END) / COUNT(h.id), 1) as error_rate
                FROM items i
                JOIN item_usage_history h ON i.id = h.item_id
                GROUP BY i.id
                HAVING total_executions >= ? AND error_rate >= ?
                ORDER BY error_rate DESC
                LIMIT 10
            """, (min_executions, min_error_rate))

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row['id'],
                    'label': row['label'],
                    'badge': row['badge'],
                    'total_executions': row['total_executions'],
                    'error_count': row['error_count'],
                    'error_rate': row['error_rate']
                })

            conn.close()
            return items

        except Exception as e:
            logger.error(f"Error getting failing items: {e}")
            return []

    def _get_slow_items(self, min_executions: int = 10, min_avg_time_seconds: float = 5.0) -> List[Dict]:
        """Obtener items con tiempo de ejecución lento"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    i.id,
                    i.label,
                    i.badge,
                    COUNT(h.id) as executions,
                    ROUND(AVG(h.execution_time_ms) / 1000.0, 2) as avg_time_seconds
                FROM items i
                JOIN item_usage_history h ON i.id = h.item_id
                WHERE h.success = 1
                GROUP BY i.id
                HAVING executions >= ? AND avg_time_seconds >= ?
                ORDER BY avg_time_seconds DESC
                LIMIT 10
            """, (min_executions, min_avg_time_seconds))

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row['id'],
                    'label': row['label'],
                    'badge': row['badge'],
                    'executions': row['executions'],
                    'avg_time_seconds': row['avg_time_seconds']
                })

            conn.close()
            return items

        except Exception as e:
            logger.error(f"Error getting slow items: {e}")
            return []

    def _get_popular_items_without_shortcuts(self, min_use_count: int = 30) -> List[Dict]:
        """Obtener items populares sin atajos asignados"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    label,
                    badge,
                    use_count
                FROM items
                WHERE use_count >= ?
                  AND (shortcut IS NULL OR shortcut = '')
                ORDER BY use_count DESC
                LIMIT 10
            """, (min_use_count,))

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row['id'],
                    'label': row['label'],
                    'badge': row['badge'],
                    'use_count': row['use_count']
                })

            conn.close()
            return items

        except Exception as e:
            logger.error(f"Error getting items without shortcuts: {e}")
            return []

    def should_show_notification(self, category: str, days_since_last: int = 7) -> bool:
        """
        Verificar si se debe mostrar una notificación

        Args:
            category: Categoría de notificación ('favorites', 'cleanup', etc.)
            days_since_last: Días mínimos desde última notificación de esta categoría

        Returns:
            bool: True si se debe mostrar
        """
        # TODO: Implementar sistema de tracking de notificaciones mostradas
        # Por ahora siempre retorna True, pero en el futuro debería:
        # 1. Guardar timestamp de última notificación por categoría
        # 2. Verificar que hayan pasado suficientes días
        # 3. Permitir que el usuario desactive ciertas categorías

        return True

    def dismiss_notification(self, notification_id: str):
        """
        Marcar notificación como descartada

        Args:
            notification_id: ID único de la notificación
        """
        # TODO: Implementar persistencia de notificaciones descartadas
        pass

    def get_notification_settings(self) -> Dict:
        """
        Obtener configuración de notificaciones

        Returns:
            Dict con configuración (categorías habilitadas, frecuencia, etc.)
        """
        # TODO: Implementar sistema de configuración de notificaciones
        return {
            'enabled': True,
            'enabled_categories': ['favorites', 'cleanup', 'abandoned', 'errors', 'performance', 'shortcuts'],
            'min_days_between': 7,
            'max_notifications_per_session': 2
        }

    def update_notification_settings(self, settings: Dict):
        """
        Actualizar configuración de notificaciones

        Args:
            settings: Diccionario con nueva configuración
        """
        # TODO: Implementar persistencia de configuración
        pass
