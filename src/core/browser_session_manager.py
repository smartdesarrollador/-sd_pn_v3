"""
Browser Session Manager - Gestiona sesiones del navegador
Author: Widget Sidebar Team
Date: 2025-11-03
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BrowserSessionManager:
    """Manager para gestionar sesiones del navegador embebido."""

    def __init__(self, db_manager):
        """
        Inicializa el manager de sesiones.

        Args:
            db_manager: Instancia de DBManager
        """
        self.db = db_manager

    def save_current_session(self, tabs_data: List[Dict], name: str = None, is_auto_save: bool = False) -> Optional[int]:
        """
        Guarda la sesión actual del navegador.

        Args:
            tabs_data: Lista de pestañas [{url, title, position, is_active}]
            name: Nombre personalizado para la sesión (opcional)
            is_auto_save: Si es auto-guardado

        Returns:
            ID de la sesión creada o None
        """
        # Generar nombre automático si no se proporciona
        if name is None:
            if is_auto_save:
                name = "Última sesión"
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                name = f"Sesión {timestamp}"

        # Guardar sesión en la base de datos
        session_id = self.db.save_session(name, tabs_data, is_auto_save)

        if session_id:
            logger.info(f"Sesión guardada: {name} (ID: {session_id})")
        else:
            logger.error("Error al guardar sesión")

        return session_id

    def restore_session(self, session_id: int) -> Optional[List[Dict]]:
        """
        Restaura una sesión del navegador.

        Args:
            session_id: ID de la sesión a restaurar

        Returns:
            Lista de pestañas de la sesión o None
        """
        tabs = self.db.get_session_tabs(session_id)

        if tabs:
            logger.info(f"Sesión {session_id} restaurada con {len(tabs)} pestañas")
        else:
            logger.warning(f"No se encontraron pestañas para la sesión {session_id}")

        return tabs

    def restore_last_session(self) -> Optional[List[Dict]]:
        """
        Restaura la última sesión guardada automáticamente.

        Returns:
            Lista de pestañas de la última sesión o None
        """
        last_session = self.db.get_last_auto_save_session()

        if not last_session:
            logger.info("No hay sesión anterior para restaurar")
            return None

        return self.restore_session(last_session['id'])

    def get_all_sessions(self, include_auto_save: bool = False) -> List[Dict]:
        """
        Obtiene todas las sesiones guardadas.

        Args:
            include_auto_save: Si incluir sesiones de auto-guardado

        Returns:
            Lista de sesiones
        """
        sessions = self.db.get_sessions(include_auto_save)
        logger.debug(f"Obtenidas {len(sessions)} sesiones")
        return sessions

    def delete_session(self, session_id: int) -> bool:
        """
        Elimina una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            True si se eliminó correctamente
        """
        success = self.db.delete_session(session_id)

        if success:
            logger.info(f"Sesión {session_id} eliminada")
        else:
            logger.error(f"Error al eliminar sesión {session_id}")

        return success

    def rename_session(self, session_id: int, new_name: str) -> bool:
        """
        Renombra una sesión.

        Args:
            session_id: ID de la sesión
            new_name: Nuevo nombre

        Returns:
            True si se renombró correctamente
        """
        if not new_name or not new_name.strip():
            logger.warning("Nombre de sesión vacío")
            return False

        success = self.db.rename_session(session_id, new_name.strip())

        if success:
            logger.info(f"Sesión {session_id} renombrada a: {new_name}")
        else:
            logger.error(f"Error al renombrar sesión {session_id}")

        return success

    def get_session_details(self, session_id: int) -> Optional[Dict]:
        """
        Obtiene detalles completos de una sesión incluyendo sus pestañas.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con información de la sesión y sus pestañas
        """
        sessions = self.db.get_sessions(include_auto_save=True)
        session = next((s for s in sessions if s['id'] == session_id), None)

        if not session:
            logger.warning(f"Sesión {session_id} no encontrada")
            return None

        tabs = self.db.get_session_tabs(session_id)
        session['tabs'] = tabs

        return session

    def auto_save_on_close(self, tabs_data: List[Dict]) -> Optional[int]:
        """
        Guarda automáticamente la sesión actual al cerrar el navegador.

        Args:
            tabs_data: Lista de pestañas activas

        Returns:
            ID de la sesión guardada o None
        """
        # Solo auto-guardar si hay pestañas
        if not tabs_data:
            logger.debug("No hay pestañas para auto-guardar")
            return None

        return self.save_current_session(tabs_data, is_auto_save=True)
