"""
Collapsible Section Widget
접을 수 있는 설정 섹션
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from styles.theme import theme_manager


class CollapsibleSection(QWidget):
    """
    접을 수 있는 설정 섹션

    Features:
    - 헤더 클릭으로 접기/펴기
    - 애니메이션 효과
    - 아이콘 표시
    """

    toggled = Signal(bool)  # expanded state

    def __init__(
        self,
        title: str,
        icon: str = "",
        expanded: bool = True,
        parent=None
    ):
        super().__init__(parent)

        self.is_expanded = expanded
        self.title = title
        self.icon = icon

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 헤더
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        # 컨텐츠 컨테이너
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 12, 16, 12)
        self.content_layout.setSpacing(12)

        # 컨텐츠 프레임 (보더 포함)
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")
        content_frame_layout = QVBoxLayout(self.content_frame)
        content_frame_layout.setContentsMargins(0, 0, 0, 0)
        content_frame_layout.addWidget(self.content_widget)

        self._style_content_frame()

        main_layout.addWidget(self.content_frame)

        # 초기 상태 설정
        self.content_frame.setVisible(self.is_expanded)

    def _create_header(self) -> QWidget:
        """헤더 생성"""
        header = QPushButton()
        header.setObjectName("section_header")
        header.setCursor(Qt.PointingHandCursor)
        header.clicked.connect(self.toggle)

        # 텍스트를 직접 QPushButton에 설정
        arrow = "▼" if self.is_expanded else "▶"
        icon_text = f"{self.icon} " if self.icon else ""
        header.setText(f"{arrow}  {icon_text}{self.title}")

        # 폰트 설정
        header_font = QFont("Segoe UI", 13)
        header_font.setWeight(QFont.Weight.DemiBold)
        header.setFont(header_font)

        # 왼쪽 정렬
        header.setStyleSheet(f"""
            QPushButton#section_header {{
                background: {theme_manager.colors['bg_layer_2']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 6px;
                text-align: left;
                padding: 12px 16px;
                color: #FFFFFF;
                font-weight: bold;
            }}
            QPushButton#section_header:hover {{
                background: {theme_manager.colors['bg_layer_3']};
                border-color: {theme_manager.colors['primary']};
            }}
        """)

        self.header_button = header  # 토글 시 텍스트 업데이트용

        return header

    def _style_content_frame(self):
        """컨텐츠 프레임 스타일"""
        self.content_frame.setStyleSheet(f"""
            #content_frame {{
                background: {theme_manager.colors['bg_layer_1']};
                border: 1px solid {theme_manager.colors['border']};
                border-top: none;
                border-radius: 0 0 6px 6px;
            }}
        """)

    def toggle(self):
        """접기/펴기 토글"""
        self.is_expanded = not self.is_expanded

        # 버튼 텍스트 업데이트
        arrow = "▼" if self.is_expanded else "▶"
        icon_text = f"{self.icon} " if self.icon else ""
        self.header_button.setText(f"{arrow}  {icon_text}{self.title}")

        self.content_frame.setVisible(self.is_expanded)
        self.toggled.emit(self.is_expanded)

    def add_widget(self, widget: QWidget):
        """컨텐츠에 위젯 추가"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """컨텐츠에 레이아웃 추가"""
        self.content_layout.addLayout(layout)

    def set_expanded(self, expanded: bool):
        """확장 상태 설정"""
        if self.is_expanded != expanded:
            self.toggle()
