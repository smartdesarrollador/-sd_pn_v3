"""
AI Bulk Item Creation Wizard - Wizard para creación masiva de items con IA

Este wizard guía al usuario a través de 5 pasos:
1. Configuración: Seleccionar categoría, tags, opciones
2. Generar Prompt: Obtener prompt personalizado para IA
3. Importar JSON: Pegar JSON generado por IA
4. Previsualizar: Revisar y editar items antes de crear
5. Crear Items: Inserción masiva en BD
"""
import sys
from pathlib import Path
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QMessageBox, QWidget, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Agregar path al sys.path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ai_bulk_manager import AIBulkItemManager
from database.db_manager import DBManager
from views.widgets.ai_config_step import ConfigStep
from views.widgets.ai_prompt_step import PromptStep
from views.widgets.ai_json_step import JSONStep
from views.widgets.ai_preview_step import PreviewStep
from views.widgets.ai_creation_step import CreationStep

logger = logging.getLogger(__name__)


class PlaceholderStep(QWidget):
    """
    Placeholder temporal para steps que se implementarán en Fase 3.
    """
    def __init__(self, step_name: str, step_number: int, parent=None):
        super().__init__(parent)
        self.step_name = step_name
        self.step_number = step_number
        self.init_ui()

    def init_ui(self):
        """Inicializa UI placeholder."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mensaje placeholder
        label = QLabel(f"🚧 Paso {self.step_number}: {self.step_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: #00d4ff; padding: 40px;")
        layout.addWidget(label)

        info_label = QLabel("Este paso se implementará en la Fase 3")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888888; font-size: 12pt;")
        layout.addWidget(info_label)

    def is_valid(self) -> bool:
        """Valida que el step se puede avanzar."""
        # Por ahora siempre válido (placeholder)
        return True


class AIBulkWizard(QDialog):
    """
    Wizard para creación masiva de items con IA.

    Señales:
        items_created(int): Emitida cuando se crean items (con count)
    """

    items_created = pyqtSignal(int)  # Señal con count de items creados

    def __init__(self, db_manager: DBManager, parent=None):
        """
        Inicializa el wizard.

        Args:
            db_manager: Instancia de DBManager para acceso a BD
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = db_manager
        self.manager = AIBulkItemManager(db_manager)

        self.current_step = 0
        self.total_steps = 5

        # Data compartida entre steps
        self.config_data = None
        self.prompt_text = None
        self.json_data = None
        self.parsed_items = None
        self.selected_items = None

        self.init_ui()
        self.load_last_config()

        logger.info("AIBulkWizard initialized")

    def init_ui(self):
        """Inicializa la interfaz del wizard."""
        self.setWindowTitle("Creación Masiva de Items con IA")
        self.setMinimumSize(900, 650)
        self.setModal(True)

        # Aplicar tema oscuro
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00d4ff;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
                border-color: #3d3d3d;
            }
            QPushButton#primaryButton {
                background-color: #00d4ff;
                color: #000000;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background-color: #00b8e6;
            }
            QPushButton#primaryButton:pressed {
                background-color: #0099cc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header con indicador de paso
        self.header = self._create_header()
        layout.addWidget(self.header)

        # Stacked widget para pasos
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #252525;
                border: none;
            }
        """)
        layout.addWidget(self.stacked_widget)

        # Inicializar steps (placeholders por ahora)
        self._init_steps()

        # Navigation bar
        nav_bar_widget = self._create_navigation_bar()
        layout.addWidget(nav_bar_widget)

    def _create_header(self) -> QWidget:
        """
        Crea header con título y paso actual.

        Returns:
            QWidget con el header
        """
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 2px solid #00d4ff;
            }
        """)
        header_widget.setFixedHeight(80)

        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(5)

        # Título principal
        title = QLabel("🤖 Creación Masiva de Items con IA")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00d4ff; border: none;")
        header_layout.addWidget(title)

        # Indicador de paso
        self.step_indicator = QLabel()
        step_font = QFont()
        step_font.setPointSize(11)
        self.step_indicator.setFont(step_font)
        self.step_indicator.setStyleSheet("color: #888888; border: none;")
        header_layout.addWidget(self.step_indicator)

        self.update_header_text()

        return header_widget

    def update_header_text(self):
        """Actualiza texto del indicador de paso."""
        step_names = [
            "Configuración",
            "Generar Prompt",
            "Importar JSON",
            "Previsualizar Items",
            "Crear Items"
        ]

        if self.current_step < len(step_names):
            text = f"Paso {self.current_step + 1} de {self.total_steps}: {step_names[self.current_step]}"
            self.step_indicator.setText(text)

    def _init_steps(self):
        """Inicializa todos los steps del wizard."""
        # Step 1: Configuración
        self.config_step = ConfigStep(self.db)
        self.stacked_widget.addWidget(self.config_step)

        # Step 2: Generación de Prompt
        self.prompt_step = PromptStep(self.manager)
        self.stacked_widget.addWidget(self.prompt_step)

        # Step 3: Importación JSON
        self.json_step = JSONStep(self.manager)
        self.stacked_widget.addWidget(self.json_step)

        # Step 4: Previsualización
        self.preview_step = PreviewStep()
        self.stacked_widget.addWidget(self.preview_step)

        # Step 5: Creación
        self.creation_step = CreationStep(self.manager)
        self.stacked_widget.addWidget(self.creation_step)

        logger.debug(f"Initialized 5 real steps")

    def _create_navigation_bar(self) -> QWidget:
        """
        Crea barra de navegación con botones.

        Returns:
            QWidget con la navigation bar
        """
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top: 1px solid #3d3d3d;
            }
        """)
        nav_widget.setFixedHeight(70)

        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 15, 20, 15)
        nav_layout.setSpacing(10)

        # Botón cancelar (izquierda)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_cancel.setFixedWidth(100)
        nav_layout.addWidget(self.btn_cancel)

        nav_layout.addStretch()

        # Botón anterior (centro-derecha)
        self.btn_previous = QPushButton("← Anterior")
        self.btn_previous.clicked.connect(self.go_previous)
        self.btn_previous.setEnabled(False)
        self.btn_previous.setFixedWidth(120)
        nav_layout.addWidget(self.btn_previous)

        # Botón siguiente (derecha)
        self.btn_next = QPushButton("Siguiente →")
        self.btn_next.clicked.connect(self.go_next)
        self.btn_next.setObjectName("primaryButton")
        self.btn_next.setFixedWidth(120)
        nav_layout.addWidget(self.btn_next)

        # Botón crear (oculto inicialmente, se muestra en último paso)
        self.btn_create = QPushButton("✓ Crear Items")
        self.btn_create.clicked.connect(self.create_items)
        self.btn_create.setObjectName("primaryButton")
        self.btn_create.setVisible(False)
        self.btn_create.setFixedWidth(140)
        nav_layout.addWidget(self.btn_create)

        return nav_widget

    def go_next(self):
        """Avanza al siguiente paso."""
        # Validar paso actual antes de avanzar
        if not self.validate_current_step():
            return

        # Pasar datos entre steps antes de avanzar
        self.pass_data_to_next_step()

        # Avanzar
        self.current_step += 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation_buttons()
        self.update_header_text()

        logger.debug(f"Advanced to step {self.current_step + 1}")

    def go_previous(self):
        """Retrocede al paso anterior."""
        self.current_step -= 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_navigation_buttons()
        self.update_header_text()

        logger.debug(f"Went back to step {self.current_step + 1}")

    def update_navigation_buttons(self):
        """Actualiza estado de botones de navegación."""
        # Botón anterior: habilitado si no estamos en el primer paso
        self.btn_previous.setEnabled(self.current_step > 0)

        # Botones siguiente/crear según paso actual
        is_last_step = self.current_step == self.total_steps - 1

        if is_last_step:
            self.btn_next.setVisible(False)
            self.btn_create.setVisible(True)
        else:
            self.btn_next.setVisible(True)
            self.btn_create.setVisible(False)

    def validate_current_step(self) -> bool:
        """
        Valida que el paso actual se puede avanzar.

        Returns:
            True si se puede avanzar, False si no
        """
        current_widget = self.stacked_widget.currentWidget()

        # Si el widget tiene método is_valid, usarlo
        if hasattr(current_widget, 'is_valid'):
            is_valid = current_widget.is_valid()

            if not is_valid:
                QMessageBox.warning(
                    self,
                    "Validación",
                    "Por favor completa los campos requeridos antes de continuar."
                )
                logger.warning(f"Step {self.current_step + 1} validation failed")
                return False

        return True

    def pass_data_to_next_step(self):
        """Pasa datos entre steps."""
        try:
            # Paso 0 → 1: pasar config a PromptStep
            if self.current_step == 0:
                config = self.config_step.get_config()
                self.prompt_step.set_config(config)
                logger.debug("Config passed to PromptStep")

            # Paso 2 → 3: pasar parsed items a PreviewStep
            elif self.current_step == 2:
                json_text = self.json_step.get_json_text()
                items, defaults, category_id = self.manager.parse_items(json_text)
                self.preview_step.set_items(items)
                # Guardar para paso 4
                self.parsed_items = items
                self.selected_category_id = category_id
                logger.debug(f"Parsed {len(items)} items for PreviewStep")

            # Paso 3 → 4: pasar selected items a CreationStep
            elif self.current_step == 3:
                selected_items = self.preview_step.get_selected_items()
                self.creation_step.set_items(selected_items, self.selected_category_id)
                logger.debug(f"{len(selected_items)} items ready for CreationStep")

        except Exception as e:
            logger.error(f"Error passing data between steps: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al procesar datos:\n{str(e)}"
            )

    def on_cancel(self):
        """Maneja cancelación del wizard."""
        # Si hay trabajo en progreso, confirmar
        if self.current_step > 0:
            reply = QMessageBox.question(
                self,
                "Cancelar",
                "¿Seguro que deseas cancelar? Se perderá el progreso actual.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        logger.info("Wizard cancelled by user")
        self.reject()

    def create_items(self):
        """Crea items en BD."""
        try:
            # Ejecutar creación en CreationStep
            self.creation_step.create_items()

            # Obtener resultado
            result = self.creation_step.get_result()

            if result and result.success:
                # Emitir señal con count
                self.items_created.emit(result.created_count)

                # Cerrar wizard después de 2 segundos
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(2000, self.accept)

                logger.info(f"Wizard completed: {result.created_count} items created")
            else:
                logger.error(f"Creation failed: {result.errors if result else 'No result'}")

        except Exception as e:
            logger.error(f"Error in create_items: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al crear items:\n{str(e)}"
            )

    def load_last_config(self):
        """
        Carga última configuración usada.

        Se implementará en Fase 5 cuando se agregue persistencia.
        """
        # Placeholder para persistencia de config
        pass

    def save_config(self):
        """
        Guarda configuración actual.

        Se implementará en Fase 5.
        """
        # Placeholder para persistencia de config
        pass

    def showEvent(self, event):
        """Override para centrar el dialog al mostrarse."""
        super().showEvent(event)

        # Centrar en la pantalla disponible
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.center().x() - self.width() // 2
            y = screen_geometry.center().y() - self.height() // 2
            self.move(x, y)
            logger.debug(f"Wizard centered at ({x}, {y}) on screen {screen_geometry}")

        logger.debug("Wizard shown")

    def closeEvent(self, event):
        """Override para manejar cierre del dialog."""
        # Llamar a on_cancel para confirmar si es necesario
        if self.current_step > 0:
            event.ignore()
            self.on_cancel()
        else:
            event.accept()
            logger.debug("Wizard closed")
