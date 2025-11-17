"""
Table Creator Wizard - Wizard para creación masiva de items en formato tabla

Este wizard guía al usuario a través de 2 pasos:
1. Configuración: Nombre, dimensiones, columnas, categoría, tags
2. Edición de Datos: Tabla editable para ingreso rápido de datos
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
from views.widgets.table_config_step import TableConfigStep
from views.widgets.table_editor_step import TableEditorStep
from controllers.table_controller import TableController

logger = logging.getLogger(__name__)


class TableCreatorWizard(QDialog):
    """
    Wizard para creación de items en formato tabla.

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

        # Inicializar TableController
        self.table_controller = TableController(db_manager)
        self.table_controller.error_occurred.connect(self.on_controller_error)

        self.current_step = 0
        self.total_steps = 2

        # Data compartida entre steps
        self.config_data = None  # Configuración de tabla
        self.table_data = None   # Datos de tabla

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del wizard."""
        self.setWindowTitle("Crear Tabla de Items")
        self.setFixedSize(900, 700)
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

        self.title_label = QLabel("Paso 1: Configuración de Tabla")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.progress_label = QLabel("1 / 2")
        self.progress_label.setStyleSheet("color: #888888; font-size: 11pt;")
        header_layout.addWidget(self.progress_label)

        main_layout.addLayout(header_layout)

        # Separador
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3d3d3d;")
        main_layout.addWidget(separator)

        # Stacked widget para los pasos
        self.stacked_widget = QStackedWidget()

        # Crear steps
        self.step1 = TableConfigStep(self.db, self.controller, self)
        self.step2 = TableEditorStep(self)

        self.stacked_widget.addWidget(self.step1)
        self.stacked_widget.addWidget(self.step2)

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

    def go_next(self):
        """Avanza al siguiente paso."""
        # Validar paso actual
        current_widget = self.stacked_widget.currentWidget()

        if not current_widget.is_valid():
            QMessageBox.warning(
                self,
                "Validación",
                "Por favor completa todos los campos requeridos antes de continuar."
            )
            return

        # Guardar datos del paso actual
        if self.current_step == 0:
            # Obtener configuración del paso 1
            self.config_data = self.step1.get_config()

            # Configurar paso 2 con los datos
            self.step2.setup_table(
                rows=self.config_data['rows'],
                cols=self.config_data['cols'],
                column_names=self.config_data['column_names']
            )

            logger.info(f"Table config: {self.config_data}")

        # Avanzar
        self.current_step += 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation()

    def go_previous(self):
        """Retrocede al paso anterior."""
        self.current_step -= 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation()

    def update_navigation(self):
        """Actualiza el estado de los botones de navegación."""
        # Actualizar título
        titles = [
            "Paso 1: Configuración de Tabla",
            "Paso 2: Ingreso de Datos"
        ]
        self.title_label.setText(titles[self.current_step])

        # Actualizar progreso
        self.progress_label.setText(f"{self.current_step + 1} / {self.total_steps}")

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
        # Validar paso final
        if not self.step2.is_valid():
            QMessageBox.warning(
                self,
                "Validación",
                "Por favor ingresa al menos algunos datos en la tabla antes de crear."
            )
            return

        # Obtener datos de tabla
        self.table_data = self.step2.get_table_data()

        # Validar que haya datos
        filled_cells = sum(1 for row in self.table_data for cell in row if cell and str(cell).strip())

        if filled_cells == 0:
            QMessageBox.warning(
                self,
                "Validación",
                "La tabla está vacía. Ingresa al menos algunos datos antes de crear."
            )
            return

        # Confirmar creación
        response = QMessageBox.question(
            self,
            "Confirmar Creación",
            f"¿Deseas crear la tabla '{self.config_data['table_name']}'?\n\n"
            f"Dimensiones: {self.config_data['rows']} filas × {self.config_data['cols']} columnas\n"
            f"Celdas con datos: {filled_cells}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        # Crear tabla usando el controlador
        try:
            logger.info(f"Creating table: {self.config_data['table_name']}")

            # Usar TableController en lugar de llamar directamente a DB
            result = self.table_controller.create_table(
                category_id=self.config_data['category_id'],
                table_name=self.config_data['table_name'],
                table_data=self.table_data,
                column_names=self.config_data['column_names'],
                tags=self.config_data.get('tags', []),
                sensitive_columns=self.config_data.get('sensitive_columns', []),
                url_columns=self.config_data.get('url_columns', [])
            )

            if result['success']:
                items_created = result['items_created']

                QMessageBox.information(
                    self,
                    "Tabla Creada",
                    f"Tabla '{self.config_data['table_name']}' creada exitosamente!\n\n"
                    f"Items creados: {items_created}\n"
                    f"Celdas con datos: {filled_cells}"
                )

                # Emitir señal
                self.table_created.emit(self.config_data['table_name'], items_created)

                # Cerrar wizard
                self.accept()

            else:
                error_msg = '\n'.join(result['errors'][:5])  # Mostrar primeros 5 errores
                QMessageBox.critical(
                    self,
                    "Error al Crear Tabla",
                    f"No se pudo crear la tabla:\n\n{error_msg}"
                )

        except Exception as e:
            logger.error(f"Error creating table: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al crear tabla:\n{str(e)}"
            )

    def on_controller_error(self, error_message: str):
        """Maneja errores del controlador."""
        logger.error(f"TableController error: {error_message}")
        # Los errores ya se manejan en el método finish(), pero esto podría ser útil para debugging


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)

    # Crear DB de prueba
    db_path = Path(__file__).parent.parent.parent.parent / "widget_sidebar.db"
    db = DBManager(str(db_path))

    wizard = TableCreatorWizard(db)
    wizard.exec()

    db.close()
