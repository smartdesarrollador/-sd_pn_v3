"""
Category Model
"""
from typing import List, Optional, Dict, Any
from .item import Item


class Category:
    """Model representing a category of items"""

    def __init__(
        self,
        category_id: str,
        name: str,
        icon: str = "",
        order_index: int = 0,
        is_active: bool = True,
        is_predefined: bool = False,
        color: Optional[str] = None,
        badge: Optional[str] = None
    ):
        self.id = category_id
        self.name = name
        self.icon = icon
        self.order_index = order_index
        self.is_active = is_active
        self.is_predefined = is_predefined
        self.color = color
        self.badge = badge
        self.items: List[Item] = []

        # Atributos extendidos (para filtros avanzados)
        self.item_count: int = 0
        self.total_uses: int = 0
        self.last_accessed: Optional[str] = None
        self.access_count: int = 0
        self.is_pinned: bool = False
        self.pinned_order: int = 0
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None

    def add_item(self, item: Item) -> None:
        """Add an item to this category"""
        if item not in self.items:
            self.items.append(item)

    def remove_item(self, item_id: str) -> bool:
        """Remove an item by ID. Returns True if found and removed."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                return True
        return False

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def validate(self) -> bool:
        """Validate category data"""
        if not self.id or not self.name:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "order_index": self.order_index,
            "is_active": self.is_active,
            "is_predefined": self.is_predefined,
            "color": self.color,
            "badge": self.badge,
            "item_count": self.item_count,
            "total_uses": self.total_uses,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "is_pinned": self.is_pinned,
            "pinned_order": self.pinned_order,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Create a Category from a dictionary"""
        category = cls(
            category_id=data.get("id", ""),
            name=data.get("name", ""),
            icon=data.get("icon", ""),
            order_index=data.get("order_index", data.get("order", 0)),  # Backward compatible
            is_active=data.get("is_active", True),
            is_predefined=data.get("is_predefined", False),
            color=data.get("color"),
            badge=data.get("badge")
        )

        # Cargar atributos extendidos
        category.item_count = data.get("item_count", 0)
        category.total_uses = data.get("total_uses", 0)
        category.last_accessed = data.get("last_accessed")
        category.access_count = data.get("access_count", 0)
        category.is_pinned = data.get("is_pinned", False)
        category.pinned_order = data.get("pinned_order", 0)
        category.created_at = data.get("created_at")
        category.updated_at = data.get("updated_at")

        # Load items
        items_data = data.get("items", [])
        for item_data in items_data:
            item = Item.from_dict(item_data)
            category.add_item(item)

        return category

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name}, items={len(self.items)})"
