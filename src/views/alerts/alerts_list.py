"""
Alerts List
Displays alerts with filtering capabilities
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
import logging

from .alert_item_widget import AlertItemWidget

logger = logging.getLogger(__name__)


class AlertsList(QWidget):
    """
    Widget for displaying and managing alerts
    Includes filtering by status (All/Active/Past)
    """

    # Signals
    alert_selected = pyqtSignal(dict)  # Emitted when alert is selected
    create_alert_requested = pyqtSignal()  # Emitted when "New Alert" clicked
    edit_alert_requested = pyqtSignal(dict)  # Emitted when edit requested
    refresh_needed = pyqtSignal()  # Emitted when list needs refresh

    def __init__(self, db_manager, parent=None):
        """
        Initialize alerts list

        Args:
            db_manager: DBManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager

        # Current filter
        self.current_filter = "active"  # active, all, past

        self.setup_ui()
        self.apply_styles()
        self.load_alerts()

        logger.info(f"AlertsList initialized with filter: {self.current_filter}")

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Filter and title bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        # Title
        title_label = QLabel("🔔 Alertas")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        filter_layout.addWidget(title_label)

        filter_layout.addStretch()

        # Filter combo
        filter_label = QLabel("Filtro:")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Activas", "active")
        self.filter_combo.addItem("Todas", "all")
        self.filter_combo.addItem("Pasadas", "past")
        self.filter_combo.setFixedWidth(120)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)

        layout.addLayout(filter_layout)

        # Stats bar
        self.stats_label = QLabel()
        stats_font = QFont()
        stats_font.setPointSize(9)
        self.stats_label.setFont(stats_font)
        self.stats_label.setStyleSheet("color: #999999;")
        layout.addWidget(self.stats_label)

        # Alerts list
        self.alerts_list = QListWidget()
        self.alerts_list.setSpacing(2)
        layout.addWidget(self.alerts_list)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_new_alert = QPushButton("+ Nueva Alerta")
        self.btn_new_alert.setMinimumHeight(35)
        self.btn_new_alert.clicked.connect(self.create_alert)

        self.btn_refresh = QPushButton("🔄 Actualizar")
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.setMinimumHeight(35)
        self.btn_refresh.clicked.connect(self.load_alerts)

        buttons_layout.addWidget(self.btn_new_alert, 1)
        buttons_layout.addWidget(self.btn_refresh)

        layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Apply styles to the widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cccccc;
                margin-right: 5px;
            }
            QListWidget {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: transparent;
                border: none;
            }
        """)

    def on_filter_changed(self, index):
        """Handle filter combo box change"""
        self.current_filter = self.filter_combo.itemData(index)
        logger.debug(f"Filter changed to: {self.current_filter}")
        self.load_alerts()

    def load_alerts(self):
        """Load alerts from database based on current filter"""
        try:
            logger.info(f"Loading alerts with filter: {self.current_filter}")

            # Clear current list
            self.alerts_list.clear()

            # Get all alerts from database
            # Note: get_alerts_by_item requires item_id, so we need a different approach
            # Let's get all items and their alerts
            conn = self.db.connect()
            cursor = conn.cursor()

            # Build query based on filter
            if self.current_filter == "active":
                # Only active and enabled alerts
                query = """
                    SELECT a.*, i.label as item_label
                    FROM item_alerts a
                    LEFT JOIN items i ON a.item_id = i.id
                    WHERE a.status = 'active' AND a.is_enabled = 1
                    ORDER BY a.alert_datetime ASC
                """
            elif self.current_filter == "past":
                # Triggered or dismissed alerts
                query = """
                    SELECT a.*, i.label as item_label
                    FROM item_alerts a
                    LEFT JOIN items i ON a.item_id = i.id
                    WHERE a.status IN ('triggered', 'dismissed')
                    ORDER BY a.alert_datetime DESC
                """
            else:  # all
                # All alerts
                query = """
                    SELECT a.*, i.label as item_label
                    FROM item_alerts a
                    LEFT JOIN items i ON a.item_id = i.id
                    ORDER BY a.alert_datetime DESC
                """

            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]

            if not alerts:
                # Show "no alerts" message
                filter_text = {
                    'active': 'activas',
                    'all': 'en total',
                    'past': 'pasadas'
                }.get(self.current_filter, '')

                item = QListWidgetItem(f"No hay alertas {filter_text}")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.alerts_list.addItem(item)
                self.update_stats(0, 0, 0)
                logger.debug(f"No alerts found for filter: {self.current_filter}")
                return

            # Count stats
            active_count = sum(1 for a in alerts if a['status'] == 'active' and a['is_enabled'])
            triggered_count = sum(1 for a in alerts if a['status'] == 'triggered')
            dismissed_count = sum(1 for a in alerts if a['status'] == 'dismissed')

            # Add alerts to list
            for alert in alerts:
                self.add_alert_item(alert)

            # Update stats
            self.update_stats(active_count, triggered_count, dismissed_count)

            logger.info(f"Loaded {len(alerts)} alerts (Active: {active_count}, Triggered: {triggered_count}, Dismissed: {dismissed_count})")

        except Exception as e:
            logger.error(f"Error loading alerts: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar alertas: {str(e)}"
            )

    def update_stats(self, active, triggered, dismissed):
        """Update the stats label"""
        total = active + triggered + dismissed
        self.stats_label.setText(
            f"Total: {total} | Activas: {active} | Disparadas: {triggered} | Descartadas: {dismissed}"
        )

    def add_alert_item(self, alert):
        """
        Add an alert item to the list

        Args:
            alert: Alert dictionary
        """
        # Create AlertItemWidget
        alert_widget = AlertItemWidget(alert)

        # Connect signals
        alert_widget.edit_requested.connect(self.on_edit_alert)
        alert_widget.dismiss_requested.connect(self.on_dismiss_alert)
        alert_widget.delete_requested.connect(self.on_delete_alert)

        # Create list item
        list_item = QListWidgetItem()
        list_item.setSizeHint(alert_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, alert)

        # Add to list
        self.alerts_list.addItem(list_item)
        self.alerts_list.setItemWidget(list_item, alert_widget)

    def create_alert(self):
        """Handle new alert button click"""
        logger.debug("Create alert requested")
        self.create_alert_requested.emit()

    def on_edit_alert(self, alert):
        """Handle edit alert request"""
        logger.debug(f"Edit alert: {alert['id']}")
        self.edit_alert_requested.emit(alert)

    def on_dismiss_alert(self, alert):
        """Handle dismiss alert request"""
        reply = QMessageBox.question(
            self,
            "Confirmar descarte",
            f"¿Descartar la alerta '{alert.get('alert_title', 'Sin título')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.dismiss_alert(alert['id'])
                logger.info(f"Alert dismissed: {alert['id']}")
                self.load_alerts()  # Refresh list
                self.refresh_needed.emit()
            except Exception as e:
                logger.error(f"Error dismissing alert: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al descartar alerta: {str(e)}"
                )

    def on_delete_alert(self, alert):
        """Handle delete alert request"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la alerta '{alert.get('alert_title', 'Sin título')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_item_alert(alert['id'])
                logger.info(f"Alert deleted: {alert['id']}")
                self.load_alerts()  # Refresh list
                self.refresh_needed.emit()
            except Exception as e:
                logger.error(f"Error deleting alert: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar alerta: {str(e)}"
                )
