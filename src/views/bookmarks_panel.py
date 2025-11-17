"""
Bookmarks Panel - Panel flotante para gestionar marcadores del navegador
Author: Widget Sidebar Team
Date: 2025-11-02
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)


class BookmarkItemWidget(QWidget):
    """Widget para mostrar un marcador individual."""

    delete_clicked = pyqtSignal(int)  # bookmark_id
    bookmark_clicked = pyqtSignal(str)  # url

    def __init__(self, bookmark_id: int, title: str, url: str, parent=None):
        super().__init__(parent)
        self.bookmark_id = bookmark_id
        self.title = title
        self.url = url

        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz del widget de marcador."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Contenedor para título y URL
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Título (clickeable)
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel:hover {
                color: #00ff00;
                text-decoration: underline;
            }
        """)
        self.title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_label.mousePressEvent = lambda e: self.bookmark_clicked.emit(self.url)
        info_layout.addWidget(self.title_label)

        # URL (truncada si es muy larga)
        truncated_url = self.url[:60] + "..." if len(self.url) > 60 else self.url
        self.url_label = QLabel(truncated_url)
        self.url_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 10px;
            }
        """)
        self.url_label.setToolTip(self.url)
        info_layout.addWidget(self.url_label)

        layout.addLayout(info_layout, 1)

        # Botón eliminar
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(25, 25)
        self.delete_btn.setToolTip("Eliminar marcador")
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.bookmark_id))
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)

        # Estilo del widget
        self.setStyleSheet("""
            BookmarkItemWidget {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 5px;
            }
            BookmarkItemWidget:hover {
                border: 1px solid #00d4ff;
            }
        """)


class BookmarksPanel(QWidget):
    """Panel flotante para gestionar marcadores del navegador."""

    bookmark_selected = pyqtSignal(str)  # url

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager

        self.setWindowTitle("Marcadores")
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        self.setFixedSize(400, 500)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Configura la interfaz del panel."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("★ Marcadores")
        header_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(header_label)

        # Botón cerrar
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setToolTip("Cerrar panel")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        header_layout.addWidget(close_btn)

        main_layout.addLayout(header_layout)

        # Área de scroll para los marcadores
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #0f3460;
                background-color: #1a1a2e;
            }
        """)

        # Contenedor de marcadores
        self.bookmarks_container = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_container)
        self.bookmarks_layout.setSpacing(5)
        self.bookmarks_layout.setContentsMargins(5, 5, 5, 5)
        self.bookmarks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.bookmarks_container)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def _apply_styles(self):
        """Aplica estilos al panel."""
        self.setStyleSheet("""
            BookmarksPanel {
                background-color: #1a1a2e;
                border: 2px solid #00d4ff;
                border-radius: 10px;
            }
        """)

    def refresh_bookmarks(self):
        """Recarga la lista de marcadores desde la base de datos."""
        # Limpiar lista actual
        while self.bookmarks_layout.count():
            item = self.bookmarks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Cargar marcadores
        bookmarks = self.db.get_bookmarks()

        if not bookmarks:
            # Mostrar mensaje si no hay marcadores
            no_bookmarks_label = QLabel("No hay marcadores guardados")
            no_bookmarks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_bookmarks_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 12px;
                    padding: 20px;
                }
            """)
            self.bookmarks_layout.addWidget(no_bookmarks_label)
        else:
            # Agregar widgets de marcadores
            for bookmark in bookmarks:
                bookmark_widget = BookmarkItemWidget(
                    bookmark['id'],
                    bookmark['title'],
                    bookmark['url']
                )
                bookmark_widget.bookmark_clicked.connect(self._on_bookmark_clicked)
                bookmark_widget.delete_clicked.connect(self._on_delete_bookmark)
                self.bookmarks_layout.addWidget(bookmark_widget)

        logger.info(f"Panel de marcadores actualizado: {len(bookmarks)} marcadores")

    def _on_bookmark_clicked(self, url: str):
        """Handler cuando se hace click en un marcador."""
        self.bookmark_selected.emit(url)
        self.close()

    def _on_delete_bookmark(self, bookmark_id: int):
        """Handler cuando se elimina un marcador."""
        if self.db.delete_bookmark(bookmark_id):
            logger.info(f"Marcador {bookmark_id} eliminado")
            self.refresh_bookmarks()
