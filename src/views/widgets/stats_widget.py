"""
Stats Widget - Widget compacto de estadísticas
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.stats_manager import StatsManager
import logging

logger = logging.getLogger(__name__)


class StatsWidget(QWidget):
    """Widget compacto que muestra estadísticas básicas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_manager = StatsManager()
        self.init_ui()
        self.load_stats()

        # Auto-refresh cada 30 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

    def init_ui(self):
        """Inicializar UI"""
        self.setObjectName("stats_widget")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Título
        title = QLabel("📊 ESTADÍSTICAS")
        title.setStyleSheet("""
            QLabel {
                color: #007acc;
                font-size: 10pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Container para las stats
        stats_container = QFrame()
        stats_container.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #3e3e42;
                border-radius: 5px;
            }
        """)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_layout.setSpacing(10)

        # Stat: Items usados hoy
        self.today_label = self._create_stat_row("📅", "Hoy", "0")
        stats_layout.addWidget(self.today_label)

        # Separator
        stats_layout.addWidget(self._create_separator())

        # Stat: Items usados esta semana
        self.week_label = self._create_stat_row("📆", "Esta Semana", "0")
        stats_layout.addWidget(self.week_label)

        # Separator
        stats_layout.addWidget(self._create_separator())

        # Stat: Total favoritos
        self.favorites_label = self._create_stat_row("⭐", "Favoritos", "0")
        stats_layout.addWidget(self.favorites_label)

        # Separator
        stats_layout.addWidget(self._create_separator())

        # Stat: Items populares (>50 usos)
        self.popular_label = self._create_stat_row("🔥", "Populares", "0")
        stats_layout.addWidget(self.popular_label)

        main_layout.addWidget(stats_container)

        # Estilos
        self.setStyleSheet("""
            QWidget#stats_widget {
                background-color: #1e1e1e;
                border-radius: 5px;
            }
        """)

    def _create_stat_row(self, icon: str, label: str, value: str) -> QWidget:
        """Crear fila de estadística"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                color: #cccccc;
            }
        """)
        icon_label.setFixedWidth(30)
        layout.addWidget(icon_label)

        # Texto
        text_label = QLabel(label)
        text_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 9pt;
            }
        """)
        layout.addWidget(text_label, 1)

        # Valor
        value_label = QLabel(value)
        value_label.setObjectName(f"value_{label}")
        value_label.setStyleSheet("""
            QLabel {
                color: #007acc;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(value_label)

        return container

    def _create_separator(self) -> QFrame:
        """Crear línea separadora"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            QFrame {
                background-color: #3e3e42;
                max-height: 1px;
            }
        """)
        return line

    def _update_stat_value(self, container: QWidget, value: str):
        """Actualizar valor de una estadística"""
        # Buscar el QLabel con el valor (último widget del layout)
        layout = container.layout()
        if layout and layout.count() >= 3:
            value_label = layout.itemAt(2).widget()
            if value_label:
                value_label.setText(value)

    def load_stats(self):
        """Cargar estadísticas"""
        try:
            # Items usados hoy
            today_items = self.stats_manager.get_most_used_items(period='today')
            today_count = len(today_items)
            self._update_stat_value(self.today_label, str(today_count))

            # Items usados esta semana
            week_items = self.stats_manager.get_most_used_items(period='week')
            week_count = len(week_items)
            self._update_stat_value(self.week_label, str(week_count))

            # Total favoritos
            from core.favorites_manager import FavoritesManager
            favorites_manager = FavoritesManager()
            favorites = favorites_manager.get_all_favorites()
            favorites_count = len(favorites)
            self._update_stat_value(self.favorites_label, str(favorites_count))

            # Items populares (>50 usos)
            popular_items = self.stats_manager.get_popular_items(min_count=50)
            popular_count = len(popular_items)
            self._update_stat_value(self.popular_label, str(popular_count))

            logger.debug(f"Stats loaded: today={today_count}, week={week_count}, "
                        f"favorites={favorites_count}, popular={popular_count}")

        except Exception as e:
            logger.error(f"Error loading stats: {e}")

    def refresh(self):
        """Refrescar estadísticas"""
        logger.debug("Refreshing stats widget")
        self.load_stats()

    def closeEvent(self, event):
        """Cleanup al cerrar"""
        if self.timer:
            self.timer.stop()
        super().closeEvent(event)
