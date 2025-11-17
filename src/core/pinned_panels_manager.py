"""
Pinned Panels Manager
Manages the business logic for pinned panel persistence and management
"""

from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)


class PinnedPanelsManager:
    """Manager for pinned panel persistence and management"""

    def __init__(self, db_manager):
        """
        Initialize the pinned panels manager

        Args:
            db_manager: DBManager instance for database operations
        """
        self.db = db_manager
        logger.info("PinnedPanelsManager initialized")

    def _serialize_filter_config(self, panel_widget) -> Optional[str]:
        """
        Serialize panel's filter configuration to JSON string

        Args:
            panel_widget: FloatingPanel widget instance

        Returns:
            str: JSON string of filter configuration, or None if no filters
        """
        try:
            # Extract search text safely
            search_text = ""
            if hasattr(panel_widget, 'search_bar') and panel_widget.search_bar:
                if hasattr(panel_widget.search_bar, 'search_input'):
                    search_text = panel_widget.search_bar.search_input.text()

            filter_config = {
                "advanced_filters": getattr(panel_widget, 'current_filters', {}),
                "state_filter": getattr(panel_widget, 'current_state_filter', 'normal'),
                "search_text": search_text
            }

            # Only save if there's actual filter data
            has_filters = (
                filter_config["advanced_filters"] or
                filter_config["state_filter"] != "normal" or
                filter_config["search_text"]
            )

            if has_filters:
                logger.debug(f"Serializing filter config: {filter_config}")
                return json.dumps(filter_config)

            logger.debug("No filters to serialize")
            return None

        except Exception as e:
            logger.error(f"Could not serialize filter config: {e}", exc_info=True)
            return None

    def _deserialize_filter_config(self, filter_config_json: Optional[str]) -> Optional[Dict]:
        """
        Deserialize filter configuration from JSON string

        Args:
            filter_config_json: JSON string from database

        Returns:
            dict: Filter configuration dict, or None if no filters saved
        """
        if not filter_config_json:
            logger.debug("No filter config to deserialize")
            return None

        try:
            filter_config = json.loads(filter_config_json)

            # Validate structure
            expected_keys = {'advanced_filters', 'state_filter', 'search_text'}
            if not all(key in filter_config for key in expected_keys):
                logger.warning(f"Filter config missing expected keys. Found: {filter_config.keys()}")
                # Add missing keys with defaults
                filter_config.setdefault('advanced_filters', {})
                filter_config.setdefault('state_filter', 'normal')
                filter_config.setdefault('search_text', '')

            logger.debug(f"Deserialized filter config: {filter_config}")
            return filter_config

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse filter config JSON: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error deserializing filter config: {e}", exc_info=True)
            return None

    def _get_next_available_shortcut(self) -> str:
        """
        Get next available keyboard shortcut for a panel

        Returns:
            str: Next available shortcut in format 'Ctrl+Shift+N' where N is 1-9
        """
        try:
            # Get all existing shortcuts
            all_panels = self.db.get_pinned_panels(active_only=False)
            existing_shortcuts = {panel.get('keyboard_shortcut') for panel in all_panels if panel.get('keyboard_shortcut')}

            # Try to assign shortcuts from Ctrl+Shift+1 to Ctrl+Shift+9
            for i in range(1, 10):
                shortcut = f"Ctrl+Shift+{i}"
                if shortcut not in existing_shortcuts:
                    logger.debug(f"Next available shortcut: {shortcut}")
                    return shortcut

            # If all 1-9 are taken, return None
            logger.warning("All keyboard shortcuts (Ctrl+Shift+1-9) are already in use")
            return None
        except Exception as e:
            logger.error(f"Error getting next available shortcut: {e}")
            return None

    def save_panel_state(self, panel_widget, category_id: int,
                        custom_name: str = None, custom_color: str = None,
                        keyboard_shortcut: str = None) -> int:
        """
        Save current state of a FloatingPanel to database

        Args:
            panel_widget: FloatingPanel widget instance
            category_id: ID of the category this panel displays
            custom_name: Custom name for the panel (optional)
            custom_color: Custom color for panel header (optional, hex format)
            keyboard_shortcut: Keyboard shortcut (optional, auto-assigned if None)

        Returns:
            int: Panel ID in database
        """
        try:
            # Auto-assign keyboard shortcut if not provided
            if keyboard_shortcut is None:
                keyboard_shortcut = self._get_next_available_shortcut()
                if keyboard_shortcut:
                    logger.info(f"Auto-assigned keyboard shortcut: {keyboard_shortcut}")

            # Serialize filter configuration
            filter_config = self._serialize_filter_config(panel_widget)

            panel_id = self.db.save_pinned_panel(
                category_id=category_id,
                x_pos=panel_widget.x(),
                y_pos=panel_widget.y(),
                width=panel_widget.width(),
                height=panel_widget.height(),
                is_minimized=getattr(panel_widget, 'is_minimized', False),
                custom_name=custom_name,
                custom_color=custom_color,
                filter_config=filter_config,
                keyboard_shortcut=keyboard_shortcut
            )
            logger.info(f"Panel state saved for category {category_id} (Panel ID: {panel_id}, Shortcut: {keyboard_shortcut})")
            return panel_id
        except Exception as e:
            logger.error(f"Failed to save panel state: {e}")
            raise

    def update_panel_state(self, panel_id: int, panel_widget, include_filters: bool = True):
        """
        Update panel position/size/filters in database

        Args:
            panel_id: Panel ID in database
            panel_widget: FloatingPanel widget instance
            include_filters: Whether to also update filter configuration (default True)
        """
        try:
            update_data = {
                'x_position': panel_widget.x(),
                'y_position': panel_widget.y(),
                'width': panel_widget.width(),
                'height': panel_widget.height(),
                'is_minimized': getattr(panel_widget, 'is_minimized', False)
            }

            # Include filter configuration if requested
            if include_filters:
                filter_config = self._serialize_filter_config(panel_widget)
                update_data['filter_config'] = filter_config

            self.db.update_pinned_panel(panel_id=panel_id, **update_data)
            logger.debug(f"Panel {panel_id} state updated (filters: {include_filters})")
        except Exception as e:
            logger.error(f"Failed to update panel state: {e}")
            raise

    def restore_panels_on_startup(self) -> List[Dict]:
        """
        Get all active panels to restore on application startup

        Returns:
            List[Dict]: List of panel dictionaries with configuration
        """
        try:
            panels = self.db.get_pinned_panels(active_only=True)
            logger.info(f"Retrieved {len(panels)} active panels for restoration")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve panels for restoration: {e}")
            return []

    def mark_panel_opened(self, panel_id: int):
        """
        Update statistics when panel is opened

        Args:
            panel_id: Panel ID in database
        """
        try:
            self.db.update_panel_last_opened(panel_id)
            logger.debug(f"Panel {panel_id} marked as opened")
        except Exception as e:
            logger.error(f"Failed to mark panel as opened: {e}")

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recently used panels for history dropdown

        Args:
            limit: Maximum number of panels to return (default: 10)

        Returns:
            List[Dict]: List of panel dictionaries ordered by last_opened
        """
        try:
            panels = self.db.get_recent_panels(limit=limit)
            logger.debug(f"Retrieved {len(panels)} recent panels")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve recent panels: {e}")
            return []

    def delete_panel(self, panel_id: int):
        """
        Remove panel from database

        Args:
            panel_id: Panel ID to delete
        """
        try:
            self.db.delete_pinned_panel(panel_id)
            logger.info(f"Panel {panel_id} deleted from database")
        except Exception as e:
            logger.error(f"Failed to delete panel: {e}")
            raise

    def archive_panel(self, panel_id: int):
        """
        Archive panel (mark as inactive) instead of deleting it

        Args:
            panel_id: Panel ID to archive
        """
        try:
            self.db.update_pinned_panel(panel_id, is_active=False)
            logger.info(f"Panel {panel_id} archived (marked as inactive)")
        except Exception as e:
            logger.error(f"Failed to archive panel: {e}")
            raise

    def restore_panel(self, panel_id: int):
        """
        Restore an archived panel (mark as active)

        Args:
            panel_id: Panel ID to restore
        """
        try:
            self.db.update_pinned_panel(panel_id, is_active=True)
            logger.info(f"Panel {panel_id} restored (marked as active)")
        except Exception as e:
            logger.error(f"Failed to restore panel: {e}")
            raise

    def cleanup_on_exit(self):
        """
        Mark all panels as inactive when app closes
        This allows us to know which panels were active in the last session
        """
        try:
            self.db.deactivate_all_panels()
            logger.info("All panels marked as inactive on application exit")
        except Exception as e:
            logger.error(f"Failed to cleanup panels on exit: {e}")

    def update_panel_customization(self, panel_id: int, custom_name: str = None,
                                   custom_color: str = None, keyboard_shortcut: str = None):
        """
        Update panel's custom name, color, and/or keyboard shortcut

        Args:
            panel_id: Panel ID to update
            custom_name: New custom name (None to keep unchanged)
            custom_color: New custom color in hex format (None to keep unchanged)
            keyboard_shortcut: New keyboard shortcut (None to keep unchanged)
        """
        try:
            kwargs = {}
            if custom_name is not None:
                kwargs['custom_name'] = custom_name
            if custom_color is not None:
                kwargs['custom_color'] = custom_color
            if keyboard_shortcut is not None:
                kwargs['keyboard_shortcut'] = keyboard_shortcut

            if kwargs:
                self.db.update_pinned_panel(panel_id, **kwargs)
                logger.info(f"Panel {panel_id} customization updated")
        except Exception as e:
            logger.error(f"Failed to update panel customization: {e}")
            raise

    def update_panel_minimize_state(self, panel_id: int, is_minimized: bool):
        """
        Actualizar estado minimizado de un panel

        Args:
            panel_id: Panel ID to update
            is_minimized: New minimized state
        """
        try:
            self.db.update_pinned_panel(panel_id, is_minimized=is_minimized)
            logger.info(f"Updated panel {panel_id} minimize state to: {is_minimized}")
        except Exception as e:
            logger.error(f"Failed to update minimize state: {e}")
            raise

    def get_panel_by_category(self, category_id: int) -> Optional[Dict]:
        """
        Check if an active panel for this category already exists

        Args:
            category_id: Category ID to check

        Returns:
            Optional[Dict]: Panel data if exists, None otherwise
        """
        try:
            panel = self.db.get_panel_by_category(category_id)
            if panel:
                logger.debug(f"Found existing panel for category {category_id}")
            return panel
        except Exception as e:
            logger.error(f"Failed to check panel by category: {e}")
            return None

    def get_all_panels(self, active_only: bool = False) -> List[Dict]:
        """
        Get all pinned panels

        Args:
            active_only: If True, only return active panels

        Returns:
            List[Dict]: List of all panel dictionaries
        """
        try:
            panels = self.db.get_pinned_panels(active_only=active_only)
            logger.debug(f"Retrieved {len(panels)} panels (active_only={active_only})")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve all panels: {e}")
            return []

    def get_panel_by_id(self, panel_id: int) -> Optional[Dict]:
        """
        Get specific panel by ID

        Args:
            panel_id: Panel ID to retrieve

        Returns:
            Optional[Dict]: Panel data if found, None otherwise
        """
        try:
            panel = self.db.get_panel_by_id(panel_id)
            if panel:
                logger.debug(f"Retrieved panel {panel_id}")
            else:
                logger.warning(f"Panel {panel_id} not found")
            return panel
        except Exception as e:
            logger.error(f"Failed to retrieve panel by ID: {e}")
            return None

    def has_panels(self) -> bool:
        """
        Check if there are any saved panels

        Returns:
            bool: True if at least one panel exists
        """
        try:
            panels = self.db.get_pinned_panels(active_only=False)
            return len(panels) > 0
        except Exception as e:
            logger.error(f"Failed to check if panels exist: {e}")
            return False

    # ========== GLOBAL SEARCH PANEL METHODS ==========

    def save_global_search_panel(self, panel_widget,
                                 custom_name: str = None, custom_color: str = None,
                                 keyboard_shortcut: str = None) -> int:
        """
        Save current state of a GlobalSearchPanel to database

        Args:
            panel_widget: GlobalSearchPanel widget instance
            custom_name: Custom name for the panel (optional, defaults to "Búsqueda Global")
            custom_color: Custom color for panel header (optional, hex format)
            keyboard_shortcut: Keyboard shortcut (optional, auto-assigned if None)

        Returns:
            int: Panel ID in database
        """
        try:
            # Auto-assign keyboard shortcut if not provided
            if keyboard_shortcut is None:
                keyboard_shortcut = self._get_next_available_shortcut()
                if keyboard_shortcut:
                    logger.info(f"Auto-assigned keyboard shortcut: {keyboard_shortcut}")

            # Extract search query
            search_query = ""
            if hasattr(panel_widget, 'search_bar') and panel_widget.search_bar:
                if hasattr(panel_widget.search_bar, 'search_input'):
                    search_query = panel_widget.search_bar.search_input.text()

            # Serialize advanced filters
            advanced_filters = None
            if hasattr(panel_widget, 'current_filters') and panel_widget.current_filters:
                advanced_filters = json.dumps(panel_widget.current_filters)

            # Get state filter
            state_filter = getattr(panel_widget, 'current_state_filter', 'normal')

            # Use custom name or default
            if not custom_name:
                custom_name = getattr(panel_widget, 'panel_name', 'Búsqueda Global')

            # Use custom color or default
            if not custom_color:
                custom_color = getattr(panel_widget, 'panel_color', '#ff6b00')

            panel_id = self.db.save_pinned_panel(
                category_id=None,  # No category for global search
                x_pos=panel_widget.x(),
                y_pos=panel_widget.y(),
                width=panel_widget.width(),
                height=panel_widget.height(),
                is_minimized=getattr(panel_widget, 'is_minimized', False),
                custom_name=custom_name,
                custom_color=custom_color,
                keyboard_shortcut=keyboard_shortcut,
                panel_type='global_search',
                search_query=search_query,
                advanced_filters=advanced_filters,
                state_filter=state_filter
            )
            logger.info(f"Global search panel saved (ID: {panel_id}, Query: '{search_query}', State: {state_filter})")
            return panel_id
        except Exception as e:
            logger.error(f"Failed to save global search panel: {e}", exc_info=True)
            raise

    def get_global_search_panels(self, active_only: bool = True) -> List[Dict]:
        """
        Get all saved global search panels

        Args:
            active_only: If True, only return active panels (default)

        Returns:
            List[Dict]: List of global search panel dictionaries
        """
        try:
            all_panels = self.db.get_pinned_panels(active_only=active_only)
            # Filter for global_search type
            global_search_panels = [
                panel for panel in all_panels
                if panel.get('panel_type') == 'global_search'
            ]
            logger.debug(f"Retrieved {len(global_search_panels)} global search panels (active_only={active_only})")
            return global_search_panels
        except Exception as e:
            logger.error(f"Failed to retrieve global search panels: {e}")
            return []

    def restore_global_search_panel(self, panel_data: Dict) -> Dict:
        """
        Extract configuration from panel data for restoring a global search panel

        Args:
            panel_data: Panel dictionary from database

        Returns:
            Dict: Configuration dictionary for reconstructing the panel with keys:
                - panel_id: Panel ID
                - custom_name: Panel name
                - custom_color: Panel header color
                - keyboard_shortcut: Keyboard shortcut
                - search_query: Search text to restore
                - advanced_filters: Advanced filters dict (deserialized from JSON)
                - state_filter: State filter value
                - position: (x, y) tuple
                - size: (width, height) tuple
                - is_minimized: Minimized state
        """
        try:
            # Deserialize advanced filters if present
            advanced_filters = {}
            if panel_data.get('advanced_filters'):
                try:
                    advanced_filters = json.loads(panel_data['advanced_filters'])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse advanced filters: {e}")

            config = {
                'panel_id': panel_data['id'],
                'custom_name': panel_data.get('custom_name', 'Búsqueda Global'),
                'custom_color': panel_data.get('custom_color', '#ff6b00'),
                'keyboard_shortcut': panel_data.get('keyboard_shortcut'),
                'search_query': panel_data.get('search_query', ''),
                'advanced_filters': advanced_filters,
                'state_filter': panel_data.get('state_filter', 'normal'),
                'position': (panel_data['x_position'], panel_data['y_position']),
                'size': (panel_data['width'], panel_data['height']),
                'is_minimized': panel_data.get('is_minimized', False)
            }

            logger.debug(f"Restored config for global search panel {config['panel_id']}")
            return config

        except Exception as e:
            logger.error(f"Failed to restore global search panel config: {e}", exc_info=True)
            raise
