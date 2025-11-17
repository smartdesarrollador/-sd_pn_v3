"""
Hotkey Manager for Widget Sidebar
Manages global keyboard shortcuts using pynput
"""

from pynput import keyboard
from typing import Callable, Dict, Optional
import threading


class HotkeyManager:
    """
    Manages global hotkeys for the application
    Runs keyboard listener in a separate thread
    """

    def __init__(self):
        """Initialize hotkey manager"""
        self.hotkeys: Dict[str, Callable] = {}
        self.listener: Optional[keyboard.Listener] = None
        self.is_running = False
        self.current_keys = set()

    def register_hotkey(self, key_combination: str, callback: Callable):
        """
        Register a global hotkey

        Args:
            key_combination: String like "ctrl+shift+v" or "ctrl+shift+1"
            callback: Function to call when hotkey is pressed
        """
        # Normalize key combination to lowercase
        normalized_key = key_combination.lower().replace(" ", "")
        self.hotkeys[normalized_key] = callback
        print(f"Registered hotkey: {normalized_key}")

    def unregister_hotkey(self, key_combination: str):
        """
        Unregister a hotkey

        Args:
            key_combination: Key combination to unregister
        """
        normalized_key = key_combination.lower().replace(" ", "")
        if normalized_key in self.hotkeys:
            del self.hotkeys[normalized_key]
            print(f"Unregistered hotkey: {normalized_key}")

    def unregister_all(self):
        """Unregister all hotkeys"""
        self.hotkeys.clear()
        print("All hotkeys unregistered")

    def start(self):
        """Start listening for global hotkeys"""
        if self.is_running:
            print("HotkeyManager already running")
            return

        print("Starting HotkeyManager...")
        self.is_running = True

        # Create and start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print("HotkeyManager started successfully")

    def stop(self):
        """Stop listening for global hotkeys"""
        if not self.is_running:
            return

        print("Stopping HotkeyManager...")
        self.is_running = False

        if self.listener:
            self.listener.stop()
            self.listener = None

        self.current_keys.clear()
        print("HotkeyManager stopped")

    def _on_press(self, key):
        """
        Handle key press event

        Args:
            key: Pressed key from pynput
        """
        if not self.is_running:
            return

        # Normalize the key
        key_str = self._normalize_key(key)
        if key_str:
            self.current_keys.add(key_str)
            self._check_hotkeys()

    def _on_release(self, key):
        """
        Handle key release event

        Args:
            key: Released key from pynput
        """
        if not self.is_running:
            return

        # Normalize the key
        key_str = self._normalize_key(key)
        if key_str and key_str in self.current_keys:
            self.current_keys.discard(key_str)

    def _normalize_key(self, key) -> Optional[str]:
        """
        Normalize a pynput key to string format

        Args:
            key: Key from pynput

        Returns:
            Normalized key string or None
        """
        try:
            # Handle special keys
            if hasattr(key, 'name'):
                return key.name.lower()

            # Handle character keys
            if hasattr(key, 'char') and key.char:
                return key.char.lower()

            return None
        except AttributeError:
            return None

    def _check_hotkeys(self):
        """Check if current key combination matches any registered hotkeys"""
        if not self.current_keys:
            return

        # Build current combination string
        # Sort to ensure consistent ordering
        sorted_keys = sorted(self.current_keys)
        current_combination = "+".join(sorted_keys)

        # Check if it matches any registered hotkey
        for hotkey, callback in self.hotkeys.items():
            if self._matches_hotkey(current_combination, hotkey):
                try:
                    # Execute callback in a separate thread to avoid blocking
                    thread = threading.Thread(target=callback)
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    print(f"Error executing hotkey callback: {e}")

    def _matches_hotkey(self, current: str, registered: str) -> bool:
        """
        Check if current key combination matches registered hotkey

        Args:
            current: Current pressed keys as string
            registered: Registered hotkey pattern

        Returns:
            True if matches
        """
        # Normalize both combinations
        current_set = set(current.split("+"))
        registered_set = set(registered.split("+"))

        # Must match exactly
        return current_set == registered_set

    def is_active(self) -> bool:
        """
        Check if hotkey manager is active

        Returns:
            True if running
        """
        return self.is_running
