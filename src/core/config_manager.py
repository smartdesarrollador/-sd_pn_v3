"""
Config Manager - SQLite Version
Manages application configuration using SQLite database
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from models.item import Item, ItemType
from database.db_manager import DBManager
from core.encryption_manager import EncryptionManager


class ConfigManager:
    """Manages application configuration using SQLite"""

    def __init__(self, db_path: Optional[str] = None, base_dir: Optional[Path] = None):
        """
        Initialize ConfigManager with SQLite database

        Args:
            db_path: Path to SQLite database file (optional)
            base_dir: Base directory for application (optional, for compatibility)
        """
        # Determine base directory (for exe compatibility)
        if base_dir:
            self.base_dir = Path(base_dir)
        elif getattr(sys, 'frozen', False):
            # Running as a bundled exe
            self.base_dir = Path(sys.executable).parent
        else:
            # Running as a script
            self.base_dir = Path(__file__).parent.parent.parent

        # Determine database path
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = str(self.base_dir / "widget_sidebar.db")

        # Initialize database manager
        self.db = DBManager(self.db_path)

        # Initialize encryption manager
        env_path = str(self.base_dir / ".env")
        self.encryption_manager = EncryptionManager(env_path)

        # Cache for categories
        self._categories_cache: Optional[List[Category]] = None

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from database (for backward compatibility)

        Returns:
            Dict containing settings
        """
        return {"settings": self.db.get_all_settings()}

    def save_config(self) -> bool:
        """
        Save configuration to database (for backward compatibility)

        Returns:
            bool: True if successful
        """
        # Settings are saved immediately when set_setting() is called
        # This method exists for backward compatibility
        return True

    def load_default_categories(self) -> List[Category]:
        """
        Load categories from database

        Returns:
            List[Category]: List of all categories
        """
        return self.get_categories()

    def get_categories(self) -> List[Category]:
        """
        Get all active categories with their items

        Returns:
            List[Category]: List of Category objects
        """
        # Return cached categories if available
        if self._categories_cache is not None:
            return self._categories_cache

        # Load from database
        categories_data = self.db.get_categories(include_inactive=False)
        categories = []

        for cat_data in categories_data:
            # Convert database dict to Category object
            category = self._dict_to_category(cat_data)

            # Load items for this category
            items_data = self.db.get_items_by_category(cat_data['id'])
            for item_data in items_data:
                item = self._dict_to_item(item_data)
                category.add_item(item)

            categories.append(category)

        # Cache results
        self._categories_cache = categories
        return categories

    def get_category(self, category_id) -> Optional[Category]:
        """
        Get a specific category by ID

        Args:
            category_id: Category ID (can be string or int)

        Returns:
            Optional[Category]: Category object or None
        """
        # Try to get from database
        try:
            # Convert to int if it's a string
            if isinstance(category_id, str):
                if category_id.isdigit():
                    cat_id = int(category_id)
                else:
                    # Search by old string ID
                    categories = self.get_categories()
                    for cat in categories:
                        if cat.id == category_id:
                            return cat
                    return None
            else:
                cat_id = int(category_id)

            cat_data = self.db.get_category(cat_id)
            if not cat_data:
                return None

            category = self._dict_to_category(cat_data)

            # Load items
            items_data = self.db.get_items_by_category(cat_id)
            for item_data in items_data:
                item = self._dict_to_item(item_data)
                category.add_item(item)

            return category

        except (ValueError, TypeError):
            return None

    def add_category(self, category: Category) -> bool:
        """
        Add a new category

        Args:
            category: Category object to add

        Returns:
            bool: True if successful
        """
        if not category.validate():
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Category validation failed: {category.name}")
            return False

        try:
            import logging
            logger = logging.getLogger(__name__)

            # Add category to database WITH order_index
            cat_id = self.db.add_category(
                name=category.name,
                icon=category.icon,
                is_predefined=category.is_predefined,
                order_index=category.order_index  # FIX: Pass order_index
            )
            logger.info(f"[ConfigManager] Category added to DB: {category.name} (ID: {cat_id}, order_index: {category.order_index})")

            # Add items
            for item in category.items:
                item_id = self.db.add_item(
                    category_id=cat_id,
                    label=item.label,
                    content=item.content,
                    item_type=item.type.value.upper(),
                    icon=item.icon,
                    is_sensitive=item.is_sensitive,
                    is_favorite=getattr(item, 'is_favorite', False),  # FIX: Add is_favorite
                    tags=item.tags,
                    description=item.description,
                    working_dir=getattr(item, 'working_dir', None),
                    color=getattr(item, 'color', None),  # FIX: Add color
                    is_active=getattr(item, 'is_active', True),  # Add is_active (default True)
                    is_archived=getattr(item, 'is_archived', False)  # Add is_archived (default False)
                )
                logger.info(f"  [ConfigManager] Item added: {item.label} (ID: {item_id})")

            # Clear cache
            self._categories_cache = None
            return True

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            error_msg = f"ERROR ADDING CATEGORY '{category.name}': {type(e).__name__}: {str(e)}"
            logger.critical("=" * 80)
            logger.critical(error_msg)
            logger.critical("Full traceback:")
            logger.critical(traceback.format_exc())
            logger.critical("=" * 80)
            print("\n" + "="*80)
            print(error_msg)
            print("Full traceback:")
            print(traceback.format_exc())
            print("="*80 + "\n")
            return False

    def update_category(self, category_id: str, updated_category: Category) -> bool:
        """
        Update an existing category

        Args:
            category_id: Category ID to update
            updated_category: Updated Category object

        Returns:
            bool: True if successful
        """
        try:
            cat_id = int(category_id) if category_id.isdigit() else None
            if cat_id is None:
                return False

            # Update category metadata
            self.db.update_category(
                category_id=cat_id,
                name=updated_category.name,
                icon=updated_category.icon,
                order_index=updated_category.order_index,
                is_active=updated_category.is_active
            )

            # Update items (simple approach: delete all and re-add)
            # Get existing items
            existing_items = self.db.get_items_by_category(cat_id)
            for existing_item in existing_items:
                self.db.delete_item(existing_item['id'])

            # Add new items
            for item in updated_category.items:
                self.db.add_item(
                    category_id=cat_id,
                    label=item.label,
                    content=item.content,
                    item_type=item.type.value.upper(),
                    icon=item.icon,
                    is_sensitive=item.is_sensitive,
                    is_favorite=getattr(item, 'is_favorite', False),  # FIX: Add is_favorite
                    tags=item.tags,
                    description=item.description,
                    working_dir=getattr(item, 'working_dir', None),
                    color=getattr(item, 'color', None),  # FIX: Add color
                    is_active=getattr(item, 'is_active', True),  # Add is_active (default True)
                    is_archived=getattr(item, 'is_archived', False)  # Add is_archived (default False)
                )

            # Clear cache
            self._categories_cache = None
            return True

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating category: {e}", exc_info=True)
            print(f"Error updating category: {e}")
            return False

    def delete_category(self, category_id: str) -> bool:
        """
        Delete a category by ID

        Args:
            category_id: Category ID to delete

        Returns:
            bool: True if successful
        """
        try:
            cat_id = int(category_id) if category_id.isdigit() else None
            if cat_id is None:
                return False

            self.db.delete_category(cat_id)

            # Clear cache
            self._categories_cache = None
            return True

        except Exception as e:
            print(f"Error deleting category: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Any: Setting value
        """
        return self.db.get_setting(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a specific setting

        Args:
            key: Setting key
            value: Setting value

        Returns:
            bool: True if successful
        """
        try:
            self.db.set_setting(key, value)
            return True
        except Exception as e:
            print(f"Error setting value: {e}")
            return False

    def get_history(self, limit: int = 20) -> List[Dict]:
        """
        Get clipboard history

        Args:
            limit: Maximum number of entries

        Returns:
            List[Dict]: History entries
        """
        return self.db.get_history(limit)

    def add_to_history(self, content: str, item_id: Optional[int] = None) -> bool:
        """
        Add entry to clipboard history

        Args:
            content: Content to add
            item_id: Optional item ID

        Returns:
            bool: True if successful
        """
        try:
            self.db.add_to_history(item_id, content)
            return True
        except Exception as e:
            print(f"Error adding to history: {e}")
            return False

    def export_config(self, export_path: Path) -> bool:
        """
        Export configuration to JSON file

        Args:
            export_path: Path to export file

        Returns:
            bool: True if successful
        """
        try:
            # Get all data from database
            settings = self.db.get_all_settings()
            categories = self.get_categories()

            export_data = {
                "version": "3.0.0",
                "settings": settings,
                "categories": [cat.to_dict() for cat in categories]
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, import_path: Path) -> bool:
        """
        Import configuration from JSON file

        Args:
            import_path: Path to import file

        Returns:
            bool: True if successful
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Import settings
            settings = data.get('settings', {})
            for key, value in settings.items():
                self.db.set_setting(key, value)

            # Import categories
            categories_data = data.get('categories', [])
            for cat_data in categories_data:
                category = Category.from_dict(cat_data)
                if category.validate():
                    self.add_category(category)

            # Clear cache
            self._categories_cache = None
            return True

        except Exception as e:
            print(f"Error importing config: {e}")
            return False

    def save_categories(self, categories: List[Category]) -> bool:
        """
        Save all categories (bulk update)

        Args:
            categories: List of Category objects

        Returns:
            bool: True if successful
        """
        try:
            # This is a destructive operation - clear existing and re-add
            # Get all category IDs
            existing_cats = self.db.get_categories()

            # Delete non-predefined categories
            for cat in existing_cats:
                if not cat['is_predefined']:
                    self.db.delete_category(cat['id'])

            # Add new categories
            for category in categories:
                self.add_category(category)

            # Clear cache
            self._categories_cache = None
            return True

        except Exception as e:
            print(f"Error saving categories: {e}")
            return False

    def close(self):
        """Close database connection"""
        self.db.close()

    # ========== PRIVATE HELPER METHODS ==========

    def _dict_to_category(self, data: Dict) -> Category:
        """
        Convert database dict to Category object

        Args:
            data: Database row as dict

        Returns:
            Category: Category object
        """
        # Map database fields to Category constructor
        category = Category(
            category_id=str(data['id']),  # Convert to string for compatibility
            name=data['name'],
            icon=data.get('icon', ''),
            order_index=data.get('order_index', 0),
            is_active=bool(data.get('is_active', True)),
            is_predefined=bool(data.get('is_predefined', False)),
            color=data.get('color'),
            badge=data.get('badge')
        )

        # Set extended attributes
        category.item_count = data.get('item_count', 0)
        category.total_uses = data.get('total_uses', 0)
        category.last_accessed = data.get('last_accessed')
        category.access_count = data.get('access_count', 0)
        category.is_pinned = bool(data.get('is_pinned', False))
        category.pinned_order = data.get('pinned_order', 0)
        category.created_at = data.get('created_at')
        category.updated_at = data.get('updated_at')
        return category

    def _dict_to_item(self, data: Dict) -> Item:
        """
        Convert database dict to Item object

        Args:
            data: Database row as dict

        Returns:
            Item: Item object
        """
        # Map database type to ItemType enum
        type_str = data.get('type', 'TEXT').upper().lower()  # Convert from DB (TEXT/URL/CODE/PATH) to enum (text/url/code/path)
        try:
            item_type = ItemType(type_str)
        except ValueError:
            item_type = ItemType.TEXT

        item = Item(
            item_id=str(data['id']),  # Convert to string for compatibility
            label=data['label'],
            content=data['content'],
            item_type=item_type,
            icon=data.get('icon'),
            is_sensitive=bool(data.get('is_sensitive', False)),
            is_favorite=bool(data.get('is_favorite', False)),
            tags=data.get('tags', []),
            description=data.get('description'),
            working_dir=data.get('working_dir'),
            color=data.get('color'),
            is_active=bool(data.get('is_active', True)),  # Add is_active (default True)
            is_archived=bool(data.get('is_archived', False))  # Add is_archived (default False)
        )
        return item

    def _category_to_dict(self, category: Category) -> Dict:
        """
        Convert Category object to database dict

        Args:
            category: Category object

        Returns:
            Dict: Database-compatible dict
        """
        return {
            'name': category.name,
            'icon': category.icon,
            'order_index': category.order_index,
            'is_active': category.is_active
        }

    def _item_to_dict(self, item: Item, category_id: int) -> Dict:
        """
        Convert Item object to database dict

        Args:
            item: Item object
            category_id: Parent category ID

        Returns:
            Dict: Database-compatible dict
        """
        return {
            'category_id': category_id,
            'label': item.label,
            'content': item.content,
            'type': item.type.value.upper(),
            'icon': item.icon,
            'is_sensitive': item.is_sensitive,
            'tags': item.tags
        }

    # ==================== Files Configuration Methods ====================

    def get_files_base_path(self) -> str:
        """
        Get base path for file storage

        Returns:
            str: Base path for file storage (empty string if not configured)
        """
        return self.get_setting('files_base_path', '')

    def set_files_base_path(self, path: str) -> bool:
        """
        Set base path for file storage

        Args:
            path: Base directory path

        Returns:
            bool: True if successful
        """
        return self.set_setting('files_base_path', path)

    def get_files_folders_config(self) -> Dict[str, str]:
        """
        Get folders configuration for file types

        Returns:
            Dict[str, str]: Mapping of file types to folder names
        """
        default_config = {
            "VIDEOS": "VIDEOS",
            "IMAGENES": "IMAGENES",
            "PDFS": "PDFS",
            "WORDS": "WORDS",
            "EXCELS": "EXCELS",
            "TEXT": "TEXT",
            "OTROS": "OTROS"
        }

        config = self.get_setting('files_folders_config', default_config)

        # DBManager.get_setting auto-parses JSON, so config might already be a dict
        if isinstance(config, dict):
            return config
        elif isinstance(config, str):
            try:
                return json.loads(config)
            except json.JSONDecodeError:
                return default_config
        else:
            return default_config

    def set_files_folders_config(self, config: Dict[str, str]) -> bool:
        """
        Set folders configuration for file types

        Args:
            config: Dict mapping file types to folder names

        Returns:
            bool: True if successful
        """
        config_json = json.dumps(config)
        return self.set_setting('files_folders_config', config_json)

    def get_files_auto_create_folders(self) -> bool:
        """
        Get auto-create folders setting

        Returns:
            bool: True if folders should be created automatically
        """
        value = self.get_setting('files_auto_create_folders', 'true')
        return value.lower() == 'true' if isinstance(value, str) else bool(value)

    def set_files_auto_create_folders(self, auto_create: bool) -> bool:
        """
        Set auto-create folders setting

        Args:
            auto_create: True to auto-create folders, False otherwise

        Returns:
            bool: True if successful
        """
        value = 'true' if auto_create else 'false'
        return self.set_setting('files_auto_create_folders', value)

    # ======================================================================

    def __del__(self):
        """Cleanup: close database connection"""
        try:
            self.close()
        except:
            pass
