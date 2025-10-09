"""
Skeleton Loader - Loading State Component
스켈레톤 로딩 컴포넌트

Features:
- 부드러운 shimmer 애니메이션
- 다양한 모양 (rect, circle, text)
- 커스터마이징 가능
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, Property,
    QTimer, QRect
)
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen

from styles.theme import theme_manager
from styles.animations import DURATIONS


class SkeletonLoader(QWidget):
    """
    스켈레톤 로더

    Features:
    - Shimmer 애니메이션 (좌→우 이동)
    - 다양한 모양 지원
    - 반복 애니메이션
    """

    def __init__(
        self,
        width: int = 200,
        height: int = 20,
        shape: str = "rect",  # rect, circle, text
        animated: bool = True,
        parent=None
    ):
        super().__init__(parent)

        self.shape = shape
        self.animated = animated
        self._shimmer_x = 0

        self.setFixedSize(width, height)

        if self.animated:
            self._setup_animation()

    def _setup_animation(self):
        """Shimmer 애니메이션 설정"""
        self._animation = QPropertyAnimation(self, b"shimmer_x")
        self._animation.setDuration(1500)  # 1.5초
        self._animation.setStartValue(-self.width())
        self._animation.setEndValue(self.width() * 2)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.setLoopCount(-1)  # 무한 반복
        self._animation.start()

    def get_shimmer_x(self):
        return self._shimmer_x

    def set_shimmer_x(self, value):
        self._shimmer_x = value
        self.update()

    shimmer_x = Property(int, get_shimmer_x, set_shimmer_x)

    def paintEvent(self, event):
        """페인트 이벤트"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = theme_manager.colors

        # 배경색 (skeleton base)
        base_color = QColor(colors['bg_layer_3'])

        # Border radius
        radius = self.height() // 2 if self.shape == 'circle' else 8

        # 배경 그리기
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base_color)

        if self.shape == 'circle':
            # 원형
            painter.drawEllipse(0, 0, self.width(), self.height())
        else:
            # 사각형 (텍스트 포함)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)

        # Shimmer 효과 (애니메이션)
        if self.animated:
            gradient = QLinearGradient(self._shimmer_x, 0, self._shimmer_x + self.width(), 0)

            # 투명 → 하이라이트 → 투명
            highlight_color = QColor(255, 255, 255, 30)  # 하얀 하이라이트
            gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
            gradient.setColorAt(0.5, highlight_color)
            gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

            painter.setBrush(gradient)

            if self.shape == 'circle':
                painter.drawEllipse(0, 0, self.width(), self.height())
            else:
                painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)


class SkeletonText(QWidget):
    """
    텍스트 스켈레톤 (여러 줄)

    Features:
    - 여러 줄 텍스트 시뮬레이션
    - 각 줄마다 다른 너비
    """

    def __init__(self, lines: int = 3, line_height: int = 16, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for i in range(lines):
            # 마지막 줄은 짧게
            if i == lines - 1:
                width = 150
            else:
                width = 200

            skeleton = SkeletonLoader(width, line_height, "text", animated=True)
            layout.addWidget(skeleton)


class SkeletonCard(QWidget):
    """
    카드 스켈레톤 (아이콘 + 텍스트 조합)

    Features:
    - 원형 아이콘 + 텍스트 라인
    - 카드 로딩 상태 표현
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 원형 아이콘
        icon_skeleton = SkeletonLoader(48, 48, "circle", animated=True)
        layout.addWidget(icon_skeleton)

        # 텍스트 영역
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)

        # 제목 (굵게)
        title_skeleton = SkeletonLoader(150, 20, "text", animated=True)
        text_layout.addWidget(title_skeleton)

        # 설명
        desc_skeleton = SkeletonLoader(200, 16, "text", animated=True)
        text_layout.addWidget(desc_skeleton)

        layout.addLayout(text_layout)
        layout.addStretch()


class SkeletonTable(QWidget):
    """
    테이블 스켈레톤 (행 여러 개)

    Features:
    - 테이블 로딩 상태
    - 여러 행 시뮬레이션
    """

    def __init__(self, rows: int = 5, columns: int = 4, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for row in range(rows):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(16)

            for col in range(columns):
                # 첫 번째 열은 좁게 (체크박스 등)
                if col == 0:
                    width = 50
                else:
                    width = 120

                skeleton = SkeletonLoader(width, 16, "text", animated=True)
                row_layout.addWidget(skeleton)

            row_layout.addStretch()
            layout.addLayout(row_layout)
