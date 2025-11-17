"""
Speed Dial Generator - Genera página HTML personalizada para accesos rápidos
Author: Widget Sidebar Team
Date: 2025-11-02
"""

import logging
from pathlib import Path
from typing import List, Dict
import base64

logger = logging.getLogger(__name__)


class SpeedDialGenerator:
    """Generador de página HTML para Speed Dial."""

    def __init__(self, db_manager):
        """
        Inicializa el generador.

        Args:
            db_manager: Instancia de DBManager
        """
        self.db = db_manager

    def generate_html(self) -> str:
        """
        Genera el HTML completo del Speed Dial.

        Returns:
            str: HTML completo de la página
        """
        speed_dials = self.db.get_speed_dials()

        # Generar los tiles HTML
        tiles_html = self._generate_tiles(speed_dials)

        # Template HTML completo
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speed Dial</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            overflow-y: auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            animation: fadeIn 0.8s ease-in;
        }}

        .header h1 {{
            color: #00d4ff;
            font-size: 42px;
            font-weight: 300;
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            margin-bottom: 10px;
        }}

        .header p {{
            color: #808080;
            font-size: 14px;
            letter-spacing: 1px;
        }}

        .speed-dial-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 25px;
            max-width: 1200px;
            width: 100%;
            animation: slideUp 0.8s ease-out;
        }}

        .speed-dial-tile {{
            background: rgba(22, 33, 62, 0.8);
            border: 2px solid #0f3460;
            border-radius: 15px;
            padding: 25px;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 15px;
            min-height: 180px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}

        .speed-dial-tile::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, transparent 0%, rgba(0, 212, 255, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .speed-dial-tile:hover {{
            transform: translateY(-5px) scale(1.02);
            border-color: #00d4ff;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }}

        .speed-dial-tile:hover::before {{
            opacity: 1;
        }}

        .speed-dial-icon {{
            font-size: 56px;
            line-height: 1;
            transition: transform 0.3s ease;
            z-index: 1;
        }}

        .speed-dial-tile:hover .speed-dial-icon {{
            transform: scale(1.15) rotate(5deg);
        }}

        .speed-dial-title {{
            color: #00d4ff;
            font-size: 16px;
            font-weight: 500;
            text-align: center;
            word-wrap: break-word;
            max-width: 100%;
            z-index: 1;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}

        .speed-dial-url {{
            color: #808080;
            font-size: 11px;
            text-align: center;
            word-wrap: break-word;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            z-index: 1;
        }}

        .add-new-tile {{
            background: rgba(15, 52, 96, 0.5);
            border: 2px dashed #00d4ff;
            cursor: pointer;
        }}

        .add-new-tile:hover {{
            background: rgba(0, 212, 255, 0.1);
            border-style: solid;
        }}

        .add-icon {{
            font-size: 48px;
            color: #00d4ff;
        }}

        .empty-state {{
            text-align: center;
            color: #808080;
            padding: 60px 20px;
            animation: fadeIn 1s ease-in;
        }}

        .empty-state-icon {{
            font-size: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }}

        .empty-state p {{
            font-size: 18px;
            margin-bottom: 10px;
        }}

        .empty-state small {{
            font-size: 14px;
            opacity: 0.7;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Scrollbar personalizado */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: rgba(15, 15, 30, 0.5);
        }}

        ::-webkit-scrollbar-thumb {{
            background: #00d4ff;
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #00b8e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Accesos Rápidos</h1>
        <p>Tus sitios favoritos a un click de distancia</p>
    </div>

    {tiles_html}

    <script>
        // Evento para agregar nuevo speed dial
        document.getElementById('add-new-btn')?.addEventListener('click', function(e) {{
            e.preventDefault();
            // Enviar señal al navegador cambiando el título
            document.title = '__SPEED_DIAL_ADD_NEW__';
            // Restaurar título después de 100ms
            setTimeout(() => {{
                document.title = 'Speed Dial';
            }}, 100);
        }});

        // Agregar animación de entrada escalonada a los tiles
        const tiles = document.querySelectorAll('.speed-dial-tile');
        tiles.forEach((tile, index) => {{
            tile.style.animation = `slideUp 0.5s ease-out ${{index * 0.05}}s both`;
        }});
    </script>
</body>
</html>
"""
        return html

    def _generate_tiles(self, speed_dials: List[Dict]) -> str:
        """
        Genera el HTML de los tiles de speed dial.

        Args:
            speed_dials: Lista de speed dials desde la DB

        Returns:
            str: HTML de los tiles
        """
        if not speed_dials:
            return """
    <div class="empty-state">
        <div class="empty-state-icon">🚀</div>
        <p>¡Aún no tienes accesos rápidos!</p>
        <small>Haz click en el botón "+" para agregar tus sitios favoritos</small>
    </div>
    <div class="speed-dial-container">
        <a href="speed-dial://add-new" class="speed-dial-tile add-new-tile" id="add-new-btn">
            <div class="add-icon">+</div>
            <div class="speed-dial-title">Agregar Nuevo</div>
        </a>
    </div>
"""

        tiles_html = '<div class="speed-dial-container">\n'

        # Generar tile para cada speed dial
        for sd in speed_dials:
            icon = sd.get('icon', '🌐')
            title = sd.get('title', 'Sin título')
            url = sd.get('url', '')
            bg_color = sd.get('background_color', '#16213e')

            # Truncar URL para mostrar
            display_url = url[:40] + '...' if len(url) > 40 else url

            tiles_html += f"""
        <a href="{url}" class="speed-dial-tile" style="background-color: {bg_color};">
            <div class="speed-dial-icon">{icon}</div>
            <div class="speed-dial-title">{title}</div>
            <div class="speed-dial-url">{display_url}</div>
        </a>
"""

        # Agregar botón de "Agregar Nuevo"
        tiles_html += """
        <a href="speed-dial://add-new" class="speed-dial-tile add-new-tile" id="add-new-btn">
            <div class="add-icon">+</div>
            <div class="speed-dial-title">Agregar Nuevo</div>
        </a>
"""

        tiles_html += '    </div>\n'

        return tiles_html

    def save_to_file(self, file_path: str = None) -> str:
        """
        Guarda la página HTML en un archivo.

        Args:
            file_path: Ruta donde guardar (opcional, usa default si no se especifica)

        Returns:
            str: Ruta del archivo guardado
        """
        if file_path is None:
            # Usar ruta por defecto en carpeta temporal o app
            file_path = Path.cwd() / "speed_dial.html"

        try:
            html_content = self.generate_html()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Speed Dial HTML guardado en: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error al guardar Speed Dial HTML: {e}")
            return None
