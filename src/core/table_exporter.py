"""
Table Exporter
Utilidades para exportar tablas a diferentes formatos (CSV, JSON, Excel)
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TableExporter:
    """
    Clase para exportar tablas a diferentes formatos.

    Soporta:
    - CSV (Comma Separated Values)
    - JSON (con estructura y metadatos)
    - TSV (Tab Separated Values)
    """

    @staticmethod
    def export_to_csv(
        table_data: List[List[str]],
        column_names: List[str],
        output_path: str,
        include_headers: bool = True,
        delimiter: str = ','
    ) -> bool:
        """
        Exporta tabla a archivo CSV.

        Args:
            table_data: Matriz de datos
            column_names: Nombres de columnas
            output_path: Ruta del archivo de salida
            include_headers: Si incluir fila de headers
            delimiter: Delimitador (default: coma)

        Returns:
            bool: True si exportación exitosa
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=delimiter)

                # Escribir headers
                if include_headers:
                    writer.writerow(column_names)

                # Escribir datos
                for row in table_data:
                    writer.writerow(row)

            logger.info(f"Table exported to CSV: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}", exc_info=True)
            return False

    @staticmethod
    def export_to_tsv(
        table_data: List[List[str]],
        column_names: List[str],
        output_path: str,
        include_headers: bool = True
    ) -> bool:
        """
        Exporta tabla a archivo TSV (Tab Separated Values).

        Args:
            table_data: Matriz de datos
            column_names: Nombres de columnas
            output_path: Ruta del archivo de salida
            include_headers: Si incluir fila de headers

        Returns:
            bool: True si exportación exitosa
        """
        return TableExporter.export_to_csv(
            table_data,
            column_names,
            output_path,
            include_headers,
            delimiter='\t'
        )

    @staticmethod
    def export_to_json(
        table_name: str,
        table_data: List[List[str]],
        column_names: List[str],
        output_path: str,
        include_metadata: bool = True,
        pretty: bool = True
    ) -> bool:
        """
        Exporta tabla a archivo JSON.

        Estructura del JSON:
        {
            "table_name": "TABLA_EJEMPLO",
            "columns": ["COL1", "COL2", "COL3"],
            "rows": [
                ["valor1", "valor2", "valor3"],
                ["valor4", "valor5", "valor6"]
            ],
            "metadata": {
                "exported_at": "2024-01-15T10:30:00",
                "row_count": 2,
                "column_count": 3
            }
        }

        Args:
            table_name: Nombre de la tabla
            table_data: Matriz de datos
            column_names: Nombres de columnas
            output_path: Ruta del archivo de salida
            include_metadata: Si incluir metadatos
            pretty: Si formatear JSON con indentación

        Returns:
            bool: True si exportación exitosa
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Construir estructura JSON
            json_data = {
                "table_name": table_name,
                "columns": column_names,
                "rows": table_data
            }

            # Agregar metadata
            if include_metadata:
                json_data["metadata"] = {
                    "exported_at": datetime.now().isoformat(),
                    "row_count": len(table_data),
                    "column_count": len(column_names)
                }

            # Escribir archivo
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(json_data, f, ensure_ascii=False)

            logger.info(f"Table exported to JSON: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}", exc_info=True)
            return False

    @staticmethod
    def export_to_json_records(
        table_name: str,
        table_data: List[List[str]],
        column_names: List[str],
        output_path: str,
        include_metadata: bool = True,
        pretty: bool = True
    ) -> bool:
        """
        Exporta tabla a JSON en formato de registros (lista de objetos).

        Estructura del JSON:
        {
            "table_name": "TABLA_EJEMPLO",
            "records": [
                {"COL1": "valor1", "COL2": "valor2", "COL3": "valor3"},
                {"COL1": "valor4", "COL2": "valor5", "COL3": "valor6"}
            ],
            "metadata": {...}
        }

        Args:
            table_name: Nombre de la tabla
            table_data: Matriz de datos
            column_names: Nombres de columnas
            output_path: Ruta del archivo de salida
            include_metadata: Si incluir metadatos
            pretty: Si formatear JSON con indentación

        Returns:
            bool: True si exportación exitosa
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convertir filas a registros (objetos)
            records = []
            for row in table_data:
                record = {}
                for col_idx, col_name in enumerate(column_names):
                    if col_idx < len(row):
                        record[col_name] = row[col_idx]
                    else:
                        record[col_name] = ""
                records.append(record)

            # Construir estructura JSON
            json_data = {
                "table_name": table_name,
                "records": records
            }

            # Agregar metadata
            if include_metadata:
                json_data["metadata"] = {
                    "exported_at": datetime.now().isoformat(),
                    "record_count": len(records),
                    "column_count": len(column_names)
                }

            # Escribir archivo
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(json_data, f, ensure_ascii=False)

            logger.info(f"Table exported to JSON (records): {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to JSON records: {e}", exc_info=True)
            return False

    @staticmethod
    def get_export_summary(
        table_name: str,
        table_data: List[List[str]],
        column_names: List[str]
    ) -> Dict[str, Any]:
        """
        Genera resumen de exportación.

        Args:
            table_name: Nombre de la tabla
            table_data: Matriz de datos
            column_names: Nombres de columnas

        Returns:
            Dict con estadísticas de la tabla
        """
        # Contar celdas llenas
        filled_cells = sum(1 for row in table_data for cell in row if cell and str(cell).strip())
        total_cells = len(table_data) * len(column_names)

        # Calcular tamaño aproximado
        total_chars = sum(len(str(cell)) for row in table_data for cell in row)

        return {
            "table_name": table_name,
            "rows": len(table_data),
            "columns": len(column_names),
            "filled_cells": filled_cells,
            "total_cells": total_cells,
            "fill_percentage": round((filled_cells / total_cells * 100), 2) if total_cells > 0 else 0,
            "total_characters": total_chars,
            "estimated_size_kb": round(total_chars / 1024, 2)
        }

    @staticmethod
    def validate_export_data(
        table_data: List[List[str]],
        column_names: List[str]
    ) -> tuple:
        """
        Valida que los datos sean exportables.

        Args:
            table_data: Matriz de datos
            column_names: Nombres de columnas

        Returns:
            Tuple (is_valid, error_message)
        """
        # Validar que haya datos
        if not table_data:
            return False, "No hay datos para exportar"

        # Validar que haya columnas
        if not column_names:
            return False, "No hay nombres de columnas"

        # Validar que todas las filas tengan el mismo número de columnas
        expected_cols = len(column_names)
        for row_idx, row in enumerate(table_data):
            if len(row) != expected_cols:
                logger.warning(f"Row {row_idx} has {len(row)} columns, expected {expected_cols}")
                # No es error fatal, solo advertencia

        return True, ""

    @staticmethod
    def get_suggested_filename(table_name: str, format: str) -> str:
        """
        Genera nombre de archivo sugerido.

        Args:
            table_name: Nombre de la tabla
            format: Formato (csv, json, tsv)

        Returns:
            Nombre de archivo sugerido
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = table_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        return f"{safe_name}_{timestamp}.{format.lower()}"
