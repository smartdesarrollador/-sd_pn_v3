"""
Clipboard Controller
"""
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.clipboard_manager import ClipboardManager
from models.item import Item


class ClipboardController:
    """Handles clipboard operations - connects UI to clipboard manager"""

    def __init__(self, clipboard_manager: ClipboardManager):
        self.clipboard_manager = clipboard_manager

    def copy_item(self, item: Item) -> bool:
        """Copy an item to clipboard and show feedback"""
        success = self.clipboard_manager.copy_item(item)

        if success:
            print(f"✓ Copied to clipboard: {item.label}")
            return True
        else:
            print(f"✗ Failed to copy: {item.label}")
            return False

    def copy_text(self, text: str) -> bool:
        """Copy plain text to clipboard"""
        success = self.clipboard_manager.copy_text(text)

        if success:
            print(f"✓ Copied text to clipboard")
            return True
        else:
            print(f"✗ Failed to copy text")
            return False

    def get_history(self, limit: int = 10):
        """Get clipboard history"""
        return self.clipboard_manager.get_history(limit)

    def clear_history(self) -> None:
        """Clear clipboard history"""
        self.clipboard_manager.clear_history()
        print("Clipboard history cleared")

    def get_last_copied(self) -> Optional[Item]:
        """Get the last copied item"""
        return self.clipboard_manager.get_last_copied()
