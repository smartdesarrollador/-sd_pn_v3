"""
Clipboard Manager
"""
import pyperclip
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.item import Item


class ClipboardHistory:
    """Simple history entry for clipboard operations"""
    def __init__(self, item: Item, timestamp: datetime):
        self.item = item
        self.timestamp = timestamp


class ClipboardManager:
    """Manages clipboard operations"""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history: List[ClipboardHistory] = []

    def copy_text(self, content: str) -> bool:
        """Copy text to clipboard"""
        try:
            pyperclip.copy(content)
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False

    def copy_item(self, item: Item) -> bool:
        """Copy an item's content to clipboard"""
        try:
            success = self.copy_text(item.content)
            if success:
                # Update item's last used timestamp
                item.update_last_used()
                # Add to history
                self.add_to_history(item)
            return success
        except Exception as e:
            print(f"Error copying item to clipboard: {e}")
            return False

    def get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return None

    def validate_url(self, url: str) -> bool:
        """Validate if a string is a URL"""
        return url.startswith(('http://', 'https://', 'www.', 'ftp://'))

    def add_to_history(self, item: Item) -> None:
        """Add item to clipboard history"""
        # Create history entry
        history_entry = ClipboardHistory(item, datetime.now())

        # Add to beginning of list
        self.history.insert(0, history_entry)

        # Keep only max_history items
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]

    def get_history(self, limit: Optional[int] = None) -> List[ClipboardHistory]:
        """Get clipboard history"""
        if limit is None:
            return self.history
        return self.history[:limit]

    def clear_history(self) -> None:
        """Clear clipboard history"""
        self.history.clear()

    def get_last_copied(self) -> Optional[Item]:
        """Get the last copied item"""
        if self.history:
            return self.history[0].item
        return None
