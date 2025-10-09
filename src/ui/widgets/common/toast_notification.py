"""
Toast Notification System
토스트 알림 시스템

Features:
- 우아한 슬라이드 인/아웃
- 4가지 타입 (info, success, warning, error)
- 자동 사라짐 + 수동 닫기
- 스택 관리 (여러 개 동시 표시)
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal, QPoint
from PySide6.QtGui import QFont

from styles.theme import theme_manager
from styles.animations import DURATIONS, create_slide_animation, create_fade_animation
from resources.icons import get_status_icon, get_primary_icon


class ToastNotification(QWidget):
    """
    개별 토스트 알림

    Features:
    - 타입별 색상
    - 아이콘 + 메시지
    - 닫기 버튼
    - 자동 사라짐
    """

    closed = Signal()

    def __init__(
        self,
        message: str,
        toast_type: str = "info",  # info, success, warning, error
        duration: int = 3000,  # 3초
        parent=None
    ):
        super().__init__(parent)

        self.toast_type = toast_type
        self.duration = duration

        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        self._setup_ui(message)
        self._setup_style()

        # 자동 닫기 타이머
        if self.duration > 0:
            QTimer.singleShot(self.duration, self._start_close_animation)

    def _setup_ui(self, message: str):
        """UI 구성"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # 아이콘
        icon_map = {
            'info': ('info', theme_manager.colors['info']),
            'success': ('check-circle', theme_manager.colors['success']),
            'warning': ('alert-triangle', theme_manager.colors['warning']),
            'error': ('x-circle', theme_manager.colors['error']),
        }

        icon_name, icon_color = icon_map.get(self.toast_type, icon_map['info'])

        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_status_icon(icon_name, 20).pixmap(20, 20))
        layout.addWidget(self.icon_label)

        # 메시지
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        message_font = QFont("Inter", 14)
        self.message_label.setFont(message_font)
        layout.addWidget(self.message_label, 1)

        # 닫기 버튼
        close_btn = QPushButton()
        close_btn.setIcon(get_primary_icon('x', 14))
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self._start_close_animation)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['hover_bg']};
            }}
        """)
        layout.addWidget(close_btn)

    def _setup_style(self):
        """스타일 설정"""
        colors = theme_manager.colors

        # 타입별 배경색
        bg_map = {
            'info': colors['info_subtle'],
            'success': colors['success_subtle'],
            'warning': colors['warning_subtle'],
            'error': colors['error_subtle'],
        }

        border_map = {
            'info': colors['info'],
            'success': colors['success'],
            'warning': colors['warning'],
            'error': colors['error'],
        }

        bg = bg_map.get(self.toast_type, bg_map['info'])
        border = border_map.get(self.toast_type, border_map['info'])

        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)

        self.message_label.setStyleSheet(f"""
            color: {colors['text_primary']};
        """)

    def _start_close_animation(self):
        """닫기 애니메이션 시작"""
        # Fade out + 오른쪽으로 슬라이드
        fade = create_fade_animation(self, 1.0, 0.0, DURATIONS['medium'])

        current_pos = self.pos()
        end_pos = QPoint(current_pos.x() + 50, current_pos.y())  # 오른쪽으로 50px
        slide = create_slide_animation(self, current_pos, end_pos, DURATIONS['medium'])

        fade.finished.connect(self._on_animation_finished)
        fade.start()
        slide.start()

    def _on_animation_finished(self):
        """애니메이션 완료"""
        self.closed.emit()
        self.deleteLater()


class ToastManager(QWidget):
    """
    토스트 매니저 (스택 관리)

    Features:
    - 여러 토스트 동시 표시
    - 위에서 아래로 쌓임
    - 자동 위치 조정
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addStretch()

        self.toasts = []

        # 화면 우측 상단에 배치
        if parent:
            self._reposition()

    def _reposition(self):
        """위치 재조정 (우측 상단)"""
        if self.parent():
            parent_rect = self.parent().rect()
            self.setGeometry(
                parent_rect.width() - 420,
                20,
                400,
                parent_rect.height() - 40
            )

    def show_toast(
        self,
        message: str,
        toast_type: str = "info",
        duration: int = 3000
    ):
        """
        토스트 표시

        Args:
            message: 메시지
            toast_type: 타입 (info, success, warning, error)
            duration: 지속 시간 (ms), 0이면 수동 닫기만
        """
        toast = ToastNotification(message, toast_type, duration)
        toast.closed.connect(lambda: self._remove_toast(toast))

        # 레이아웃에 추가 (위에서 아래로)
        self.layout().insertWidget(0, toast)
        self.toasts.append(toast)

        # 슬라이드 인 애니메이션
        toast.setWindowOpacity(0)
        end_pos = toast.pos()
        start_pos = QPoint(end_pos.x() + 50, end_pos.y())  # 오른쪽에서 시작

        # Fade in + Slide in
        fade = create_fade_animation(toast, 0.0, 1.0, DURATIONS['medium'])
        slide = create_slide_animation(toast, start_pos, end_pos, DURATIONS['medium'])

        fade.start()
        slide.start()

        self.show()

    def _remove_toast(self, toast: ToastNotification):
        """토스트 제거"""
        if toast in self.toasts:
            self.toasts.remove(toast)

        # 모든 토스트가 제거되면 숨김
        if not self.toasts:
            self.hide()


# 전역 토스트 매니저 인스턴스
_toast_manager_instance = None


def get_toast_manager(parent=None) -> ToastManager:
    """
    전역 토스트 매니저 가져오기 (싱글톤)

    Args:
        parent: 부모 위젯 (최초 생성 시 필요)

    Returns:
        ToastManager
    """
    global _toast_manager_instance

    if _toast_manager_instance is None:
        _toast_manager_instance = ToastManager(parent)

    return _toast_manager_instance


def show_toast(message: str, toast_type: str = "info", duration: int = 3000):
    """
    간편한 토스트 표시 함수

    Args:
        message: 메시지
        toast_type: info, success, warning, error
        duration: 지속 시간 (ms)
    """
    manager = get_toast_manager()
    if manager:
        manager.show_toast(message, toast_type, duration)


# 편의 함수들
def show_info(message: str, duration: int = 3000):
    """정보 토스트"""
    show_toast(message, "info", duration)


def show_success(message: str, duration: int = 3000):
    """성공 토스트"""
    show_toast(message, "success", duration)


def show_warning(message: str, duration: int = 3000):
    """경고 토스트"""
    show_toast(message, "warning", duration)


def show_error(message: str, duration: int = 3000):
    """에러 토스트"""
    show_toast(message, "error", duration)
