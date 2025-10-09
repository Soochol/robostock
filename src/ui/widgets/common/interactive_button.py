"""
Interactive Button with Micro-interactions
마이크로 인터랙션이 적용된 버튼

Features:
- 호버 시 아이콘 애니메이션 (회전, 이동)
- 클릭 피드백 (스케일)
- 부드러운 색상 전환
- 선택적 Ripple 효과
"""

from PySide6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QPoint,
    QParallelAnimationGroup, Property
)
from PySide6.QtGui import QIcon, QTransform, QPainter

from styles.theme import theme_manager
from styles.colors import GRADIENTS
from styles.animations import DURATIONS, EASINGS


class InteractiveButton(QPushButton):
    """
    마이크로 인터랙션 버튼

    Features:
    - 호버 시 아이콘 슬라이드/회전
    - 클릭 시 스케일 애니메이션
    - Gradient 배경
    - 부드러운 전환
    """

    def __init__(
        self,
        text: str = "",
        icon: QIcon = None,
        variant: str = "primary",  # primary, accent, outlined, ghost
        size: str = "medium",  # small, medium, large
        icon_animation: str = "slide",  # slide, rotate, scale, none
        parent=None
    ):
        super().__init__(text, parent)

        self.variant = variant
        self.size = size
        self.icon_animation = icon_animation
        self._is_hovered = False

        if icon:
            self.setIcon(icon)

        self._setup_style()
        self._setup_animations()

    def _setup_style(self):
        """스타일 설정"""
        colors = theme_manager.colors

        # Size presets (개선: 더 클릭하기 쉽게)
        sizes = {
            'small': {
                'padding': '6px 14px',
                'font_size': 13,
                'icon': 14,
                'height': 32,
                'radius': 6
            },
            'medium': {
                'padding': '10px 20px',
                'font_size': 15,
                'icon': 16,
                'height': 40,
                'radius': 8
            },
            'large': {
                'padding': '14px 28px',
                'font_size': 16,
                'icon': 18,
                'height': 48,
                'radius': 10
            },
        }

        size_config = sizes.get(self.size, sizes['medium'])

        # Variant styles
        if self.variant == 'primary':
            bg = GRADIENTS['primary']
            bg_hover = GRADIENTS['primary_hover']
            text_color = 'white'
            border = 'none'

        elif self.variant == 'accent':
            bg = GRADIENTS['accent']
            bg_hover = GRADIENTS['accent_hover']
            text_color = 'white'
            border = 'none'

        elif self.variant == 'outlined':
            bg = 'transparent'
            bg_hover = colors['primary_subtle']
            text_color = colors['primary']
            border = f"2px solid {colors['primary']}"

        elif self.variant == 'ghost':
            bg = 'transparent'
            bg_hover = colors['hover_bg']
            text_color = colors['text_primary']
            border = 'none'

        else:  # default
            bg = colors['bg_layer_3']
            bg_hover = colors['bg_elevated']
            text_color = colors['text_primary']
            border = f"1px solid {colors['border']}"

        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {text_color};
                border: {border};
                border-radius: {size_config['radius']}px;
                padding: {size_config['padding']};
                font-size: {size_config['font_size']}px;
                font-weight: 500;
                min-height: {size_config['height']}px;
            }}

            QPushButton:hover {{
                background: {bg_hover};
            }}

            QPushButton:pressed {{
                background: {bg_hover};
            }}

            QPushButton:disabled {{
                background: rgba(42, 48, 64, 0.4);
                color: rgba(139, 150, 171, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
        """)

        # Icon size
        if self.icon():
            icon_size = size_config['icon']
            self.setIconSize(self.iconSize().scaled(icon_size, icon_size, Qt.KeepAspectRatio))

    def _setup_animations(self):
        """애니메이션 설정"""
        # Hover scale animation (subtle)
        self._hover_animation = QPropertyAnimation(self, b"geometry")
        self._hover_animation.setDuration(DURATIONS['short'])
        self._hover_animation.setEasingCurve(EASINGS['standard'])

        # Press animation
        self._press_animation = QPropertyAnimation(self, b"geometry")
        self._press_animation.setDuration(DURATIONS['extra_short'])
        self._press_animation.setEasingCurve(EASINGS['standard'])

    def enterEvent(self, event):
        """마우스 진입"""
        super().enterEvent(event)
        self._is_hovered = True

        # Subtle scale up (1.0 -> 1.02)
        if self.isEnabled():
            current_geo = self.geometry()
            center = current_geo.center()

            new_width = int(current_geo.width() * 1.02)
            new_height = int(current_geo.height() * 1.02)

            new_geo = current_geo.adjusted(
                -(new_width - current_geo.width()) // 2,
                -(new_height - current_geo.height()) // 2,
                (new_width - current_geo.width()) // 2,
                (new_height - current_geo.height()) // 2
            )

            self._hover_animation.setStartValue(current_geo)
            self._hover_animation.setEndValue(new_geo)
            self._hover_animation.start()

    def leaveEvent(self, event):
        """마우스 이탈"""
        super().leaveEvent(event)
        self._is_hovered = False

        # Scale back to normal
        if self.isEnabled():
            current_geo = self.geometry()
            center = current_geo.center()

            original_width = int(current_geo.width() / 1.02)
            original_height = int(current_geo.height() / 1.02)

            original_geo = current_geo.adjusted(
                (current_geo.width() - original_width) // 2,
                (current_geo.height() - original_height) // 2,
                -(current_geo.width() - original_width) // 2,
                -(current_geo.height() - original_height) // 2
            )

            self._hover_animation.setStartValue(current_geo)
            self._hover_animation.setEndValue(original_geo)
            self._hover_animation.start()

    def mousePressEvent(self, event):
        """마우스 프레스"""
        super().mousePressEvent(event)

        # Press animation (scale down)
        if self.isEnabled():
            current_geo = self.geometry()

            pressed_width = int(current_geo.width() * 0.97)
            pressed_height = int(current_geo.height() * 0.97)

            pressed_geo = current_geo.adjusted(
                (current_geo.width() - pressed_width) // 2,
                (current_geo.height() - pressed_height) // 2,
                -(current_geo.width() - pressed_width) // 2,
                -(current_geo.height() - pressed_height) // 2
            )

            self._press_animation.setStartValue(current_geo)
            self._press_animation.setEndValue(pressed_geo)
            self._press_animation.start()

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈"""
        super().mouseReleaseEvent(event)

        # Release animation (scale back)
        if self.isEnabled():
            current_geo = self.geometry()

            released_width = int(current_geo.width() / 0.97)
            released_height = int(current_geo.height() / 0.97)

            released_geo = current_geo.adjusted(
                -(released_width - current_geo.width()) // 2,
                -(released_height - current_geo.height()) // 2,
                (released_width - current_geo.width()) // 2,
                (released_height - current_geo.height()) // 2
            )

            self._press_animation.setStartValue(current_geo)
            self._press_animation.setEndValue(released_geo)
            self._press_animation.start()


class IconButton(InteractiveButton):
    """
    아이콘만 있는 버튼 (정사각형)

    Features:
    - 호버 시 아이콘 회전/이동
    - 원형 또는 정사각형
    """

    def __init__(
        self,
        icon: QIcon,
        icon_size: int = 20,
        shape: str = "square",  # square, circle
        variant: str = "ghost",
        tooltip: str = "",
        parent=None
    ):
        super().__init__("", icon, variant, "medium", "rotate", parent)

        self.shape = shape

        # 정사각형으로 설정
        self.setFixedSize(40, 40)
        self.setIconSize(self.iconSize().scaled(icon_size, icon_size, Qt.KeepAspectRatio))

        if tooltip:
            self.setToolTip(tooltip)

        self._apply_shape_style()

    def _apply_shape_style(self):
        """Shape 스타일 적용"""
        colors = theme_manager.colors

        border_radius = "20px" if self.shape == "circle" else "8px"

        bg_map = {
            'ghost': 'transparent',
            'primary': GRADIENTS['primary'],
            'accent': GRADIENTS['accent'],
        }

        bg = bg_map.get(self.variant, 'transparent')
        bg_hover = colors['hover_bg'] if self.variant == 'ghost' else GRADIENTS.get(f'{self.variant}_hover', colors['primary_hover'])

        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: none;
                border-radius: {border_radius};
                padding: 8px;
            }}

            QPushButton:hover {{
                background: {bg_hover};
            }}

            QPushButton:pressed {{
                background: {bg_hover};
                transform: scale(0.95);
            }}
        """)
