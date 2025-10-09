"""
Parameter Input Widget
값 입력을 위한 SpinBox 위젯
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Signal
from styles.theme import theme_manager


class ParameterSlider(QWidget):
    """
    파라미터 입력 위젯

    Features:
    - 숫자 입력 필드 (SpinBox)
    - 프리셋 버튼 (선택)
    """

    valueChanged = Signal(object)  # int, float, or formatted value

    def __init__(
        self,
        label: str,
        min_value: float = 0,
        max_value: float = 100,
        default_value: float = 50,
        step: float = 1,
        decimals: int = 0,
        suffix: str = "",
        presets: list = None,
        parent=None
    ):
        super().__init__(parent)

        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.decimals = decimals
        self.suffix = suffix
        self.presets = presets or []

        self._setup_ui(label, default_value)

    def _setup_ui(self, label: str, default_value: float):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 라벨
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
        """)
        layout.addWidget(label_widget)

        # 숫자 입력 필드
        if self.decimals > 0:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(self.decimals)
        else:
            self.spin_box = QSpinBox()

        # QSpinBox has max limit of 2,147,483,647, so cap it
        MAX_SPINBOX_VALUE = 2_147_483_647
        safe_min = max(self.min_value, -MAX_SPINBOX_VALUE)
        safe_max = min(self.max_value, MAX_SPINBOX_VALUE)
        safe_step = min(self.step, MAX_SPINBOX_VALUE)
        self.spin_box.setRange(safe_min, safe_max)
        self.spin_box.setSingleStep(safe_step)
        self.spin_box.setValue(min(default_value, safe_max))
        self.spin_box.setSuffix(f" {self.suffix}" if self.suffix else "")

        # 버튼 제거
        self.spin_box.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # 천 단위 구분자 (콤마) 추가
        self.spin_box.setGroupSeparatorShown(True)

        self.spin_box.setFixedWidth(150)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        self._style_spinbox(self.spin_box)
        layout.addWidget(self.spin_box)

        # 프리셋 버튼들
        if self.presets:
            preset_container = QWidget()
            preset_layout = QHBoxLayout(preset_container)
            preset_layout.setContentsMargins(0, 0, 0, 0)
            preset_layout.setSpacing(8)

            for preset_value, preset_label in self.presets:
                btn = QPushButton(preset_label)
                btn.clicked.connect(
                    lambda checked, v=preset_value: self.set_value(v)
                )
                self._style_preset_button(btn)
                preset_layout.addWidget(btn)

            preset_layout.addStretch()
            layout.addWidget(preset_container)

    def _style_spinbox(self, spinbox):
        """스핀박스 스타일"""
        spinbox.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background: {theme_manager.colors['bg_layer_2']};
                color: {theme_manager.colors['text_primary']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {theme_manager.colors['primary']};
            }}
        """)


    def _style_preset_button(self, button: QPushButton):
        """프리셋 버튼 스타일"""
        button.setStyleSheet(f"""
            QPushButton {{
                background: {theme_manager.colors['bg_layer_2']};
                color: {theme_manager.colors['text_secondary']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_primary']};
                border-color: {theme_manager.colors['primary']};
            }}
        """)

    def _on_value_changed(self, value: float):
        """스핀박스 값 변경"""
        self.valueChanged.emit(value)

    def value(self) -> float:
        """현재 값 반환"""
        return self.spin_box.value()

    def set_value(self, value: float):
        """값 설정"""
        # QSpinBox 최대값 제한 체크
        MAX_SPINBOX_VALUE = 2_147_483_647
        safe_value = min(value, MAX_SPINBOX_VALUE)

        # 업데이트 (시그널 방지를 위해 blockSignals 사용)
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(safe_value)
        self.spin_box.blockSignals(False)

        # 실제 값은 내부 저장
        self._actual_value = value
        self.valueChanged.emit(value)
