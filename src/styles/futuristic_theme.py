"""
Futuristic Theme - Sistema de estilos y paletas de colores futuristas
"""
from enum import Enum
from typing import Dict, Any


class ColorPalette(Enum):
    """Paletas de colores disponibles"""
    CYBER_NEON = "cyber_neon"
    DARK_HOLOGRAPHIC = "dark_holographic"


class FuturisticTheme:
    """Gestor de tema futurista con paletas de colores y estilos"""

    # Paleta Cyber Neon
    CYBER_NEON = {
        'primary': '#00D9FF',        # Cyan brillante
        'secondary': '#BD00FF',      # Púrpura neón
        'accent': '#FF006E',         # Rosa magenta
        'background_deep': '#0A0E27', # Azul oscuro profundo
        'background_mid': '#1A1F3A',  # Azul medio
        'surface': '#252B4A',         # Superficie elevada
        'text_primary': '#E0E7FF',    # Texto principal
        'text_secondary': '#8B9FDE',  # Texto secundario
        'success': '#00FFA3',         # Verde neón
        'warning': '#FFD700',         # Dorado
        'error': '#FF3366',           # Rojo neón
        'glow_cyan': 'rgba(0, 217, 255, 0.3)',
        'glow_purple': 'rgba(189, 0, 255, 0.3)',
        'glow_pink': 'rgba(255, 0, 110, 0.3)',
    }

    # Paleta Dark Holographic
    DARK_HOLOGRAPHIC = {
        'primary': '#4A90E2',         # Azul real
        'secondary': '#9B59B6',       # Púrpura profundo
        'accent': '#E74C3C',          # Rojo carmesí
        'background_deep': '#0D0D0D', # Negro profundo
        'background_mid': '#1A1A1A',  # Gris muy oscuro
        'surface': '#2C2C2C',         # Superficie gris
        'text_primary': '#FFFFFF',    # Blanco puro
        'text_secondary': '#B0B0B0',  # Gris claro
        'success': '#2ECC71',         # Verde esmeralda
        'warning': '#F39C12',         # Naranja
        'error': '#E74C3C',           # Rojo
        'holographic_1': '#FF00FF',   # Magenta
        'holographic_2': '#00FFFF',   # Cyan
        'holographic_3': '#FFD700',   # Dorado
    }

    def __init__(self, palette: ColorPalette = ColorPalette.CYBER_NEON):
        """Inicializar tema con paleta seleccionada"""
        self.current_palette = palette
        self._colors = self.CYBER_NEON if palette == ColorPalette.CYBER_NEON else self.DARK_HOLOGRAPHIC

    def get_color(self, key: str) -> str:
        """Obtener color de la paleta actual"""
        return self._colors.get(key, '#FFFFFF')

    def get_all_colors(self) -> Dict[str, str]:
        """Obtener todos los colores de la paleta actual"""
        return self._colors.copy()

    def switch_palette(self, palette: ColorPalette):
        """Cambiar de paleta"""
        self.current_palette = palette
        self._colors = self.CYBER_NEON if palette == ColorPalette.CYBER_NEON else self.DARK_HOLOGRAPHIC

    # ===== ESTILOS DE COMPONENTES =====

    def get_sidebar_style(self) -> str:
        """Estilo para la barra lateral principal"""
        return f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.get_color('background_deep')},
                    stop:1 {self.get_color('background_mid')}
                );
                border-right: 2px solid {self.get_color('primary')};
                border-image: none;
            }}
        """

    def get_button_style(self, button_type: str = 'primary') -> str:
        """Estilos para botones con efectos futuristas"""
        if button_type == 'primary':
            bg_color = self.get_color('primary')
            hover_color = self.get_color('secondary')
            glow = self.get_color('glow_cyan') if self.current_palette == ColorPalette.CYBER_NEON else self.get_color('primary')
        elif button_type == 'secondary':
            bg_color = self.get_color('secondary')
            hover_color = self.get_color('accent')
            glow = self.get_color('glow_purple') if self.current_palette == ColorPalette.CYBER_NEON else self.get_color('secondary')
        else:  # accent
            bg_color = self.get_color('accent')
            hover_color = self.get_color('primary')
            glow = self.get_color('glow_pink') if self.current_palette == ColorPalette.CYBER_NEON else self.get_color('accent')

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {self.get_color('text_primary')};
                border: 2px solid {bg_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
                box-shadow: 0 0 20px {glow};
            }}
            QPushButton:pressed {{
                background-color: {self.get_color('surface')};
                transform: scale(0.95);
            }}
            QPushButton:disabled {{
                background-color: {self.get_color('surface')};
                color: {self.get_color('text_secondary')};
                border-color: {self.get_color('surface')};
            }}
        """

    def get_category_button_style(self) -> str:
        """Estilo para botones de categoría en el sidebar"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {self.get_color('text_primary')};
                text-align: left;
                padding: 12px 10px;
                border: none;
                border-left: 3px solid transparent;
                font-size: 11pt;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {self.get_color('surface')};
                border-left: 3px solid {self.get_color('primary')};
            }}
            QPushButton:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.get_color('primary')},
                    stop:1 transparent
                );
                border-left: 3px solid {self.get_color('accent')};
                color: {self.get_color('text_primary')};
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {self.get_color('accent')};
            }}
        """

    def get_floating_panel_style(self) -> str:
        """Estilo para paneles flotantes con glassmorphism"""
        return f"""
            QWidget {{
                background-color: rgba(26, 31, 58, 0.85);
                border: 2px solid {self.get_color('primary')};
                border-radius: 12px;
            }}
        """

    def get_header_style(self) -> str:
        """Estilo para headers de paneles"""
        return f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.get_color('primary')},
                    stop:0.5 {self.get_color('secondary')},
                    stop:1 {self.get_color('accent')}
                );
                border-radius: 10px 10px 0 0;
                border: none;
            }}
        """

    def get_input_style(self) -> str:
        """Estilo para campos de entrada"""
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {self.get_color('surface')};
                color: {self.get_color('text_primary')};
                border: 2px solid {self.get_color('primary')};
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.get_color('accent')};
                box-shadow: 0 0 15px {self.get_color('glow_cyan') if self.current_palette == ColorPalette.CYBER_NEON else self.get_color('primary')};
            }}
            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {self.get_color('background_mid')};
                color: {self.get_color('text_secondary')};
                border-color: {self.get_color('surface')};
            }}
        """

    def get_scrollbar_style(self) -> str:
        """Estilo futurista para scrollbars"""
        return f"""
            QScrollBar:vertical {{
                background-color: {self.get_color('background_mid')};
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.get_color('primary')},
                    stop:1 {self.get_color('secondary')}
                );
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.get_color('accent')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background-color: {self.get_color('background_mid')};
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.get_color('primary')},
                    stop:1 {self.get_color('secondary')}
                );
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {self.get_color('accent')};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """

    def get_label_style(self, label_type: str = 'normal') -> str:
        """Estilos para labels"""
        if label_type == 'title':
            return f"""
                QLabel {{
                    color: {self.get_color('text_primary')};
                    font-size: 14pt;
                    font-weight: bold;
                    background: transparent;
                }}
            """
        elif label_type == 'subtitle':
            return f"""
                QLabel {{
                    color: {self.get_color('text_secondary')};
                    font-size: 11pt;
                    font-weight: 600;
                    background: transparent;
                }}
            """
        else:  # normal
            return f"""
                QLabel {{
                    color: {self.get_color('text_primary')};
                    font-size: 10pt;
                    background: transparent;
                }}
            """

    def get_combobox_style(self) -> str:
        """Estilo para comboboxes"""
        return f"""
            QComboBox {{
                background-color: {self.get_color('surface')};
                color: {self.get_color('text_primary')};
                border: 2px solid {self.get_color('primary')};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }}
            QComboBox:hover {{
                border-color: {self.get_color('accent')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {self.get_color('primary')};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.get_color('surface')};
                color: {self.get_color('text_primary')};
                border: 2px solid {self.get_color('primary')};
                selection-background-color: {self.get_color('primary')};
                selection-color: {self.get_color('text_primary')};
            }}
        """

    def get_checkbox_style(self) -> str:
        """Estilo para checkboxes"""
        return f"""
            QCheckBox {{
                color: {self.get_color('text_primary')};
                spacing: 8px;
                font-size: 10pt;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {self.get_color('primary')};
                border-radius: 4px;
                background-color: {self.get_color('surface')};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.get_color('accent')};
                background-color: {self.get_color('background_mid')};
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.get_color('primary')},
                    stop:1 {self.get_color('secondary')}
                );
                border-color: {self.get_color('accent')};
            }}
        """


# Instancia global del tema
theme = FuturisticTheme(ColorPalette.CYBER_NEON)


def get_theme() -> FuturisticTheme:
    """Obtener instancia del tema actual"""
    return theme


def set_palette(palette: ColorPalette):
    """Cambiar la paleta global"""
    theme.switch_palette(palette)
