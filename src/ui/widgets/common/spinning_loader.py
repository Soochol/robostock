"""
Spinning Loader
회전 로딩 스피너

Features:
- 부드러운 회전 애니메이션
- 다양한 크기
- 커스텀 색상
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QConicalGradient

from styles.theme import theme_manager


class SpinningLoader(QWidget):
    """
    회전 스피너 로더

    Features:
    - Conical gradient 회전
    - 부드러운 애니메이션
    """

    def __init__(
        self,
        size: int = 40,
        color: str = None,
        parent=None
    ):
        super().__init__(parent)

        self.spinner_size = size
        self.spinner_color = color or theme_manager.colors['primary']
        self._rotation_angle = 0

        self.setFixedSize(size, size)

        # 회전 타이머
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(16)  # ~60fps

    def _rotate(self):
        """회전 각도 증가"""
        self._rotation_angle = (self._rotation_angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        """페인트 이벤트"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 중심점
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 4

        # Conical Gradient (회전 그라데이션)
        gradient = QConicalGradient(center_x, center_y, self._rotation_angle)

        # 투명 → 색상
        base_color = QColor(self.spinner_color)
        transparent = QColor(base_color)
        transparent.setAlpha(0)

        gradient.setColorAt(0.0, transparent)
        gradient.setColorAt(0.7, base_color)
        gradient.setColorAt(1.0, base_color)

        # 원 그리기
        pen = QPen()
        pen.setWidth(3)
        pen.setBrush(gradient)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)
        painter.drawArc(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
            0,
            270 * 16  # 3/4 원
        )

    def start(self):
        """애니메이션 시작"""
        self._timer.start()

    def stop(self):
        """애니메이션 정지"""
        self._timer.stop()

    def isRunning(self) -> bool:
        """실행 중인지 확인"""
        return self._timer.isActive()


class DotLoader(QWidget):
    """
    점 3개 로더 (...)

    Features:
    - 3개 점이 순차적으로 튕김
    - 부드러운 애니메이션
    """

    def __init__(
        self,
        dot_size: int = 8,
        spacing: int = 12,
        color: str = None,
        parent=None
    ):
        super().__init__(parent)

        self.dot_size = dot_size
        self.spacing = spacing
        self.dot_color = color or theme_manager.colors['primary']
        self._current_dot = 0
        self._animation_step = 0  # 0-10 (튕김 높이)

        width = (dot_size + spacing) * 3
        self.setFixedSize(width, dot_size * 3)

        # 애니메이션 타이머
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)  # 20fps

    def _animate(self):
        """애니메이션 업데이트"""
        self._animation_step += 1

        if self._animation_step > 10:
            self._animation_step = 0
            self._current_dot = (self._current_dot + 1) % 3

        self.update()

    def paintEvent(self, event):
        """페인트 이벤트"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        base_y = self.height() - self.dot_size
        color = QColor(self.dot_color)

        for i in range(3):
            x = i * (self.dot_size + self.spacing)

            # 현재 점이 튕김
            if i == self._current_dot:
                # 사인 곡선으로 부드러운 튕김
                import math
                bounce_height = math.sin(self._animation_step / 10 * math.pi) * self.dot_size * 2
                y = base_y - bounce_height
            else:
                y = base_y

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x), int(y), self.dot_size, self.dot_size)

    def start(self):
        """애니메이션 시작"""
        self._timer.start()

    def stop(self):
        """애니메이션 정지"""
        self._timer.stop()
