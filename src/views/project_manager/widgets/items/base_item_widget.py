"""
Widget base para items de vista completa

Clase abstracta que proporciona funcionalidad común para todos
los tipos de items (TEXT, CODE, URL, PATH).

Autor: Widget Sidebar Team
Versión: 1.0
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from abc import abstractmethod
from ..common.copy_button import CopyButton
import pyperclip
import re


class BaseItemWidget(QFrame):
    """
    Clase base abstracta para todos los widgets de items

    Proporciona:
    - Layout base con área de contenido y botón de copiar
    - Funcionalidad de copiado al portapapeles
    - Métodos helper para obtener datos del item
    - Método abstracto render_content() que debe ser implementado

    Señales:
        item_copied: Emitida cuando se copia el item al portapapeles
    """

    # Señales
    item_copied = pyqtSignal(dict)

    def __init__(self, item_data: dict, parent=None):
        """
        Inicializar widget base de item

        Args:
            item_data: Diccionario con datos del item
            parent: Widget padre
        """
        super().__init__(parent)

        self.item_data = item_data
        self.copy_button = None

        self.init_base_ui()
        self.render_content()  # Método abstracto - implementado por subclases

    def init_base_ui(self):
        """Inicializar UI base común a todos los items"""
        # Establecer ancho fijo para el contenedor del item
        self.setFixedWidth(800)  # ANCHO FIJO: 800px

        # Layout principal (horizontal)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        # Layout de contenido (vertical, izquierda)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(6)
        self.main_layout.addLayout(self.content_layout, 1)  # stretch=1 para ocupar espacio disponible

        # Botón de copiar (derecha, sin stretch)
        self.copy_button = CopyButton()
        self.copy_button.copy_clicked.connect(self.copy_to_clipboard)
        self.copy_button.setFixedSize(32, 32)  # Tamaño fijo para el botón
        self.main_layout.addWidget(
            self.copy_button,
            0,  # stretch=0 para mantener tamaño fijo
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        # Cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @abstractmethod
    def render_content(self):
        """
        Renderizar contenido específico del tipo de item

        Este método debe ser implementado por cada subclase
        para mostrar el contenido según el tipo de item.
        """
        pass

    def copy_to_clipboard(self):
        """
        Copiar contenido del item al portapapeles

        Copia el campo 'content' del item_data y emite
        la señal item_copied.
        """
        # Si el item es sensible, verificar contraseña maestra
        if self.item_data.get('is_sensitive', False):
            from views.dialogs.master_password_dialog import MasterPasswordDialog

            item_label = self.item_data.get('label', 'item sensible')
            verified = MasterPasswordDialog.verify(
                title="Item Sensible",
                message=f"Ingresa tu contraseña maestra para copiar:\n'{item_label}'",
                parent=self.window()
            )

            if not verified:
                print(f"Master password verification cancelled for copying item: {item_label}")
                return  # Usuario canceló o contraseña incorrecta

        content = self.item_data.get('content', '')
        if content:
            try:
                pyperclip.copy(content)
                self.item_copied.emit(self.item_data)
            except Exception as e:
                print(f"Error al copiar al portapapeles: {e}")

    def get_item_label(self) -> str:
        """
        Obtener etiqueta/título del item

        Returns:
            Etiqueta del item o 'Sin título' si no existe
        """
        return self.item_data.get('label', 'Sin título')

    def get_item_content(self) -> str:
        """
        Obtener contenido del item

        Si el item es sensible (is_sensitive=True), retorna
        el contenido enmascarado para proteger la información.

        Returns:
            Contenido del item o string vacío si no existe.
            Si es sensible, retorna contenido enmascarado.
        """
        content = self.item_data.get('content', '')
        is_sensitive = self.item_data.get('is_sensitive', False)

        # Si el item es sensible, enmascarar el contenido
        if is_sensitive and content:
            # Calcular longitud aproximada para el enmascaramiento
            # Usar puntos circulares (bullets) para enmascarar
            mask_length = min(len(content), 20)  # Máximo 20 bullets
            return '•' * mask_length + (' ...' if len(content) > 20 else '')

        return content

    def get_item_description(self) -> str:
        """
        Obtener descripción del item

        Returns:
            Descripción del item o string vacío si no existe
        """
        return self.item_data.get('description', '')

    def get_item_type(self) -> str:
        """
        Obtener tipo del item

        Returns:
            Tipo del item (TEXT, CODE, URL, PATH)
        """
        return self.item_data.get('type', 'TEXT')

    def get_item_id(self) -> int:
        """
        Obtener ID del item

        Returns:
            ID del item o None si no existe
        """
        return self.item_data.get('id')

    def is_content_long(self, max_length: int = 800) -> bool:
        """
        Verificar si el contenido es extenso

        Args:
            max_length: Longitud máxima antes de considerar extenso

        Returns:
            True si el contenido excede max_length caracteres
        """
        content = self.get_item_content()
        return len(content) > max_length

    def has_match(self, search_text: str) -> bool:
        """
        Verificar si el item coincide con el texto de búsqueda

        Busca en: label, content (sin enmascarar), y description

        Args:
            search_text: Texto a buscar (case-insensitive)

        Returns:
            True si hay coincidencia en algún campo
        """
        if not search_text:
            return False

        search_lower = search_text.lower()

        # Buscar en label
        label = self.get_item_label()
        if label and search_lower in label.lower():
            return True

        # Buscar en content (sin enmascarar)
        content = self.item_data.get('content', '')
        if content and search_lower in content.lower():
            return True

        # Buscar en description
        description = self.get_item_description()
        if description and search_lower in description.lower():
            return True

        return False

    def highlight_text(self, search_text: str):
        """
        Resaltar texto de búsqueda en el widget

        Recorre todos los QLabel hijos y resalta el texto encontrado
        usando HTML con color de fondo amarillo.

        Args:
            search_text: Texto a resaltar (case-insensitive)
        """
        if not search_text:
            return

        # Recorrer todos los widgets hijos que sean QLabel
        for child in self.findChildren(QLabel):
            self._highlight_label(child, search_text)

    def clear_highlight(self):
        """
        Limpiar resaltado de texto en el widget

        Restaura el texto original sin HTML de resaltado.
        """
        # Recorrer todos los QLabel hijos y limpiar HTML
        for child in self.findChildren(QLabel):
            self._clear_label_highlight(child)

    def _highlight_label(self, label: QLabel, search_text: str):
        """
        Resaltar texto en un QLabel específico

        Args:
            label: QLabel a modificar
            search_text: Texto a resaltar
        """
        original_text = label.text()

        # Si el texto ya tiene HTML (indicado por tags), extraer texto plano
        if '<' in original_text and '>' in original_text:
            # Intentar extraer texto sin HTML
            import html
            plain_text = re.sub(r'<[^>]+>', '', original_text)
            plain_text = html.unescape(plain_text)
        else:
            plain_text = original_text

        # Guardar texto original en una propiedad dinámica si no existe
        if not label.property("original_text"):
            label.setProperty("original_text", plain_text)

        # Crear patrón regex case-insensitive
        pattern = re.compile(re.escape(search_text), re.IGNORECASE)

        # Función de reemplazo que preserva el caso original
        def replace_match(match):
            matched_text = match.group(0)
            return f'<span style="background-color: #FFD700; color: #000000; font-weight: bold;">{matched_text}</span>'

        # Aplicar resaltado
        highlighted_text = pattern.sub(replace_match, plain_text)

        # Si hubo cambios, aplicar HTML
        if highlighted_text != plain_text:
            # Preservar saltos de línea y espacios en HTML
            highlighted_text = highlighted_text.replace('\n', '<br>')
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setText(highlighted_text)

    def _clear_label_highlight(self, label: QLabel):
        """
        Limpiar resaltado en un QLabel específico

        Args:
            label: QLabel a limpiar
        """
        # Restaurar texto original si existe
        original_text = label.property("original_text")
        if original_text:
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setText(original_text)
            label.setProperty("original_text", None)
