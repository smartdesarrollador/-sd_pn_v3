"""
JSON Editor Widget - Editor de texto con syntax highlighting para JSON

Proporciona un QTextEdit con colores syntax highlighting básico para JSON.
"""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QFont, QColor
)
from PyQt6.QtCore import Qt, QRegularExpression
import logging

logger = logging.getLogger(__name__)


class JSONHighlighter(QSyntaxHighlighter):
    """Syntax highlighter para JSON."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Formato para keys (strings con ":")
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#00d4ff"))  # Cyan
        key_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"]*"\s*:'),
            key_format
        ))

        # Formato para strings (valores)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#00ff88"))  # Verde
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"]*"'),
            string_format
        ))

        # Formato para números
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FFD700"))  # Dorado
        self.highlighting_rules.append((
            QRegularExpression(r'\b\d+\.?\d*\b'),
            number_format
        ))

        # Formato para booleans y null
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF8C00"))  # Naranja
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ['true', 'false', 'null']
        for keyword in keywords:
            self.highlighting_rules.append((
                QRegularExpression(f'\\b{keyword}\\b'),
                keyword_format
            ))

        # Formato para llaves y corchetes
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor("#ffffff"))  # Blanco
        brace_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression(r'[\{\}\[\]]'),
            brace_format
        ))

    def highlightBlock(self, text):
        """Aplica highlighting a un bloque de texto."""
        for pattern, format_obj in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    format_obj
                )


class JSONEditor(QTextEdit):
    """
    Editor de texto especializado para JSON con syntax highlighting.

    Características:
    - Syntax highlighting para JSON
    - Fuente monospace
    - Tema oscuro
    - Tab = 2 espacios
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configurar fuente monospace
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Aplicar estilo
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                selection-background-color: #264f78;
            }
        """)

        # Aplicar syntax highlighter
        self.highlighter = JSONHighlighter(self.document())

        # Tab width = 2 espacios
        self.setTabStopDistance(20)  # ~2 caracteres

        logger.debug("JSONEditor initialized with syntax highlighting")

    def setPlainText(self, text: str):
        """Override para mantener highlighting al set text."""
        super().setPlainText(text)
        # El highlighter se actualiza automáticamente

    def keyPressEvent(self, event):
        """Override para manejar Tab como espacios."""
        if event.key() == Qt.Key.Key_Tab:
            # Insertar 2 espacios en lugar de tab
            self.insertPlainText("  ")
        else:
            super().keyPressEvent(event)
