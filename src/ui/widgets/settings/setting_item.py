"""
Setting Item Widget
개별 설정 항목 (체크박스 + 설명 + 컨트롤)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from styles.theme import theme_manager


class SettingItem(QWidget):
    """
    개별 설정 항목

    Features:
    - 체크박스 (활성화/비활성화)
    - 라벨 + 설명
    - 커스텀 컨트롤 위젯 (슬라이더, 콤보박스 등)
    """

    toggled = Signal(bool)
    valueChanged = Signal(object)

    def __init__(
        self,
        label: str,
        description: str = "",
        control_widget: QWidget = None,
        checked: bool = True,
        parent=None
    ):
        super().__init__(parent)

        self.label = label
        self.description = description
        self.control_widget = control_widget

        self._setup_ui(checked)

    def _setup_ui(self, checked: bool):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        # 상단: 체크박스
        self.checkbox = QCheckBox(self.label)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self._on_toggled)
        self._style_checkbox()
        layout.addWidget(self.checkbox)

        # 설명 텍스트
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                color: {theme_manager.colors['text_secondary']};
                font-size: 13px;
                padding-left: 26px;
                line-height: 1.4;
            """)
            layout.addWidget(desc_label)

        # 컨트롤 위젯
        if self.control_widget:
            control_container = QWidget()
            control_layout = QVBoxLayout(control_container)
            control_layout.setContentsMargins(26, 0, 0, 0)
            control_layout.addWidget(self.control_widget)
            layout.addWidget(control_container)

            # 체크박스 상태에 따라 컨트롤 활성화/비활성화
            self.control_widget.setEnabled(checked)

        # 하단 구분선
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            background: {theme_manager.colors['border']};
        """)
        layout.addWidget(separator)

    def _style_checkbox(self):
        """체크박스 스타일"""
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {theme_manager.colors['text_primary']};
                font-size: 15px;
                spacing: 8px;
                padding: 4px 0;
            }}
            QCheckBox:hover {{
                color: {theme_manager.colors['primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid {theme_manager.colors['border']};
                background: {theme_manager.colors['bg_layer_2']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {theme_manager.colors['primary']};
            }}
            QCheckBox::indicator:checked {{
                background: {theme_manager.colors['primary']};
                border-color: {theme_manager.colors['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            QCheckBox::indicator:checked:hover {{
                background: {theme_manager.colors['primary_hover']};
            }}
        """)

    def _on_toggled(self, checked: bool):
        """체크박스 토글"""
        if self.control_widget:
            self.control_widget.setEnabled(checked)
        self.toggled.emit(checked)

    def is_checked(self) -> bool:
        """체크 상태 반환"""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """체크 상태 설정"""
        self.checkbox.setChecked(checked)

    def get_value(self):
        """컨트롤 위젯의 값 반환"""
        if not self.control_widget:
            return self.is_checked()

        # 일반적인 위젯 타입에 대한 값 추출
        if hasattr(self.control_widget, 'value'):
            return self.control_widget.value()
        elif hasattr(self.control_widget, 'text'):
            return self.control_widget.text()
        elif hasattr(self.control_widget, 'currentText'):
            return self.control_widget.currentText()

        return None
