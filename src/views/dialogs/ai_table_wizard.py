"""
AI Table Creator Wizard - Wizard para creación de tablas con IA

Este wizard guía al usuario a través de 5 pasos:
1. Configuración: Nombre, categoría, contexto, filas esperadas
2. Generación de Prompt: Prompt personalizado para copiar a IA
3. Importación JSON: Pegar y validar JSON de IA
4. Previsualización: Editar tabla, columnas y datos
5. Creación: Inserción masiva en BD con progress
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_manager import DBManager
from core.ai_table_manager import AITableManager
from views.widgets.ai_table_config_step import AITableConfigStep
from views.widgets.ai_table_prompt_step import AITablePromptStep
from views.widgets.ai_table_json_step import AITableJSONStep
from views.widgets.ai_table_preview_step import AITablePreviewStep
from views.widgets.ai_table_creation_step import AITableCreationStep

logger = logging.getLogger(__name__)


class AITableCreatorWizard(QDialog):
    """
    Wizard para creación de tablas con IA.

    Señales:
        table_created(str, int): Emitida cuando se crea una tabla (nombre, items_count)
    """

    table_created = pyqtSignal(str, int)  # (table_name, items_created)

    def __init__(self, db_manager: DBManager, controller=None, parent=None):
        """
        Inicializa el wizard.

        Args:
            db_manager: Instancia de DBManager para acceso a BD
            controller: MainController para acceso a categorías
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = db_manager
        self.controller = controller

        # Inicializar AITableManager
        self.ai_manager = AITableManager(db_manager)

        self.current_step = 0
        self.total_steps = 5

        # Data compartida entre steps
        self.prompt_config = None  # Config para generar prompt (AITablePromptConfig)
        self.generated_prompt = None  # Prompt generado (str)
        self.json_text = None  # JSON pegado por usuario (str)
        self.ai_table = None  # Datos parseados (AITableData)

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del wizard."""
        self.setWindowTitle("Crear Tabla con IA")
        self.setFixedSize(900, 750)
        self.setModal(True)

        # Aplicar tema oscuro
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #666666;
                border: 1px solid #2d2d2d;
            }
            QPushButton#next_button, QPushButton#finish_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#next_button:hover, QPushButton#finish_button:hover {
                background-color: #005a9e;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header con título y progreso
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Paso 1: Configuración de Prompt")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.progress_label = QLabel("1 / 5")
        self.progress_label.setStyleSheet("color: #888888; font-size: 11pt;")
        header_layout.addWidget(self.progress_label)

        main_layout.addLayout(header_layout)

        # Stepper visual
        self.stepper_label = QLabel()
        self.stepper_label.setStyleSheet("color: #00d4ff; font-family: monospace;")
        self.update_stepper()
        main_layout.addWidget(self.stepper_label)

        # Separador
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3d3d3d;")
        main_layout.addWidget(separator)

        # Stacked widget para los pasos
        self.stacked_widget = QStackedWidget()

        # Crear steps
        self.step1 = AITableConfigStep(self.db, self.controller, self)
        self.step2 = AITablePromptStep(self)
        self.step3 = AITableJSONStep(self.ai_manager, self)
        self.step4 = AITablePreviewStep(self)
        self.step5 = AITableCreationStep(self.ai_manager, self)

        self.stacked_widget.addWidget(self.step1)
        self.stacked_widget.addWidget(self.step2)
        self.stacked_widget.addWidget(self.step3)
        self.stacked_widget.addWidget(self.step4)
        self.stacked_widget.addWidget(self.step5)

        main_layout.addWidget(self.stacked_widget, 1)

        # Botones de navegación
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        self.prev_button = QPushButton("← Anterior")
        self.prev_button.clicked.connect(self.go_previous)
        self.prev_button.setEnabled(False)
        buttons_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Siguiente →")
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(self.go_next)
        buttons_layout.addWidget(self.next_button)

        self.finish_button = QPushButton("Crear Tabla")
        self.finish_button.setObjectName("finish_button")
        self.finish_button.clicked.connect(self.finish)
        self.finish_button.setVisible(False)
        buttons_layout.addWidget(self.finish_button)

        main_layout.addLayout(buttons_layout)

    def update_stepper(self):
        """Actualiza el stepper visual."""
        steps = []
        for i in range(self.total_steps):
            if i < self.current_step:
                steps.append("(✓)")
            elif i == self.current_step:
                steps.append("(•)")
            else:
                steps.append("( )")

        stepper_text = "──".join(steps)
        labels = ["Config", "Prompt", "JSON", "Preview", "Crear"]

        self.stepper_label.setText(f"{stepper_text}\n{(' ' * 6).join(labels)}")

    def go_next(self):
        """Avanza al siguiente paso."""
        # Validar paso actual
        current_widget = self.stacked_widget.currentWidget()

        if not current_widget.is_valid():
            QMessageBox.warning(
                self,
                "Validación",
                current_widget.get_validation_message()
            )
            return

        # Pasar datos al siguiente paso
        try:
            self.pass_data_to_next_step()
        except Exception as e:
            logger.error(f"Error passing data to next step: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al procesar datos:\n{str(e)}"
            )
            return

        # Avanzar
        self.current_step += 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation()

    def go_previous(self):
        """Retrocede al paso anterior."""
        self.current_step -= 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation()

    def pass_data_to_next_step(self):
        """Pasa datos del paso actual al siguiente."""
        # Paso 0 → 1: config → PromptStep
        if self.current_step == 0:
            self.prompt_config = self.step1.get_config()
            self.step2.set_config(self.prompt_config)
            logger.info(f"Config passed to step 2: {self.prompt_config.table_name}")

        # Paso 1 → 2: prompt generado (ya está en step2)
        elif self.current_step == 1:
            self.generated_prompt = self.step2.get_prompt()
            logger.info("Prompt generated and ready")

        # Paso 2 → 3: JSON → parse → PreviewStep
        elif self.current_step == 2:
            self.json_text = self.step3.get_json_text()
            self.ai_table = self.step3.get_parsed_data()
            self.step4.set_table_data(self.ai_table)
            logger.info(
                f"Table data parsed: {self.ai_table.rows_count}x{self.ai_table.cols_count}"
            )

        # Paso 3 → 4: tabla editada → CreationStep
        elif self.current_step == 3:
            self.ai_table = self.step4.get_final_table_data()
            self.step5.set_table_data(self.ai_table)
            logger.info("Final table data ready for creation")

    def update_navigation(self):
        """Actualiza el estado de los botones de navegación."""
        # Actualizar título
        titles = [
            "Paso 1: Configuración de Prompt",
            "Paso 2: Generación de Prompt",
            "Paso 3: Importación de JSON",
            "Paso 4: Previsualización de Tabla",
            "Paso 5: Creación de Tabla"
        ]
        self.title_label.setText(titles[self.current_step])

        # Actualizar progreso
        self.progress_label.setText(f"{self.current_step + 1} / {self.total_steps}")

        # Actualizar stepper
        self.update_stepper()

        # Actualizar botones
        self.prev_button.setEnabled(self.current_step > 0)

        if self.current_step == self.total_steps - 1:
            # Último paso
            self.next_button.setVisible(False)
            self.finish_button.setVisible(True)
        else:
            self.next_button.setVisible(True)
            self.finish_button.setVisible(False)

    def finish(self):
        """Finaliza el wizard y crea la tabla."""
        # Step 5 maneja la creación internamente
        # Solo emitir señal cuando termine
        self.step5.creation_finished.connect(self.on_creation_finished)
        self.step5.start_creation()

    def on_creation_finished(self, success: bool, items_created: int):
        """
        Callback cuando la creación termina.

        Args:
            success: Si fue exitosa
            items_created: Número de items creados
        """
        if success:
            # Emitir señal
            self.table_created.emit(self.ai_table.table_config.table_name, items_created)

            # Cerrar wizard después de un delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self.accept)
        else:
            logger.error("Table creation failed")

    def on_controller_error(self, error_message: str):
        """Maneja errores del controlador."""
        logger.error(f"AI Table Manager error: {error_message}")


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)

    # Crear DB de prueba
    db_path = Path(__file__).parent.parent.parent.parent / "widget_sidebar.db"
    db = DBManager(str(db_path))

    wizard = AITableCreatorWizard(db)
    wizard.exec()

    db.close()
