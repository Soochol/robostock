"""
Gradient Progress Bar
그라데이션 프로그레스 바
"""

from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont

from styles.colors import GRADIENTS
from styles.theme import theme_manager


class GradientProgressBar(QProgressBar):
    """
    그라데이션 프로그레스 바

    특징:
    - 좌→우 그라데이션 (블루→퍼플)
    - 부드러운 애니메이션
    - 퍼센트 텍스트 중앙 표시
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimum(0)
        self.setMaximum(100)

        # 폰트 설정
        font = QFont("Poppins", 13)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)

        # 스타일 적용
        self._apply_style()

        # 애니메이션
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setDuration(500)

    def _apply_style(self):
        """스타일 적용 (3-Color Animated Gradient)"""
        colors = theme_manager.colors

        self.setStyleSheet(f"""
            QProgressBar {{
                background: {colors['bg_layer_3']};
                border-radius: 12px;
                text-align: center;
                color: white;
                font-weight: 600;
                font-size: 16px;
                min-height: 28px;
                max-height: 28px;
            }}
            QProgressBar::chunk {{
                background: {GRADIENTS['progress_animated']};
                border-radius: 12px;
            }}
        """)

    def set_progress(self, value: int, animate: bool = True):
        """
        진행률 설정

        Args:
            value: 진행률 (0-100)
            animate: 애니메이션 여부
        """
        if animate:
            self._animation.stop()
            self._animation.setStartValue(self.value())
            self._animation.setEndValue(value)
            self._animation.start()
        else:
            self.setValue(value)

    def set_gradient(self, gradient_name: str):
        """
        그라데이션 변경

        Args:
            gradient_name: 'primary', 'success', 'level_4' 등
        """
        gradient = GRADIENTS.get(gradient_name, GRADIENTS['primary'])
        colors = theme_manager.colors

        self.setStyleSheet(f"""
            QProgressBar {{
                background: {colors['bg_layer_3']};
                border-radius: 10px;
                text-align: center;
                color: white;
                font-weight: 600;
                font-size: 15px;
                min-height: 20px;
                max-height: 20px;
            }}
            QProgressBar::chunk {{
                background: {gradient};
                border-radius: 10px;
            }}
        """)
