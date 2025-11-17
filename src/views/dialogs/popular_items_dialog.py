"""
Popular Items Dialog - Diálogo mostrando items más usados
Autor: Widget Sidebar Team
Fecha: 2025-01-23
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem,
                              QWidget, QTabWidget, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.stats_manager import StatsManager
import logging

logger = logging.getLogger(__name__)


class PopularItemsDialog(QDialog):
    """Diálogo mostrando items más usados"""

    item_selected = pyqtSignal(int)  # item_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_manager = StatsManager()
        self.init_ui()
        self.load_popular_items()

    def init_ui(self):
        """Inicializar UI"""
        self.setWindowTitle("🔥 Items Más Usados")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Items más populares por período")
        header_font = QFont()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Tabs para diferentes períodos
        self.tabs = QTabWidget()

        # Tab: Todos los tiempos
        self.all_time_list = QListWidget()
        self.all_time_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tabs.addTab(self.all_time_list, "📊 Todos los Tiempos")

        # Tab: Este mes
        self.month_list = QListWidget()
        self.month_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tabs.addTab(self.month_list, "📅 Este Mes")

        # Tab: Esta semana
        self.week_list = QListWidget()
        self.week_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tabs.addTab(self.week_list, "🗓 Esta Semana")

        # Tab: Hoy
        self.today_list = QListWidget()
        self.today_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tabs.addTab(self.today_list, "🕐 Hoy")

        layout.addWidget(self.tabs)

        # Info
        info_label = QLabel("💡 Tip: Haz doble click en un item para seleccionarlo")
        info_label.setStyleSheet("color: #858585; font-style: italic; font-size: 9pt;")
        layout.addWidget(info_label)

        # Botones
        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.clicked.connect(self.load_popular_items)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #cccccc;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 15px;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #252526;
                color: #007acc;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                color: #cccccc;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #3e3e42;
                border-left: 3px solid #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)

    def load_popular_items(self):
        """Cargar items populares en cada tab"""
        try:
            # All time
            all_time = self.stats_manager.get_most_used_items(limit=20)
            self.populate_list(self.all_time_list, all_time, show_percentage=True)

            # This month (30 days)
            month_items = self.stats_manager.get_most_used_items(limit=20, period='month')
            self.populate_list(self.month_list, month_items)

            # This week
            week_items = self.stats_manager.get_most_used_items(limit=20, period='week')
            self.populate_list(self.week_list, week_items)

            # Today
            today_items = self.stats_manager.get_most_used_items(limit=20, period='today')
            self.populate_list(self.today_list, today_items)

            logger.info("Popular items loaded successfully")

        except Exception as e:
            logger.error(f"Error loading popular items: {e}")

    def populate_list(self, list_widget: QListWidget, items: list,
                     show_percentage: bool = False):
        """Poblar lista con items"""
        list_widget.clear()

        if not items:
            empty_item = QListWidgetItem("No hay datos disponibles")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            list_widget.addItem(empty_item)
            return

        max_uses = items[0].get('use_count', 1) if items else 1

        for i, item in enumerate(items, 1):
            # Crear widget personalizado
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(10)

            # Ranking
            rank_label = QLabel(f"#{i}")
            rank_label.setFixedWidth(35)
            rank_label.setStyleSheet("""
                font-weight: bold;
                color: #007acc;
                font-size: 11pt;
            """)
            layout.addWidget(rank_label)

            # Badge + Label
            badge = item.get('badge', '')
            label_text = f"{badge} {item['label']}" if badge else item['label']
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 10pt; color: #cccccc;")
            layout.addWidget(label, 1)

            # Use count
            uses = item.get('use_count', 0)
            use_label = QLabel(f"{uses} usos")
            use_label.setStyleSheet("color: #858585; font-size: 9pt;")
            use_label.setFixedWidth(80)
            use_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(use_label)

            # Progress bar (solo para "all time")
            if show_percentage and max_uses > 0:
                progress = QProgressBar()
                progress.setMaximum(100)
                progress.setValue(int((uses / max_uses) * 100))
                progress.setFixedWidth(100)
                progress.setFixedHeight(8)
                progress.setTextVisible(False)
                progress.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        border-radius: 4px;
                        background-color: #2d2d2d;
                    }
                    QProgressBar::chunk {
                        border-radius: 4px;
                        background-color: #007acc;
                    }
                """)
                layout.addWidget(progress)

            # Agregar a lista
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            list_widget.addItem(list_item)
            list_widget.setItemWidget(list_item, widget)

    def on_item_double_clicked(self, item):
        """Handler cuando se hace doble click"""
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_id:
            logger.info(f"Popular item selected: {item_id}")
            self.item_selected.emit(item_id)
            self.accept()
