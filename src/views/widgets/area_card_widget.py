"""
Area Card Widget - Card moderna para Modo Limpio

Diseño en card estilo Material Design para mostrar elementos del área
en un grid responsive. Incluye:
- Hover effects con sombras elevadas
- Preview de contenido
- Metadata visible (tipo, fecha)
- Badge de tipo de elemento
- Bordes de color según tipo
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, QTimer, QRect
from PyQt6.QtGui import QCursor, QColor, QPainter, QPen, QFont
import logging

logger = logging.getLogger(__name__)


class AreaCardWidget(QWidget):
    """Card moderna para mostrar elementos del área en modo limpio"""

    # Señales
    clicked = pyqtSignal(str)  # Emite el contenido a copiar
    view_items_requested = pyqtSignal(str, int, str, str)  # relation_type, entity_id, entity_name, entity_icon

    # Colores por tipo de elemento
    TYPE_COLORS = {
        'tag': '#9b59b6',      # Púrpura
        'item': '#bb79d6',     # Púrpura claro
        'category': '#ff8800', # Naranja
        'list': '#aa88ff',     # Púrpura lavanda
        'table': '#ff0088',    # Rosa
        'process': '#88ff00',  # Lima
        'comment': '#bb79d6',  # Púrpura claro
        'alert': '#ffaa00',    # Amarillo/Naranja
        'note': '#9b59b6',     # Púrpura
        'divider': '#555555'   # Gris
    }

    # Iconos por tipo
    TYPE_ICONS = {
        'tag': '🏷️',
        'item': '📄',
        'category': '📂',
        'list': '📋',
        'table': '📊',
        'process': '⚙️',
        'comment': '💬',
        'alert': '⚠️',
        'note': '📌',
        'divider': '─'
    }

    def __init__(self, item_data: dict, item_type: str, parent=None):
        """
        Args:
            item_data: Datos del elemento (puede ser relation o component)
            item_type: Tipo de elemento ('tag', 'item', 'category', etc.)
        """
        super().__init__(parent)

        self.item_data = item_data
        self.item_type = item_type
        self.is_hovered = False
        self.show_copied_indicator = False  # Para mostrar checkmark al copiar

        # Guardar el nombre original completo para copiar
        self.original_name = item_data.get('name', item_data.get('content', ''))

        # Configurar tamaño fijo de la card (aumentado de 160 a 180)
        self.setFixedSize(280, 180)
        # NO configurar cursor aquí - el botón tendrá su propio cursor

        self.init_ui()
        self.setup_shadow_effect()

        # Timer para ocultar el indicador de copiado
        self.copied_timer = QTimer()
        self.copied_timer.setSingleShot(True)
        self.copied_timer.timeout.connect(self.hide_copied_indicator)

    def init_ui(self):
        """Inicializa la interfaz de la card"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Frame contenedor
        self.card_frame = QFrame()
        self.card_frame.setObjectName("cardFrame")

        # Color del borde según tipo
        border_color = self.TYPE_COLORS.get(self.item_type, '#555555')

        # Detectar si es componente para usar color de fondo diferente
        is_component = self.item_type in ['comment', 'alert', 'note', 'divider']

        # Colores de fondo específicos para componentes
        if is_component:
            bg_color = '#1a2332'  # Azul oscuro para componentes
            hover_color = '#223244'
        else:
            bg_color = '#2d2d2d'  # Gris oscuro para relaciones
            hover_color = '#353535'

        self.card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#cardFrame:hover {{
                background-color: {hover_color};
                border-color: #ffffff;
            }}
        """)

        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        # Header: Icono + Nombre + Badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Icono del elemento
        icon = self.item_data.get('icon', self.TYPE_ICONS.get(self.item_type, '📄'))
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20pt;")
        icon_label.setFixedSize(32, 32)
        header_layout.addWidget(icon_label)

        # Nombre del elemento como botón clickeable
        name = self.item_data.get('name', self.item_data.get('content', 'Sin nombre'))
        # Truncar nombre largo para mostrar
        display_name = name
        if len(name) > 25:
            display_name = name[:22] + '...'

        self.name_button = QPushButton(display_name)
        self.name_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.name_button.setToolTip(f"Click para copiar: {name}")
        self.name_button.clicked.connect(self._on_name_button_clicked)

        # Ajustar altura mínima para evitar texto cortado
        self.name_button.setMinimumHeight(32)
        self.name_button.setMaximumHeight(40)

        # Color del borde según tipo
        border_color = self.TYPE_COLORS.get(self.item_type, '#555555')

        self.name_button.setStyleSheet(f"""
            QPushButton {{
                color: #ffffff;
                font-size: 10pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {border_color}30;
                border: 2px solid #ffffff;
            }}
            QPushButton:pressed {{
                background-color: {border_color}50;
                border: 3px solid {border_color};
            }}
        """)
        header_layout.addWidget(self.name_button, 1)

        # Badge de tipo - Más grande y distintivo para componentes
        is_component = self.item_type in ['comment', 'alert', 'note', 'divider']

        if is_component:
            # Badge especial para componentes - Más destacado
            component_icons = {
                'comment': '💬',
                'alert': '⚠️',
                'note': '📌',
                'divider': '─'
            }
            icon = component_icons.get(self.item_type, '💬')
            badge_text = f"{icon} {self.item_type.upper()}"
            badge_width = 95
            badge_height = 26
            badge_font_size = "8pt"
        else:
            # Badge normal para relaciones
            badge_text = self.item_type.upper()
            badge_width = 48
            badge_height = 20
            badge_font_size = "7pt"

        type_badge = QLabel(badge_text)
        type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_badge.setFixedSize(badge_width, badge_height)
        type_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {border_color};
                color: #000000;
                font-size: {badge_font_size};
                font-weight: bold;
                border-radius: 5px;
                padding: 2px 6px;
            }}
        """)
        header_layout.addWidget(type_badge)

        card_layout.addLayout(header_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {border_color}; max-height: 1px;")
        card_layout.addWidget(separator)

        # Descripción / Preview - Ahora como botón clickeable
        description = self.item_data.get('description', '')
        content = self.item_data.get('content', '')

        # Guardar texto completo para mostrar en diálogo
        self.full_description = description if description else content

        # Texto truncado para preview
        preview_text = self.full_description
        if preview_text and len(preview_text) > 100:
            preview_text = preview_text[:97] + '...'

        # Usar QPushButton en lugar de QLabel para hacerlo clickeable
        self.preview_button = QPushButton(preview_text or "Sin descripción")
        # QPushButton NO tiene setWordWrap - el texto se ajustará con el estilo CSS
        self.preview_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.preview_button.clicked.connect(self._show_full_description)

        # Tooltip para indicar que es clickeable
        if self.full_description and len(self.full_description) > 100:
            self.preview_button.setToolTip("🔍 Click para ver descripción completa")

        # Configurar para que el texto se ajuste con word-wrap en CSS
        self.preview_button.setSizePolicy(
            self.preview_button.sizePolicy().horizontalPolicy(),
            self.preview_button.sizePolicy().verticalPolicy()
        )

        self.preview_button.setStyleSheet("""
            QPushButton {
                color: #aaaaaa;
                font-size: 9pt;
                font-style: italic;
                background-color: transparent;
                border: 1px dashed #555555;
                border-radius: 4px;
                padding: 6px;
                text-align: left;
                qproperty-wordWrap: true;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px dashed #777777;
                color: #cccccc;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.preview_button.setMinimumHeight(40)
        card_layout.addWidget(self.preview_button, 1)

        # Tags (si existen)
        if 'tags' in self.item_data and self.item_data['tags']:
            self._add_tags_section(card_layout)

        # Footer: Metadata
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        # Tipo de contenido (para items)
        if 'type' in self.item_data and self.item_data['type']:
            content_type_label = QLabel(f"📋 {self.item_data['type']}")
            content_type_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 8pt;
                }
            """)
            footer_layout.addWidget(content_type_label)

        # Botón "Ver items" para categorías, tags y listas
        # En áreas, podemos ver items de: categorías, tags, listas, o del área completa
        if self.item_type in ['category', 'tag', 'list']:
            self.view_items_btn = QPushButton("👁️")
            self.view_items_btn.setFixedSize(28, 28)
            self.view_items_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.view_items_btn.setToolTip("Ver todos los items relacionados")
            border_color = self.TYPE_COLORS.get(self.item_type, '#555555')
            self.view_items_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e1e1e;
                    color: {border_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    font-size: 12pt;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {border_color}40;
                    border-color: #ffffff;
                }}
                QPushButton:pressed {{
                    background-color: {border_color}60;
                }}
            """)
            self.view_items_btn.clicked.connect(self._on_view_items_clicked)
            footer_layout.addWidget(self.view_items_btn)

        footer_layout.addStretch()

        # Fecha de última modificación (si existe)
        if 'updated_at' in self.item_data or 'created_at' in self.item_data:
            date = self.item_data.get('updated_at', self.item_data.get('created_at', ''))
            if date:
                # Extraer solo la fecha (primeros 10 caracteres)
                date_str = str(date)[:10]
                date_label = QLabel(f"⏰ {date_str}")
                date_label.setStyleSheet("""
                    QLabel {
                        color: #888888;
                        font-size: 8pt;
                    }
                """)
                footer_layout.addWidget(date_label)

        card_layout.addLayout(footer_layout)

        main_layout.addWidget(self.card_frame)

    def _add_tags_section(self, layout):
        """Agrega la sección de tags al layout"""
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(4)
        tags_layout.setContentsMargins(0, 4, 0, 0)

        # Obtener los tags
        tags = self.item_data.get('tags', [])

        # Mostrar máximo 3 tags
        max_visible_tags = 3
        visible_tags = tags[:max_visible_tags]

        for tag in visible_tags:
            # Crear chip simple sin dependencia de AreaTagChip
            chip = self._create_simple_tag_chip(tag)
            tags_layout.addWidget(chip)

        # Si hay más tags, mostrar indicador "+X más"
        if len(tags) > max_visible_tags:
            remaining = len(tags) - max_visible_tags
            more_label = QLabel(f"+{remaining}")
            more_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 7pt;
                    font-style: italic;
                    padding: 2px 6px;
                }
            """)
            tags_layout.addWidget(more_label)

        tags_layout.addStretch()
        layout.addLayout(tags_layout)

    def _create_simple_tag_chip(self, tag):
        """Crea un chip simple para mostrar un tag"""
        chip = QLabel(tag.name)
        chip.setFixedHeight(24)  # Aumentado de 18 a 24
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setStyleSheet(f"""
            QLabel {{
                background-color: {tag.color};
                color: #000000;
                font-size: 9pt;  /* Aumentado de 7pt a 9pt */
                font-weight: bold;
                border-radius: 12px;  /* Aumentado proporcionalmente */
                padding: 4px 12px;  /* Aumentado de 2px 8px a 4px 12px */
                border: 1px solid {tag.color};
            }}
        """)
        return chip

    def setup_shadow_effect(self):
        """Configura el efecto de sombra"""
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.card_frame.setGraphicsEffect(self.shadow)

    def enterEvent(self, event):
        """Al pasar el mouse sobre la card"""
        self.is_hovered = True

        # Animar sombra - aumentar blur y offset
        self.shadow.setBlurRadius(20)
        self.shadow.setYOffset(6)
        self.shadow.setColor(QColor(0, 0, 0, 100))

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Al quitar el mouse de la card"""
        self.is_hovered = False

        # Restaurar sombra
        self.shadow.setBlurRadius(10)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 60))

        super().leaveEvent(event)

    def _on_name_button_clicked(self):
        """Callback cuando se hace click en el botón del nombre"""
        # Emitir señal con el nombre original (sin truncar)
        self.clicked.emit(self.original_name)
        logger.info(f"Name button clicked - Copying to clipboard: {self.original_name}")

        # Mostrar feedback visual
        self.show_copy_feedback()

    def _on_view_items_clicked(self):
        """Callback cuando se hace click en el botón 'Ver items'"""
        # Obtener datos según el tipo
        entity_id = self.item_data.get('id', 0)
        entity_name = self.item_data.get('name', 'Sin nombre')
        entity_icon = self.item_data.get('icon', self.TYPE_ICONS.get(self.item_type, '📄'))

        # Determinar el relation_type correcto
        # Para tags de área, usamos 'area_tag' en lugar de 'tag'
        relation_type = self.item_type
        if self.item_type == 'tag':
            relation_type = 'area_tag'

        logger.info(f"View items requested for {relation_type}: {entity_name} (ID: {entity_id})")

        # Emitir señal con los datos necesarios
        self.view_items_requested.emit(relation_type, entity_id, entity_name, entity_icon)

    def _show_full_description(self):
        """Muestra la descripción completa en un diálogo"""
        if not self.full_description:
            return

        # Crear diálogo personalizado
        dialog = QMessageBox(self)
        dialog.setWindowTitle(f"📝 Descripción - {self.original_name}")
        dialog.setText(self.full_description)
        dialog.setIcon(QMessageBox.Icon.Information)

        # Botón para copiar descripción
        copy_button = dialog.addButton("📋 Copiar", QMessageBox.ButtonRole.ActionRole)
        dialog.addButton("Cerrar", QMessageBox.ButtonRole.AcceptRole)

        # Estilo oscuro para el diálogo
        dialog.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 10pt;
                padding: 10px;
                min-width: 400px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)

        # Mostrar diálogo
        result = dialog.exec()

        # Si se hizo click en copiar
        if dialog.clickedButton() == copy_button:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.full_description)
            logger.info(f"Description copied to clipboard")

    def mousePressEvent(self, event):
        """Al hacer clic en la card - DESHABILITADO"""
        # Ya NO copiamos al hacer click en la card completa
        # Solo el botón del nombre copia al portapapeles
        super().mousePressEvent(event)

    def show_copy_feedback(self):
        """Muestra feedback visual de que se copió al portapapeles"""
        # Activar indicador
        self.show_copied_indicator = True
        self.update()  # Forzar repaint

        # Cambiar estilo del BOTÓN temporalmente
        self.name_button.setStyleSheet(f"""
            QPushButton {{
                color: #000000;
                font-size: 10pt;
                font-weight: bold;
                background-color: #9b59b6;
                border: 3px solid #9b59b6;
                border-radius: 8px;
                padding: 6px 12px;
                text-align: left;
            }}
        """)

        # Cambiar color del borde de la card
        border_color = self.TYPE_COLORS.get(self.item_type, '#555555')
        self.card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: #2a1a3d;
                border: 3px solid #9b59b6;
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        # Iniciar animación de sombra
        self.shadow.setBlurRadius(25)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(155, 89, 182, 150))

        # Ocultar indicador después de 1 segundo
        self.copied_timer.start(1000)

    def hide_copied_indicator(self):
        """Oculta el indicador de copiado"""
        self.show_copied_indicator = False
        self.update()

        # Restaurar estilo original
        border_color = self.TYPE_COLORS.get(self.item_type, '#555555')

        # Restaurar estilo del BOTÓN
        self.name_button.setStyleSheet(f"""
            QPushButton {{
                color: #ffffff;
                font-size: 10pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {border_color}30;
                border: 2px solid #ffffff;
            }}
            QPushButton:pressed {{
                background-color: {border_color}50;
                border: 3px solid {border_color};
            }}
        """)

        # Detectar si es componente para restaurar color correcto
        is_component = self.item_type in ['comment', 'alert', 'note', 'divider']

        if is_component:
            bg_color = '#1a2332'  # Azul oscuro para componentes
            hover_color = '#223244'
        else:
            bg_color = '#2d2d2d'  # Gris oscuro para relaciones
            hover_color = '#353535'

        self.card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#cardFrame:hover {{
                background-color: {hover_color};
                border-color: #ffffff;
            }}
        """)

        # Restaurar sombra
        self.shadow.setBlurRadius(10)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 60))

    def paintEvent(self, event):
        """Dibuja el indicador de copiado si está activo"""
        super().paintEvent(event)

        if self.show_copied_indicator:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Dibujar círculo de fondo
            center_x = self.width() - 30
            center_y = 30
            radius = 20

            # Círculo púrpura con borde
            painter.setBrush(QColor(155, 89, 182))
            painter.setPen(QPen(QColor(123, 71, 145), 2))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

            # Dibujar checkmark
            painter.setPen(QPen(QColor(0, 0, 0), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

            # Línea 1 del check (parte corta)
            painter.drawLine(center_x - 8, center_y, center_x - 3, center_y + 6)

            # Línea 2 del check (parte larga)
            painter.drawLine(center_x - 3, center_y + 6, center_x + 8, center_y - 6)

            # Texto "Copiado!"
            painter.setPen(QColor(155, 89, 182))
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(center_x - 30, center_y + 35, "Copiado!")
