"""
Glass Card
Glassmorphism 카드 위젯
"""

from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, Property
from PySide6.QtGui import QColor

from styles.theme import theme_manager
from core.config import SHADOWS


class GlassCard(QFrame):
    """
    Glassmorphism 스타일 카드

    특징:
    - 반투명 배경
    - 흐림 효과 (backdrop-filter 시뮬레이션)
    - 호버 시 살짝 떠오름
    - 그림자 효과
    """

    def __init__(self, parent=None, hover_effect: bool = False):
        super().__init__(parent)
        self._hover_effect = hover_effect
        self._is_hovered = False

        self.setObjectName("glass_card")
        self._apply_style()
        self._setup_shadow()

    def _apply_style(self):
        """스타일 적용 (Glassmorphism 2.0)"""
        colors = theme_manager.colors

        # Glassmorphism 2.0: 그라데이션 배경
        bg_gradient = (
            'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
            f'stop:0 {colors["surface_glass"]}, '
            f'stop:1 {colors["surface_frosted"]})'
        )

        # hover_effect가 활성화된 경우에만 hover 스타일 추가
        hover_style = ""
        if self._hover_effect:
            bg_hover_gradient = (
                'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
                f'stop:0 {colors["surface_glass_hover"]}, '
                f'stop:1 {colors["surface_frosted"]})'
            )
            hover_style = f"""
            #glass_card:hover {{
                background: {bg_hover_gradient};
                border-color: {colors['border_hover']};
            }}
            """

        self.setStyleSheet(f"""
            #glass_card {{
                background: {bg_gradient};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
            {hover_style}
        """)

    def _setup_shadow(self):
        """그림자 효과 설정 (Material Design 3 Layered Shadows)"""
        # MD3 스타일: 더 부드럽고 자연스러운 그림자
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)  # 20 → 32 (더 부드럽게)
        shadow.setXOffset(0)
        shadow.setYOffset(8)  # 4 → 8 (더 깊은 깊이감)
        shadow.setColor(QColor(0, 0, 0, 40))  # 50 → 40 (약간 투명하게)
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        """마우스 진입 시"""
        if self._hover_effect:
            self._is_hovered = True
            # 살짝 위로 이동 효과
            self.setStyleSheet(self.styleSheet() + """
                QFrame {
                    margin-top: -2px;
                }
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """마우스 이탈 시"""
        if self._hover_effect:
            self._is_hovered = False
            self._apply_style()
        super().leaveEvent(event)

    def set_glow(self, color: str = None):
        """
        네온 글로우 효과 추가

        Args:
            color: 글로우 색상 ('blue', 'green', 'red', 'pink')
        """
        if color:
            shadow_key = f'glow_{color}'
            if shadow_key in SHADOWS:
                shadow = QGraphicsDropShadowEffect(self)
                shadow.setBlurRadius(30)
                shadow.setXOffset(0)
                shadow.setYOffset(0)
                # 색상 파싱 (간단한 버전)
                glow_colors = {
                    'blue': QColor(59, 130, 246, 128),
                    'green': QColor(16, 185, 129, 128),
                    'red': QColor(239, 68, 68, 128),
                    'pink': QColor(255, 0, 128, 128),
                }
                shadow.setColor(glow_colors.get(color, QColor(59, 130, 246, 128)))
                self.setGraphicsEffect(shadow)
