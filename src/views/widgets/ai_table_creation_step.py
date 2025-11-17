"""
AI Table Creation Step - Paso 5: Creación de tabla en BD

Este step:
- Muestra resumen pre-creación
- Ejecuta creación con progress bar
- Muestra log en tiempo real
- Muestra resultado final
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ai_table_manager import AITableManager
from models.ai_table_data import AITableData

logger = logging.getLogger(__name__)


class CreationWorker(QThread):
    """Worker thread para creación de tabla."""

    progress = pyqtSignal(int, str)  # (percentage, message)
    finished = pyqtSignal(bool, dict)  # (success, result)

    def __init__(self, ai_manager: AITableManager, ai_table: AITableData):
        super().__init__()
        self.ai_manager = ai_manager
        self.ai_table = ai_table

    def run(self):
        """Ejecuta la creación."""
        try:
            self.progress.emit(10, "Validando datos...")

            self.progress.emit(30, "Preparando items...")

            self.progress.emit(50, "Creando tabla en base de datos...")

            # Crear tabla
            result = self.ai_manager.create_table_from_ai(self.ai_table)

            self.progress.emit(90, "Finalizando...")

            self.progress.emit(100, "Completado")

            # Emitir resultado
            self.finished.emit(result.get('success', False), result)

        except Exception as e:
            logger.error(f"Error in creation worker: {e}", exc_info=True)
            self.finished.emit(False, {
                'success': False,
                'errors': [str(e)],
                'items_created': 0
            })


class AITableCreationStep(QWidget):
    """Step 5: Creación de tabla."""

    creation_finished = pyqtSignal(bool, int)  # (success, items_created)

    def __init__(self, ai_manager: AITableManager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.ai_table = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Título
        title = QLabel("🚀 Creación de Tabla")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; padding: 10px;")
        layout.addWidget(title)

        # Resumen
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 15px;
                color: #cccccc;
                font-size: 10pt;
            }
        """)
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #1e1e1e;
                text-align: center;
                color: #cccccc;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Esperando...")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        layout.addWidget(self.status_label)

        # Log
        log_label = QLabel("Log de Creación:")
        log_label.setStyleSheet("color: #cccccc; font-size: 10pt; font-weight: bold;")
        layout.addWidget(log_label)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 10px;
                color: #cccccc;
                font-family: monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.log_display, 1)

        # Resultado final
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #2d4d2d;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 20px;
                color: #ffffff;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        self.result_label.setWordWrap(True)
        self.result_label.setVisible(False)
        layout.addWidget(self.result_label)

    def set_table_data(self, ai_table: AITableData):
        """Establece los datos de la tabla."""
        self.ai_table = ai_table

        # Mostrar resumen
        summary = (
            f"Tabla: {ai_table.table_config.table_name}\n"
            f"Categoría ID: {ai_table.table_config.category_id}\n"
            f"Dimensiones: {ai_table.rows_count} filas × {ai_table.cols_count} columnas\n"
            f"Items a crear: {ai_table.filled_cells_count}\n"
            f"Columnas sensibles: {len(ai_table.table_structure.get_sensitive_indices())}\n"
            f"Columnas URL: {len(ai_table.table_structure.get_url_indices())}"
        )
        self.summary_label.setText(summary)

    def start_creation(self):
        """Inicia el proceso de creación."""
        if not self.ai_table:
            logger.error("No table data to create")
            return

        self.log("Iniciando creación de tabla...")

        # Crear worker
        self.worker = CreationWorker(self.ai_manager, self.ai_table)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, percentage: int, message: str):
        """Actualiza el progreso."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self.log(f"[{percentage}%] {message}")

    def on_finished(self, success: bool, result: dict):
        """Callback cuando termina la creación."""
        if success:
            items_created = result.get('items_created', 0)

            self.log(f"\n[OK] Tabla creada exitosamente!")
            self.log(f"Items creados: {items_created}")

            # Mostrar resultado
            self.result_label.setText(
                f"✓ TABLA CREADA EXITOSAMENTE\n\n"
                f"Items creados: {items_created}\n"
                f"Tabla: {self.ai_table.table_config.table_name}"
            )
            self.result_label.setVisible(True)

            # Emitir señal
            self.creation_finished.emit(True, items_created)

        else:
            errors = result.get('errors', ['Error desconocido'])
            self.log(f"\n[ERROR] Creación fallida:")
            for error in errors:
                self.log(f"  - {error}")

            # Mostrar resultado de error
            self.result_label.setText(
                f"✗ ERROR AL CREAR TABLA\n\n"
                f"Errores:\n" + "\n".join(f"• {e}" for e in errors[:3])
            )
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #4d2d2d;
                    border: 2px solid #dd4444;
                    border-radius: 5px;
                    padding: 20px;
                    color: #ffffff;
                    font-size: 11pt;
                    font-weight: bold;
                }
            """)
            self.result_label.setVisible(True)

            # Emitir señal
            self.creation_finished.emit(False, 0)

    def log(self, message: str):
        """Agrega mensaje al log."""
        self.log_display.append(message)

    def is_valid(self) -> bool:
        """Siempre válido (último paso)."""
        return True

    def get_validation_message(self) -> str:
        """Mensaje de validación."""
        return "Listo para crear."
