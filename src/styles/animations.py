"""
Animations - Sistema de animaciones futuristas para PyQt6
"""
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QPoint, QSize, QRect, pyqtProperty
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget
from PyQt6.QtGui import QColor
from typing import Optional, Callable


class AnimationDurations:
    """Duraciones estándar para animaciones"""
    INSTANT = 0
    VERY_FAST = 100
    FAST = 200
    NORMAL = 300
    SLOW = 500
    VERY_SLOW = 800


class AnimationEasing:
    """Curvas de easing predefinidas"""
    LINEAR = QEasingCurve.Type.Linear
    IN_OUT_CUBIC = QEasingCurve.Type.InOutCubic
    IN_OUT_QUAD = QEasingCurve.Type.InOutQuad
    OUT_BOUNCE = QEasingCurve.Type.OutBounce
    IN_OUT_ELASTIC = QEasingCurve.Type.InOutElastic
    OUT_BACK = QEasingCurve.Type.OutBack
    IN_OUT_BACK = QEasingCurve.Type.InOutBack


class AnimationSystem:
    """Sistema centralizado de animaciones"""

    @staticmethod
    def fade_in(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de fade in (aparecer)"""
        # Crear efecto de opacidad si no existe
        if not widget.graphicsEffect():
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

        effect = widget.graphicsEffect()

        # Crear animación
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                 on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de fade out (desaparecer)"""
        # Crear efecto de opacidad si no existe
        if not widget.graphicsEffect():
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

        effect = widget.graphicsEffect()

        # Crear animación
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def slide_in_from_left(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                           distance: int = 100,
                           on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de deslizamiento desde la izquierda"""
        current_pos = widget.pos()
        start_pos = QPoint(current_pos.x() - distance, current_pos.y())

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(AnimationEasing.OUT_BACK)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def slide_in_from_right(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                            distance: int = 100,
                            on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de deslizamiento desde la derecha"""
        current_pos = widget.pos()
        start_pos = QPoint(current_pos.x() + distance, current_pos.y())

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(AnimationEasing.OUT_BACK)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def slide_in_from_top(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                          distance: int = 50,
                          on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de deslizamiento desde arriba"""
        current_pos = widget.pos()
        start_pos = QPoint(current_pos.x(), current_pos.y() - distance)

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(AnimationEasing.OUT_BACK)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def scale_in(widget: QWidget, duration: int = AnimationDurations.NORMAL,
                 on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación de escala (crecer desde pequeño)"""
        current_size = widget.size()
        start_size = QSize(0, 0)

        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(current_size)
        animation.setEasingCurve(AnimationEasing.OUT_BACK)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def bounce_in(widget: QWidget, duration: int = AnimationDurations.SLOW,
                  on_finished: Optional[Callable] = None) -> QPropertyAnimation:
        """Animación con efecto de rebote"""
        current_pos = widget.pos()
        start_pos = QPoint(current_pos.x(), current_pos.y() - 100)

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(AnimationEasing.OUT_BOUNCE)

        if on_finished:
            animation.finished.connect(on_finished)

        return animation

    @staticmethod
    def combined_fade_slide(widget: QWidget,
                           duration: int = AnimationDurations.NORMAL,
                           direction: str = 'left',
                           distance: int = 100,
                           on_finished: Optional[Callable] = None) -> QParallelAnimationGroup:
        """Animación combinada de fade + slide"""
        group = QParallelAnimationGroup()

        # Fade in
        fade = AnimationSystem.fade_in(widget, duration)

        # Slide
        if direction == 'left':
            slide = AnimationSystem.slide_in_from_left(widget, duration, distance)
        elif direction == 'right':
            slide = AnimationSystem.slide_in_from_right(widget, duration, distance)
        elif direction == 'top':
            slide = AnimationSystem.slide_in_from_top(widget, duration, distance)
        else:
            slide = AnimationSystem.slide_in_from_left(widget, duration, distance)

        group.addAnimation(fade)
        group.addAnimation(slide)

        if on_finished:
            group.finished.connect(on_finished)

        return group

    @staticmethod
    def pulse_scale(widget: QWidget, duration: int = AnimationDurations.FAST,
                    scale_factor: float = 1.1) -> QSequentialAnimationGroup:
        """Animación de pulso (escala arriba y abajo)"""
        group = QSequentialAnimationGroup()

        current_size = widget.size()
        enlarged_size = QSize(
            int(current_size.width() * scale_factor),
            int(current_size.height() * scale_factor)
        )

        # Escalar hacia arriba
        scale_up = QPropertyAnimation(widget, b"size")
        scale_up.setDuration(duration)
        scale_up.setStartValue(current_size)
        scale_up.setEndValue(enlarged_size)
        scale_up.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        # Escalar hacia abajo
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setDuration(duration)
        scale_down.setStartValue(enlarged_size)
        scale_down.setEndValue(current_size)
        scale_down.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        group.addAnimation(scale_up)
        group.addAnimation(scale_down)

        return group

    @staticmethod
    def shake(widget: QWidget, duration: int = AnimationDurations.FAST,
              intensity: int = 10) -> QSequentialAnimationGroup:
        """Animación de sacudida (para errores)"""
        group = QSequentialAnimationGroup()

        original_pos = widget.pos()

        # Crear serie de movimientos
        for i in range(4):
            offset = intensity if i % 2 == 0 else -intensity
            target_pos = QPoint(original_pos.x() + offset, original_pos.y())

            move = QPropertyAnimation(widget, b"pos")
            move.setDuration(duration // 4)
            move.setStartValue(widget.pos() if i == 0 else None)
            move.setEndValue(target_pos)
            move.setEasingCurve(AnimationEasing.LINEAR)

            group.addAnimation(move)

        # Volver a posición original
        final_move = QPropertyAnimation(widget, b"pos")
        final_move.setDuration(duration // 4)
        final_move.setEndValue(original_pos)
        final_move.setEasingCurve(AnimationEasing.LINEAR)
        group.addAnimation(final_move)

        return group

    @staticmethod
    def glow_pulse(widget: QWidget, duration: int = AnimationDurations.NORMAL) -> QSequentialAnimationGroup:
        """Animación de pulso de brillo (para notificaciones)"""
        group = QSequentialAnimationGroup()

        # Crear efecto de opacidad si no existe
        if not widget.graphicsEffect():
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

        effect = widget.graphicsEffect()

        # Brillo hacia arriba
        brighten = QPropertyAnimation(effect, b"opacity")
        brighten.setDuration(duration)
        brighten.setStartValue(1.0)
        brighten.setEndValue(0.5)
        brighten.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        # Brillo hacia abajo
        dim = QPropertyAnimation(effect, b"opacity")
        dim.setDuration(duration)
        dim.setStartValue(0.5)
        dim.setEndValue(1.0)
        dim.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)

        group.addAnimation(brighten)
        group.addAnimation(dim)

        return group


class HoverAnimationMixin:
    """Mixin para añadir animaciones hover a widgets"""

    def setup_hover_animation(self, scale_factor: float = 1.05, duration: int = AnimationDurations.FAST):
        """Configurar animación al pasar el mouse"""
        self._original_size = None
        self._scale_factor = scale_factor
        self._hover_duration = duration
        self._is_hovered = False

    def enterEvent(self, event):
        """Handler al entrar el mouse"""
        if hasattr(super(), 'enterEvent'):
            super().enterEvent(event)

        if not self._is_hovered:
            self._is_hovered = True
            self._animate_hover_in()

    def leaveEvent(self, event):
        """Handler al salir el mouse"""
        if hasattr(super(), 'leaveEvent'):
            super().leaveEvent(event)

        if self._is_hovered:
            self._is_hovered = False
            self._animate_hover_out()

    def _animate_hover_in(self):
        """Animar entrada del hover"""
        if self._original_size is None:
            self._original_size = self.size()

        enlarged_size = QSize(
            int(self._original_size.width() * self._scale_factor),
            int(self._original_size.height() * self._scale_factor)
        )

        animation = QPropertyAnimation(self, b"size")
        animation.setDuration(self._hover_duration)
        animation.setStartValue(self.size())
        animation.setEndValue(enlarged_size)
        animation.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)
        animation.start()

        self._hover_animation = animation

    def _animate_hover_out(self):
        """Animar salida del hover"""
        if self._original_size is None:
            return

        animation = QPropertyAnimation(self, b"size")
        animation.setDuration(self._hover_duration)
        animation.setStartValue(self.size())
        animation.setEndValue(self._original_size)
        animation.setEasingCurve(AnimationEasing.IN_OUT_CUBIC)
        animation.start()

        self._hover_animation = animation


# Instancia global del sistema de animaciones
animations = AnimationSystem()


def get_animation_system() -> AnimationSystem:
    """Obtener instancia del sistema de animaciones"""
    return animations
