"""
File Manager - Gestión Avanzada de Archivos para Items TYPE PATH
Fase 3 - Plan de Implementación PATH Avanzado

Responsabilidades:
- Gestionar copia de archivos a carpetas organizadas
- Extraer metadatos básicos
- Calcular hash SHA256
- Detectar duplicados
- Validar existencia de archivos
"""

import os
import sys
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.item import Item

logger = logging.getLogger(__name__)


# ==================== Constantes ====================

# Mapeo de extensiones de archivo a tipos
FOLDER_MAPPING = {
    'IMAGENES': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'],
    'VIDEOS': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
    'PDFS': ['.pdf'],
    'WORDS': ['.doc', '.docx', '.odt', '.rtf'],
    'EXCELS': ['.xls', '.xlsx', '.csv', '.ods'],
    'TEXT': ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg'],
    'OTROS': []  # Fallback para archivos desconocidos
}

# Iconos emoji por tipo de archivo
FILE_TYPE_ICONS = {
    'IMAGEN': '🖼️',
    'VIDEO': '🎬',
    'PDF': '📕',
    'WORD': '📘',
    'EXCEL': '📊',
    'TEXT': '📄',
    'OTROS': '📎'
}


# ==================== FileManager Class ====================

class FileManager:
    """
    Gestor de archivos para items con tipo PATH

    Maneja la organización, copia, metadatos y validación de archivos
    almacenados como items en la aplicación.
    """

    def __init__(self, config_manager):
        """
        Inicializa el FileManager

        Args:
            config_manager: Instancia de ConfigManager para acceder a configuración
        """
        self.config_manager = config_manager
        self.db_manager = config_manager.db
        logger.info("FileManager initialized")

    # ==================== Métodos de Configuración ====================

    def get_base_path(self) -> str:
        """
        Obtiene la ruta base de almacenamiento de archivos

        Returns:
            str: Ruta base configurada (puede ser vacía si no está configurada)
        """
        return self.config_manager.get_files_base_path()

    def set_base_path(self, path: str) -> bool:
        """
        Establece la ruta base de almacenamiento de archivos

        Args:
            path: Ruta absoluta al directorio base

        Returns:
            bool: True si se estableció correctamente

        Raises:
            ValueError: Si la ruta no es válida o no tiene permisos
        """
        path_obj = Path(path)

        # Validar que es una ruta absoluta
        if not path_obj.is_absolute():
            raise ValueError(f"La ruta debe ser absoluta: {path}")

        # Si la ruta no existe, intentar crearla
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created base path: {path}")
            except PermissionError:
                raise ValueError(f"No hay permisos para crear el directorio: {path}")
            except Exception as e:
                raise ValueError(f"Error al crear directorio: {e}")

        # Validar que es un directorio
        if not path_obj.is_dir():
            raise ValueError(f"La ruta debe ser un directorio: {path}")

        # Validar permisos de escritura
        if not os.access(path, os.W_OK):
            raise ValueError(f"No hay permisos de escritura en: {path}")

        # Guardar configuración
        success = self.config_manager.set_files_base_path(path)
        if success:
            logger.info(f"Base path set to: {path}")
        return success

    def get_folders_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración de carpetas por tipo de archivo

        Returns:
            Dict[str, str]: Diccionario con mapeo tipo -> nombre_carpeta
        """
        return self.config_manager.get_files_folders_config()

    def update_folders_config(self, config: Dict[str, str]) -> bool:
        """
        Actualiza la configuración de carpetas

        Args:
            config: Diccionario con mapeo tipo -> nombre_carpeta

        Returns:
            bool: True si se actualizó correctamente
        """
        return self.config_manager.set_files_folders_config(config)

    def get_auto_create_folders(self) -> bool:
        """
        Obtiene el estado de auto-creación de carpetas

        Returns:
            bool: True si está habilitado
        """
        return self.config_manager.get_files_auto_create_folders()

    # ==================== Detección Automática ====================

    def detect_file_type(self, extension: str) -> str:
        """
        Detecta el tipo de archivo basado en su extensión

        Args:
            extension: Extensión del archivo (con o sin punto)

        Returns:
            str: Tipo de archivo (IMAGEN, VIDEO, PDF, WORD, EXCEL, TEXT, OTROS)
        """
        # Normalizar extensión (agregar punto si no lo tiene, lowercase)
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = '.' + ext

        # Buscar en el mapeo
        for file_type, extensions in FOLDER_MAPPING.items():
            if ext in extensions:
                # Normalizar nombre de tipo
                if file_type == 'IMAGENES':
                    return 'IMAGEN'
                elif file_type == 'VIDEOS':
                    return 'VIDEO'
                elif file_type == 'PDFS':
                    return 'PDF'
                elif file_type == 'WORDS':
                    return 'WORD'
                elif file_type == 'EXCELS':
                    return 'EXCEL'
                elif file_type == 'TEXT':
                    return 'TEXT'

        return 'OTROS'

    def get_target_folder(self, extension: str) -> str:
        """
        Obtiene la carpeta destino para un archivo basado en su extensión

        Args:
            extension: Extensión del archivo (con o sin punto)

        Returns:
            str: Nombre de la carpeta destino
        """
        # Normalizar extensión
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = '.' + ext

        # Buscar en el mapeo de carpetas
        for folder_type, extensions in FOLDER_MAPPING.items():
            if ext in extensions:
                # Obtener nombre de carpeta de la configuración
                folders_config = self.get_folders_config()
                return folders_config.get(folder_type, folder_type)

        # Fallback a OTROS
        folders_config = self.get_folders_config()
        return folders_config.get('OTROS', 'OTROS')

    # ==================== Gestión de Archivos ====================

    def copy_file_to_storage(self, source_path: str) -> Dict[str, any]:
        """
        Copia un archivo al almacenamiento organizado y extrae metadatos

        Args:
            source_path: Ruta absoluta al archivo fuente

        Returns:
            Dict con los siguientes campos:
                - full_path: Ruta completa del archivo copiado
                - file_size: Tamaño en bytes
                - file_type: Tipo detectado (IMAGEN, VIDEO, etc.)
                - file_extension: Extensión con punto
                - original_filename: Nombre original del archivo
                - file_hash: Hash SHA256 del archivo

        Raises:
            ValueError: Si la ruta base no está configurada o el archivo no existe
            IOError: Si hay error al copiar el archivo
        """
        # Validar que el archivo existe
        source = Path(source_path)
        if not source.exists():
            raise ValueError(f"El archivo no existe: {source_path}")

        if not source.is_file():
            raise ValueError(f"La ruta no es un archivo: {source_path}")

        # Validar que la ruta base está configurada
        base_path = self.get_base_path()
        if not base_path:
            raise ValueError("La ruta base de almacenamiento no está configurada")

        # Extraer información del archivo
        original_filename = source.name
        file_extension = source.suffix.lower()
        file_type = self.detect_file_type(file_extension)
        target_folder = self.get_target_folder(file_extension)

        # Construir ruta destino
        dest_dir = Path(base_path) / target_folder

        # Crear carpeta si no existe (si está habilitado)
        if self.get_auto_create_folders():
            self.ensure_folder_exists(str(dest_dir))

        # Validar que la carpeta destino existe
        if not dest_dir.exists():
            raise ValueError(f"La carpeta destino no existe: {dest_dir}")

        # Manejar archivos con nombre duplicado
        dest_file = dest_dir / original_filename
        if dest_file.exists():
            # Agregar timestamp al nombre
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_without_ext = source.stem
            dest_file = dest_dir / f"{name_without_ext}_{timestamp}{file_extension}"

        # Copiar archivo
        try:
            shutil.copy2(source, dest_file)
            logger.info(f"File copied: {source} -> {dest_file}")
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            raise IOError(f"Error al copiar archivo: {e}")

        # Calcular metadatos
        file_size = dest_file.stat().st_size
        file_hash = self.calculate_file_hash(str(dest_file))

        # Construir ruta relativa (portable)
        # Formato: CARPETA/archivo.ext
        relative_path = f"{target_folder}/{original_filename}"
        if dest_file.name != original_filename:
            # Si se le agregó timestamp, usar el nombre real
            relative_path = f"{target_folder}/{dest_file.name}"

        return {
            'success': True,
            'destination_path': str(dest_file),  # Ruta completa (temporal, para preview)
            'relative_path': relative_path,      # Ruta relativa (PORTABLE - se guarda en DB)
            'file_size': file_size,
            'file_type': file_type,
            'file_extension': file_extension,
            'original_filename': original_filename,
            'file_hash': file_hash
        }

    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calcula el hash SHA256 de un archivo

        Args:
            file_path: Ruta al archivo

        Returns:
            str: Hash SHA256 en formato hexadecimal

        Raises:
            ValueError: Si el archivo no existe
            IOError: Si hay error al leer el archivo
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"El archivo no existe: {file_path}")

        sha256 = hashlib.sha256()

        try:
            with open(path, 'rb') as f:
                # Leer en bloques para archivos grandes
                for block in iter(lambda: f.read(4096), b''):
                    sha256.update(block)
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            raise IOError(f"Error al calcular hash: {e}")

        return sha256.hexdigest()

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Convierte una ruta relativa a ruta absoluta usando la configuración actual

        Args:
            relative_path: Ruta relativa (ej: "IMAGENES/test.jpg")

        Returns:
            str: Ruta absoluta completa

        Raises:
            ValueError: Si la ruta base no está configurada
        """
        base_path = self.get_base_path()
        if not base_path:
            raise ValueError("La ruta base de almacenamiento no está configurada")

        # Normalizar separadores (Windows vs Unix)
        relative_path = relative_path.replace('\\', '/')

        # Construir ruta completa
        absolute_path = Path(base_path) / relative_path

        return str(absolute_path)

    def check_duplicate(self, file_hash: str) -> Optional[Item]:
        """
        Verifica si ya existe un archivo con el mismo hash

        Args:
            file_hash: Hash SHA256 del archivo

        Returns:
            Optional[Item]: Item existente con el mismo hash, o None si no existe
        """
        # Buscar en la base de datos
        try:
            duplicate = self.db_manager.get_item_by_hash(file_hash)
            if duplicate:
                logger.info(f"Duplicate file found: {duplicate.get('label', 'Unknown')}")
                # Convertir dict a Item si es necesario
                # Aquí podrías usar el método _dict_to_item del ConfigManager
                # Por ahora retornamos el dict
                return duplicate
            return None
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return None

    def validate_file_exists(self, file_path: str) -> bool:
        """
        Valida que un archivo existe en el sistema

        Args:
            file_path: Ruta al archivo

        Returns:
            bool: True si el archivo existe y es accesible
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False

    def get_file_metadata(self, file_path: str) -> Dict[str, any]:
        """
        Extrae metadatos de un archivo sin copiarlo

        Args:
            file_path: Ruta al archivo

        Returns:
            Dict con metadatos:
                - file_size: Tamaño en bytes
                - file_type: Tipo detectado
                - file_extension: Extensión
                - original_filename: Nombre del archivo
                - file_hash: Hash SHA256

        Raises:
            ValueError: Si el archivo no existe
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"El archivo no existe: {file_path}")

        if not path.is_file():
            raise ValueError(f"La ruta no es un archivo: {file_path}")

        # Extraer metadatos
        original_filename = path.name
        file_extension = path.suffix.lower()
        file_type = self.detect_file_type(file_extension)
        file_size = path.stat().st_size
        file_hash = self.calculate_file_hash(file_path)

        return {
            'file_size': file_size,
            'file_type': file_type,
            'file_extension': file_extension,
            'original_filename': original_filename,
            'file_hash': file_hash
        }

    # ==================== Utilidades ====================

    def format_file_size(self, size_bytes: int) -> str:
        """
        Formatea el tamaño de archivo en formato legible

        Args:
            size_bytes: Tamaño en bytes

        Returns:
            str: Tamaño formateado (ej: "2.5 MB", "1.2 GB")
        """
        if size_bytes < 0:
            return "0 B"

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0

        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1

        # Formatear con decimales apropiados
        if unit_index == 0:  # Bytes
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"

    def ensure_folder_exists(self, folder_path: str) -> bool:
        """
        Asegura que una carpeta existe, creándola si es necesario

        Args:
            folder_path: Ruta a la carpeta

        Returns:
            bool: True si la carpeta existe o fue creada exitosamente

        Raises:
            PermissionError: Si no hay permisos para crear la carpeta
        """
        path = Path(folder_path)

        if path.exists():
            if path.is_dir():
                return True
            else:
                raise ValueError(f"La ruta existe pero no es un directorio: {folder_path}")

        # Crear carpeta
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return True
        except PermissionError:
            logger.error(f"Permission denied creating folder: {folder_path}")
            raise
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return False

    def get_file_icon_by_type(self, file_type: str) -> str:
        """
        Obtiene el icono emoji para un tipo de archivo

        Args:
            file_type: Tipo de archivo (IMAGEN, VIDEO, etc.)

        Returns:
            str: Emoji representativo del tipo
        """
        return FILE_TYPE_ICONS.get(file_type.upper(), FILE_TYPE_ICONS['OTROS'])

    def get_file_icon_by_extension(self, extension: str) -> str:
        """
        Obtiene el icono emoji basado en la extensión del archivo

        Args:
            extension: Extensión del archivo (con o sin punto)

        Returns:
            str: Emoji representativo
        """
        file_type = self.detect_file_type(extension)
        return self.get_file_icon_by_type(file_type)

    def get_storage_stats(self) -> Dict[str, any]:
        """
        Obtiene estadísticas del almacenamiento de archivos

        Returns:
            Dict con estadísticas:
                - total_items: Total de items PATH
                - total_size: Tamaño total en bytes
                - total_size_formatted: Tamaño formateado
                - by_type: Diccionario con conteo por tipo
        """
        try:
            # Obtener todos los items de tipo PATH
            # Nota: esto requeriría un método en DBManager para filtrar por tipo
            # Por ahora retornamos estructura básica
            stats = {
                'total_items': 0,
                'total_size': 0,
                'total_size_formatted': '0 B',
                'by_type': {}
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                'total_items': 0,
                'total_size': 0,
                'total_size_formatted': '0 B',
                'by_type': {}
            }
