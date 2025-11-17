"""
Detector automático de tipos de columnas.

Detecta automáticamente:
- Columnas que contienen URLs o emails
- Columnas que contienen datos sensibles (contraseñas, API keys, etc.)
"""
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ColumnTypeDetector:
    """Detección automática de tipos y características de columnas."""

    # Palabras clave para detección de datos sensibles
    SENSITIVE_KEYWORDS = [
        'password', 'pass', 'pwd', 'contraseña', 'clave',
        'api_key', 'apikey', 'api-key', 'token', 'secret', 'secreto',
        'cvv', 'pin', 'ssn', 'credit_card', 'tarjeta',
        'private_key', 'private-key', 'auth', 'credential',
        'secret_key', 'access_token', 'refresh_token'
    ]

    # Patrones regex para URLs y emails
    URL_PATTERNS = [
        r'https?://',
        r'www\.',
        r'.*\.com',
        r'.*\.org',
        r'.*\.net',
        r'.*\.io',
        r'.*\.dev',
        r'.*@.*\.',  # emails
        r'ftp://',
        r'mailto:',
    ]

    @staticmethod
    def detect_url_column(column_data: List[str], threshold: float = 0.7) -> bool:
        """
        Detecta si una columna contiene URLs/emails.

        Args:
            column_data: Lista de valores de la columna
            threshold: Porcentaje mínimo de matches (0.7 = 70%)

        Returns:
            True si >threshold% de valores parecen URLs

        Example:
            >>> data = ["https://google.com", "https://github.com", "www.example.org"]
            >>> ColumnTypeDetector.detect_url_column(data)
            True
        """
        if not column_data:
            return False

        # Filtrar valores vacíos
        non_empty = [cell for cell in column_data if cell and str(cell).strip()]
        if not non_empty:
            return False

        matches = 0
        for cell in non_empty:
            if not isinstance(cell, str):
                continue

            cell_lower = cell.lower().strip()

            # Verificar contra patrones
            for pattern in ColumnTypeDetector.URL_PATTERNS:
                if re.search(pattern, cell_lower):
                    matches += 1
                    break

        match_ratio = matches / len(non_empty) if non_empty else 0
        logger.debug(f"URL detection: {matches}/{len(non_empty)} = {match_ratio:.2%}")

        return match_ratio >= threshold

    @staticmethod
    def detect_sensitive_column(
        column_name: str,
        column_data: List[str],
        threshold: float = 0.5
    ) -> bool:
        """
        Detecta si una columna contiene datos sensibles.

        Usa dos estrategias:
        1. Detección por nombre de columna (keywords)
        2. Detección por patrón de datos (longitud, caracteres)

        Args:
            column_name: Nombre de la columna
            column_data: Lista de valores de la columna
            threshold: Umbral de confianza para detección por patrón

        Returns:
            True si parece contener datos sensibles

        Example:
            >>> ColumnTypeDetector.detect_sensitive_column("API_KEY", ["sk_live_123", "sk_test_456"])
            True
            >>> ColumnTypeDetector.detect_sensitive_column("PASSWORD", ["pass123", "secret456"])
            True
        """
        # 1. Detectar por nombre de columna
        column_name_lower = column_name.lower()
        for keyword in ColumnTypeDetector.SENSITIVE_KEYWORDS:
            if keyword in column_name_lower:
                logger.info(f"Column '{column_name}' detected as sensitive (keyword: '{keyword}')")
                return True

        # 2. Detectar por patrón de datos
        if not column_data:
            return False

        # Filtrar valores no vacíos
        non_empty = [str(cell).strip() for cell in column_data if cell and str(cell).strip()]
        if not non_empty:
            return False

        # Características típicas de passwords/keys:
        # - Longitud entre 6 y 64 caracteres
        # - Mix de letras y números
        # - Puede tener caracteres especiales
        password_like_count = 0
        sample_size = min(len(non_empty), 10)  # Solo primeras 10 muestras

        for cell in non_empty[:sample_size]:
            if 6 <= len(cell) <= 64:
                has_digit = any(c.isdigit() for c in cell)
                has_alpha = any(c.isalpha() for c in cell)
                has_special = any(not c.isalnum() and c not in (' ', '-', '_') for c in cell)

                # Si tiene mix de tipos de caracteres, probablemente sea sensible
                char_types = sum([has_digit, has_alpha, has_special])
                if char_types >= 2:
                    password_like_count += 1

        pattern_ratio = password_like_count / sample_size if sample_size > 0 else 0

        if pattern_ratio >= threshold:
            logger.info(
                f"Column '{column_name}' detected as sensitive "
                f"(pattern match: {pattern_ratio:.2%})"
            )
            return True

        return False

    @staticmethod
    def auto_detect_column_types(
        columns: List[Dict],
        table_data: List[List[str]],
        enable_url_detection: bool = True,
        enable_sensitive_detection: bool = True
    ) -> List[Dict]:
        """
        Detecta automáticamente tipos de todas las columnas.

        Args:
            columns: Lista de configs de columnas (dicts)
            table_data: Matriz de datos
            enable_url_detection: Habilitar detección de URLs
            enable_sensitive_detection: Habilitar detección de sensibles

        Returns:
            Lista de columnas con tipos detectados y actualizados

        Example:
            >>> columns = [
            ...     {"name": "EMAIL", "type": "TEXT", "is_sensitive": False},
            ...     {"name": "PASSWORD", "type": "TEXT", "is_sensitive": False}
            ... ]
            >>> data = [
            ...     ["user@example.com", "pass123"],
            ...     ["admin@test.com", "secret456"]
            ... ]
            >>> updated = ColumnTypeDetector.auto_detect_column_types(columns, data)
            >>> updated[0]["type"]
            'URL'
            >>> updated[1]["is_sensitive"]
            True
        """
        if not table_data:
            logger.warning("No table data provided for auto-detection")
            return columns

        updated_columns = []
        detections = {
            'url': 0,
            'sensitive': 0
        }

        for col_idx, column in enumerate(columns):
            # Crear copia para no modificar original
            updated_col = column.copy()

            # Extraer datos de esta columna
            column_data = []
            for row in table_data:
                if col_idx < len(row):
                    column_data.append(row[col_idx])
                else:
                    column_data.append('')

            # Detectar URL
            if enable_url_detection and ColumnTypeDetector.detect_url_column(column_data):
                updated_col['type'] = 'URL'
                detections['url'] += 1
                logger.debug(f"Column {col_idx} ('{column['name']}') detected as URL")

            # Detectar sensible
            if enable_sensitive_detection and ColumnTypeDetector.detect_sensitive_column(
                column['name'],
                column_data
            ):
                updated_col['is_sensitive'] = True
                detections['sensitive'] += 1
                logger.debug(f"Column {col_idx} ('{column['name']}') detected as sensitive")

            updated_columns.append(updated_col)

        logger.info(
            f"Auto-detected types for {len(updated_columns)} columns: "
            f"{detections['url']} URLs, {detections['sensitive']} sensitive"
        )

        return updated_columns

    @staticmethod
    def get_detection_summary(
        original_columns: List[Dict],
        detected_columns: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Genera resumen de cambios detectados.

        Args:
            original_columns: Columnas originales
            detected_columns: Columnas después de detección

        Returns:
            Dict con listas de cambios:
                - 'url_detected': nombres de columnas detectadas como URL
                - 'sensitive_detected': nombres de columnas detectadas como sensibles
        """
        summary = {
            'url_detected': [],
            'sensitive_detected': []
        }

        for orig, detected in zip(original_columns, detected_columns):
            # URL detectada
            if orig.get('type') != 'URL' and detected.get('type') == 'URL':
                summary['url_detected'].append(detected['name'])

            # Sensible detectado
            if not orig.get('is_sensitive') and detected.get('is_sensitive'):
                summary['sensitive_detected'].append(detected['name'])

        return summary
