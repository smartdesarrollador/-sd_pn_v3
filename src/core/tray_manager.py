"""
Tray Manager for Widget Sidebar
Manages system tray icon and context menu
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional


class TrayManager(QObject):
    """
    Manages system tray icon and menu
    Provides quick access to show/hide window and application settings
    """

    # Signals
    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    stats_dashboard_requested = pyqtSignal()
    popular_items_requested = pyqtSignal()
    forgotten_items_requested = pyqtSignal()
    pinned_panels_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize tray manager"""
        super().__init__(parent)
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_menu: Optional[QMenu] = None
        self.is_window_visible = True

    def setup_tray(self, main_window):
        """
        Setup system tray icon and menu

        Args:
            main_window: Reference to main window for positioning
        """
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system")
            return False

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(main_window)

        # Set icon (using default application icon for now)
        # TODO: Create and use custom icon file
        icon = QIcon()  # Empty icon, will show default
        if icon.isNull():
            # Try to use a simple colored icon as fallback
            from PyQt6.QtGui import QPixmap, QPainter, QColor
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 122, 204))  # Blue color
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            from PyQt6.QtGui import QFont
            font = QFont("Arial", 16, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), 0x84, "WS")  # AlignCenter
            painter.end()
            icon = QIcon(pixmap)

        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Widget Sidebar")

        # Create context menu
        self._create_menu()

        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Show tray icon
        self.tray_icon.show()

        print("System tray icon created successfully")
        return True

    def _create_menu(self):
        """Create context menu for tray icon"""
        self.tray_menu = QMenu()

        # Show/Hide action
        self.toggle_action = QAction("Mostrar/Ocultar", self.tray_menu)
        self.toggle_action.triggered.connect(self._on_toggle_window)
        self.tray_menu.addAction(self.toggle_action)

        # Separator
        self.tray_menu.addSeparator()

        # Settings action
        settings_action = QAction("⚙ Configuración", self.tray_menu)
        settings_action.triggered.connect(self._on_settings)
        self.tray_menu.addAction(settings_action)

        # Separator
        self.tray_menu.addSeparator()

        # Stats dashboard action
        dashboard_action = QAction("📊 Dashboard de Estadísticas", self.tray_menu)
        dashboard_action.triggered.connect(self._on_stats_dashboard)
        self.tray_menu.addAction(dashboard_action)

        # Popular items action
        popular_action = QAction("🔥 Items Populares", self.tray_menu)
        popular_action.triggered.connect(self._on_popular_items)
        self.tray_menu.addAction(popular_action)

        # Forgotten items action
        forgotten_action = QAction("📦 Items Olvidados", self.tray_menu)
        forgotten_action.triggered.connect(self._on_forgotten_items)
        self.tray_menu.addAction(forgotten_action)

        # Separator
        self.tray_menu.addSeparator()

        # Pinned panels action
        pinned_panels_action = QAction("📌 Gestionar Paneles Anclados", self.tray_menu)
        pinned_panels_action.triggered.connect(self._on_pinned_panels)
        self.tray_menu.addAction(pinned_panels_action)

        # Separator
        self.tray_menu.addSeparator()

        # Logout action
        logout_action = QAction("🔒 Cerrar Sesión", self.tray_menu)
        logout_action.triggered.connect(self._on_logout)
        self.tray_menu.addAction(logout_action)

        # Separator
        self.tray_menu.addSeparator()

        # Quit action
        quit_action = QAction("Salir", self.tray_menu)
        quit_action.triggered.connect(self._on_quit)
        self.tray_menu.addAction(quit_action)

        # Set menu to tray icon
        self.tray_icon.setContextMenu(self.tray_menu)

    def _on_tray_activated(self, reason):
        """
        Handle tray icon activation

        Args:
            reason: Activation reason (click, double-click, etc.)
        """
        # Left click or double click -> toggle window
        if reason == QSystemTrayIcon.ActivationReason.Trigger or \
           reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._on_toggle_window()

    def _on_toggle_window(self):
        """Toggle window visibility"""
        if self.is_window_visible:
            self.hide_window_requested.emit()
            self.is_window_visible = False
            self.toggle_action.setText("Mostrar")
        else:
            self.show_window_requested.emit()
            self.is_window_visible = True
            self.toggle_action.setText("Ocultar")

    def _on_settings(self):
        """Handle settings menu action"""
        self.settings_requested.emit()

    def _on_stats_dashboard(self):
        """Handle stats dashboard menu action"""
        self.stats_dashboard_requested.emit()

    def _on_popular_items(self):
        """Handle popular items menu action"""
        self.popular_items_requested.emit()

    def _on_forgotten_items(self):
        """Handle forgotten items menu action"""
        self.forgotten_items_requested.emit()

    def _on_pinned_panels(self):
        """Handle pinned panels menu action"""
        self.pinned_panels_requested.emit()

    def _on_logout(self):
        """Handle logout menu action"""
        self.logout_requested.emit()

    def _on_quit(self):
        """Handle quit menu action"""
        self.quit_requested.emit()

    def show_message(self, title: str, message: str, duration: int = 3000):
        """
        Show system tray notification

        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds (default 3000)
        """
        if self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )

    def update_window_state(self, is_visible: bool):
        """
        Update internal state of window visibility

        Args:
            is_visible: True if window is visible
        """
        self.is_window_visible = is_visible
        if hasattr(self, 'toggle_action'):
            self.toggle_action.setText("Ocultar" if is_visible else "Mostrar")

    def cleanup(self):
        """Cleanup tray icon resources"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
        if self.tray_menu:
            self.tray_menu = None
        print("TrayManager cleaned up")
