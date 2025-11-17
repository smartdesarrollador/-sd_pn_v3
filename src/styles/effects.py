"""
Effects - Sistema de efectos visuales especiales futuristas
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QRadialGradient, QPainterPath
import random
import math
from typing import List, Tuple


class Particle:
    """Clase para representar una partícula flotante"""

    def __init__(self, x: float, y: float, size: float, speed: float, color: QColor):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color
        self.opacity = random.uniform(0.3, 0.8)
        self.direction = random.uniform(0, 360)  # Dirección en grados
        self.lifetime = random.randint(100, 300)  # Frames de vida
        self.age = 0

    def update(self, width: int, height: int):
        """Actualizar posición de la partícula"""
        # Mover partícula
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed

        # Wrapping en los bordes
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0

        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0

        # Incrementar edad
        self.age += 1

        # Ajustar opacidad según edad
        if self.age > self.lifetime * 0.8:
            fade_factor = 1 - ((self.age - self.lifetime * 0.8) / (self.lifetime * 0.2))
            self.opacity = min(0.8, self.opacity * fade_factor)

    def is_dead(self) -> bool:
        """Verificar si la partícula debe ser eliminada"""
        return self.age >= self.lifetime


class ParticleEffect(QWidget):
    """Widget con efecto de partículas flotantes"""

    def __init__(self, parent=None, particle_count: int = 50):
        super().__init__(parent)
        self.particles: List[Particle] = []
        self.particle_count = particle_count
        self.particle_colors = [
            QColor(0, 217, 255, 100),  # Cyan
            QColor(189, 0, 255, 100),  # Púrpura
            QColor(255, 0, 110, 100),  # Rosa magenta
        ]

        # Hacer el widget transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Inicializar partículas
        self._init_particles()

        # Timer para animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(33)  # ~30 FPS

    def _init_particles(self):
        """Inicializar partículas"""
        for _ in range(self.particle_count):
            x = random.uniform(0, self.width())
            y = random.uniform(0, self.height())
            size = random.uniform(1, 3)
            speed = random.uniform(0.2, 0.8)
            color = random.choice(self.particle_colors)
            self.particles.append(Particle(x, y, size, speed, color))

    def update_particles(self):
        """Actualizar y redibujar partículas"""
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle.update(self.width(), self.height())
            if particle.is_dead():
                self.particles.remove(particle)

        # Agregar nuevas partículas si hay menos del límite
        while len(self.particles) < self.particle_count:
            x = random.uniform(0, self.width())
            y = random.uniform(0, self.height())
            size = random.uniform(1, 3)
            speed = random.uniform(0.2, 0.8)
            color = random.choice(self.particle_colors)
            self.particles.append(Particle(x, y, size, speed, color))

        self.update()

    def paintEvent(self, event):
        """Dibujar partículas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for particle in self.particles:
            # Configurar color con opacidad
            color = QColor(particle.color)
            color.setAlphaF(particle.opacity)

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)

            # Dibujar partícula
            painter.drawEllipse(
                QPointF(particle.x, particle.y),
                particle.size,
                particle.size
            )


class ScanLineEffect(QWidget):
    """Widget con efecto de líneas de escaneo"""

    def __init__(self, parent=None, line_spacing: int = 4, speed: float = 2.0):
        super().__init__(parent)
        self.line_spacing = line_spacing
        self.speed = speed
        self.offset = 0

        # Hacer el widget semi-transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Timer para animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(33)  # ~30 FPS

    def animate(self):
        """Animar líneas de escaneo"""
        self.offset += self.speed
        if self.offset >= self.line_spacing * 2:
            self.offset = 0
        self.update()

    def paintEvent(self, event):
        """Dibujar líneas de escaneo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Color de las líneas
        line_color = QColor(0, 217, 255, 10)  # Cyan muy sutil
        painter.setPen(QPen(line_color, 1))

        # Dibujar líneas horizontales
        y = -self.line_spacing + self.offset
        while y < self.height():
            painter.drawLine(0, int(y), self.width(), int(y))
            y += self.line_spacing * 2


class AuroraEffect(QWidget):
    """Widget con efecto aurora animado"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.colors = [
            (0, 217, 255),    # Cyan
            (189, 0, 255),    # Púrpura
            (255, 0, 110),    # Rosa magenta
        ]

        # Hacer el widget transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Timer para animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # ~20 FPS

    def animate(self):
        """Animar efecto aurora"""
        self.phase += 0.02
        if self.phase >= 2 * math.pi:
            self.phase = 0
        self.update()

    def paintEvent(self, event):
        """Dibujar efecto aurora"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Crear gradiente radial animado
        center_x = self.width() / 2
        center_y = self.height() / 2

        # Calcular posición del foco basada en la fase
        offset_x = math.cos(self.phase) * 100
        offset_y = math.sin(self.phase * 1.5) * 100

        gradient = QRadialGradient(
            center_x + offset_x,
            center_y + offset_y,
            max(self.width(), self.height())
        )

        # Colores del gradiente con transparencia
        color1 = QColor(*self.colors[0], 30)
        color2 = QColor(*self.colors[1], 20)
        color3 = QColor(*self.colors[2], 10)

        gradient.setColorAt(0, color1)
        gradient.setColorAt(0.5, color2)
        gradient.setColorAt(1, color3)

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())


class HolographicShimmer(QWidget):
    """Widget con efecto shimmer holográfico"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shimmer_position = 0
        self.shimmer_width = 100

        # Hacer el widget transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Timer para animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)  # ~25 FPS

    def animate(self):
        """Animar shimmer"""
        self.shimmer_position += 5
        if self.shimmer_position > self.width() + self.shimmer_width:
            self.shimmer_position = -self.shimmer_width
        self.update()

    def paintEvent(self, event):
        """Dibujar efecto shimmer"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Crear gradiente lineal para el shimmer
        gradient = QLinearGradient(
            self.shimmer_position - self.shimmer_width / 2,
            0,
            self.shimmer_position + self.shimmer_width / 2,
            0
        )

        # Colores del shimmer
        transparent = QColor(255, 255, 255, 0)
        shimmer_color = QColor(255, 255, 255, 40)

        gradient.setColorAt(0, transparent)
        gradient.setColorAt(0.5, shimmer_color)
        gradient.setColorAt(1, transparent)

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())


class GlitchEffect(QWidget):
    """Widget con efecto glitch ocasional"""

    glitch_triggered = pyqtSignal()

    def __init__(self, parent=None, glitch_probability: float = 0.01):
        super().__init__(parent)
        self.glitch_probability = glitch_probability
        self.is_glitching = False
        self.glitch_offset = 0
        self.glitch_duration = 0

        # Hacer el widget transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Timer para chequear glitch
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_glitch)
        self.timer.start(100)  # Chequear cada 100ms

    def check_glitch(self):
        """Verificar si debe ocurrir un glitch"""
        if not self.is_glitching:
            if random.random() < self.glitch_probability:
                self.trigger_glitch()
        else:
            self.glitch_duration -= 1
            if self.glitch_duration <= 0:
                self.is_glitching = False
                self.update()

    def trigger_glitch(self):
        """Activar efecto glitch"""
        self.is_glitching = True
        self.glitch_offset = random.randint(-5, 5)
        self.glitch_duration = random.randint(1, 3)
        self.glitch_triggered.emit()
        self.update()

    def paintEvent(self, event):
        """Dibujar efecto glitch"""
        if not self.is_glitching:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dibujar líneas de color desplazadas (efecto RGB split)
        colors = [
            QColor(255, 0, 0, 50),    # Rojo
            QColor(0, 255, 0, 50),    # Verde
            QColor(0, 0, 255, 50),    # Azul
        ]

        for i, color in enumerate(colors):
            offset = self.glitch_offset * (i - 1)
            painter.setPen(QPen(color, 2))

            # Dibujar líneas horizontales aleatorias
            for _ in range(3):
                y = random.randint(0, self.height())
                painter.drawLine(
                    offset,
                    y,
                    self.width() + offset,
                    y
                )


class NeonGlow:
    """Utilidad para crear efectos de brillo neón"""

    @staticmethod
    def create_glow_gradient(color: QColor, intensity: float = 1.0) -> QRadialGradient:
        """Crear gradiente con efecto glow"""
        gradient = QRadialGradient(0.5, 0.5, 0.5)

        # Color central brillante
        center_color = QColor(color)
        center_color.setAlphaF(min(255, color.alpha() * intensity) / 255)

        # Color exterior desvanecido
        outer_color = QColor(color)
        outer_color.setAlphaF(0)

        gradient.setColorAt(0, center_color)
        gradient.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), int(color.alpha() * 0.5 * intensity)))
        gradient.setColorAt(1, outer_color)

        return gradient

    @staticmethod
    def apply_glow_to_widget(widget: QWidget, color: QColor, blur_radius: int = 20):
        """Aplicar efecto glow a un widget (requiere QGraphicsDropShadowEffect)"""
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)


# Función helper para aplicar múltiples efectos a un widget
def apply_effects(widget: QWidget, effects: List[str] = None):
    """
    Aplicar efectos visuales a un widget

    Efectos disponibles:
    - 'particles': Partículas flotantes
    - 'scanlines': Líneas de escaneo
    - 'aurora': Efecto aurora
    - 'shimmer': Shimmer holográfico
    - 'glitch': Efecto glitch ocasional
    """
    if effects is None:
        effects = []

    applied_effects = []

    if 'particles' in effects:
        particle_effect = ParticleEffect(widget, particle_count=30)
        particle_effect.setGeometry(widget.rect())
        particle_effect.lower()  # Enviar al fondo
        applied_effects.append(particle_effect)

    if 'scanlines' in effects:
        scanline_effect = ScanLineEffect(widget)
        scanline_effect.setGeometry(widget.rect())
        scanline_effect.lower()
        applied_effects.append(scanline_effect)

    if 'aurora' in effects:
        aurora_effect = AuroraEffect(widget)
        aurora_effect.setGeometry(widget.rect())
        aurora_effect.lower()
        applied_effects.append(aurora_effect)

    if 'shimmer' in effects:
        shimmer_effect = HolographicShimmer(widget)
        shimmer_effect.setGeometry(widget.rect())
        shimmer_effect.raise_()  # Traer al frente
        applied_effects.append(shimmer_effect)

    if 'glitch' in effects:
        glitch_effect = GlitchEffect(widget)
        glitch_effect.setGeometry(widget.rect())
        glitch_effect.raise_()
        applied_effects.append(glitch_effect)

    return applied_effects
