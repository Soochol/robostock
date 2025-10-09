"""
Step Progress Widget
단계별 진행 표시 위젯
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

from styles.theme import theme_manager
from core.config import SPACING
from resources.icons import IconManager


class StepProgressWidget(QWidget):
    """
    단계별 진행 표시 위젯

    특징:
    - 각 단계별 상태 표시 (대기/진행중/완료/실패)
    - 진행 카운트 표시
    - 아이콘과 색상으로 시각화
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps = []
        self.step_widgets = []
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(SPACING['xs'])

    def set_steps(self, steps: list[str]):
        """
        단계 설정

        Args:
            steps: 단계 이름 리스트
                  예: ["종목 리스트 로드", "주가 데이터 수집", ...]
        """
        # 기존 위젯 제거
        for widget in self.step_widgets:
            widget.deleteLater()
        self.step_widgets.clear()

        self.steps = steps

        # 새로운 단계 위젯 생성
        for i, step_name in enumerate(steps):
            step_widget = self._create_step_widget(i, step_name)
            self.layout.addWidget(step_widget)
            self.step_widgets.append(step_widget)

    def _create_step_widget(self, index: int, name: str) -> QWidget:
        """단계 위젯 생성"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['sm'])

        # 상태 아이콘
        icon_label = QLabel()
        icon_label.setFixedSize(18, 18)
        icon_label.setObjectName(f"step_icon_{index}")
        layout.addWidget(icon_label)

        # 단계 이름
        name_label = QLabel(name)
        name_label.setFont(QFont("Inter", 11))
        name_label.setObjectName(f"step_name_{index}")
        layout.addWidget(name_label)

        # 진행 카운트 (진행중일 때만 표시)
        count_label = QLabel("")
        count_label.setFont(QFont("Inter", 10))
        count_label.setObjectName(f"step_count_{index}")
        count_label.hide()
        layout.addWidget(count_label)

        layout.addStretch()

        # 초기 상태: 대기
        self._update_step_style(widget, "pending")

        return widget

    def _update_step_style(
        self, widget: QWidget, status: str, count_text: str = ""
    ):
        """단계 스타일 업데이트"""
        icon_label = widget.findChild(QLabel, widget.objectName() + "_icon")
        name_label = widget.findChild(QLabel, widget.objectName() + "_name")
        count_label = widget.findChild(
            QLabel, widget.objectName() + "_count"
        )

        if not icon_label or not name_label or not count_label:
            # findChild로 찾지 못하면 직접 찾기
            children = widget.findChildren(QLabel)
            if len(children) >= 3:
                icon_label = children[0]
                name_label = children[1]
                count_label = children[2]

        colors = theme_manager.colors

        if status == "pending":
            # 대기: 회색 동그라미
            icon_label.setPixmap(
                IconManager.get_qicon(
                    "circle", 14, colors["text_disabled"]
                ).pixmap(QSize(14, 14))
            )
            name_label.setStyleSheet(
                f"color: {colors['text_tertiary']};"
            )
            count_label.hide()

        elif status == "in_progress":
            # 진행중: 파란색 화살표
            icon_label.setPixmap(
                IconManager.get_qicon(
                    "chevron-right", 16, colors["primary"]
                ).pixmap(QSize(16, 16))
            )
            name_label.setStyleSheet(
                f"color: {colors['primary']}; font-weight: 600;"
            )
            if count_text:
                count_label.setText(count_text)
                count_label.setStyleSheet(
                    f"color: {colors['text_tertiary']};"
                )
                count_label.show()
            else:
                count_label.hide()

        elif status == "completed":
            # 완료: 초록색 체크
            icon_label.setPixmap(
                IconManager.get_qicon(
                    "check-circle", 16, colors["success"]
                ).pixmap(QSize(16, 16))
            )
            name_label.setStyleSheet(
                f"color: {colors['text_secondary']};"
            )
            count_label.hide()

        elif status == "failed":
            # 실패: 빨간색 X
            icon_label.setPixmap(
                IconManager.get_qicon(
                    "x-circle", 16, colors["error"]
                ).pixmap(QSize(16, 16))
            )
            name_label.setStyleSheet(
                f"color: {colors['error']};"
            )
            count_label.hide()

    def update_step(
        self, index: int, status: str, count_text: str = ""
    ):
        """
        단계 상태 업데이트

        Args:
            index: 단계 인덱스 (0부터 시작)
            status: 'pending', 'in_progress', 'completed', 'failed'
            count_text: 진행 카운트 텍스트 (예: "45/200")
        """
        if 0 <= index < len(self.step_widgets):
            self._update_step_style(
                self.step_widgets[index], status, count_text
            )

    def reset(self):
        """모든 단계를 대기 상태로 리셋"""
        for widget in self.step_widgets:
            self._update_step_style(widget, "pending")
