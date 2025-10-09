"""
Settings Search Bar
설정 검색 바 위젯
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from styles.theme import theme_manager


class SettingsSearchBar(QWidget):
    """
    설정 검색 바

    Features:
    - 실시간 검색
    - 검색어 하이라이트
    - 단축키 (Ctrl+F)
    """

    searchChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 검색 아이콘
        icon_label = QLabel("🔎")
        icon_font = QFont()
        icon_font.setPointSize(14)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # 검색 입력 필드
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "설정, 파라미터 검색... (Ctrl+F)"
        )
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setClearButtonEnabled(True)
        self._style_search_input()
        layout.addWidget(self.search_input)

    def _style_search_input(self):
        """검색 입력 필드 스타일"""
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {theme_manager.colors['bg_layer_2']};
                color: {theme_manager.colors['text_primary']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {theme_manager.colors['primary']};
                background: {theme_manager.colors['bg_layer_3']};
            }}
            QLineEdit::placeholder {{
                color: {theme_manager.colors['text_tertiary']};
            }}
        """)

    def _on_search_changed(self, text: str):
        """검색어 변경"""
        self.searchChanged.emit(text.lower())

    def clear(self):
        """검색어 초기화"""
        self.search_input.clear()

    def text(self) -> str:
        """현재 검색어 반환"""
        return self.search_input.text()
