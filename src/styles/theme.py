"""
Theme Manager
테마 관리 (다크/라이트 모드 전환)
"""

from PySide6.QtCore import QObject, Signal
from .colors import DARK_COLORS, LIGHT_COLORS, GRADIENTS
from .typography import font_to_qss
from core.enums import ThemeMode

class ThemeManager(QObject):
    """
    테마 매니저 (싱글톤)

    기능:
    - 다크/라이트 모드 전환
    - QSS 스타일시트 생성
    - 색상/폰트 동적 적용
    """

    theme_changed = Signal(str)  # "dark" or "light"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._current_mode = ThemeMode.DARK
        self._initialized = True

    @property
    def current_mode(self) -> ThemeMode:
        """현재 테마 모드"""
        return self._current_mode

    @property
    def colors(self) -> dict:
        """현재 테마의 색상 팔레트"""
        return DARK_COLORS if self._current_mode == ThemeMode.DARK else LIGHT_COLORS

    def set_theme(self, mode: ThemeMode):
        """테마 변경"""
        if mode != self._current_mode:
            self._current_mode = mode
            self.theme_changed.emit(mode.value)

    def toggle_theme(self):
        """테마 토글"""
        new_mode = ThemeMode.LIGHT if self._current_mode == ThemeMode.DARK else ThemeMode.DARK
        self.set_theme(new_mode)

    def get_stylesheet(self) -> str:
        """전역 QSS 스타일시트 생성"""
        colors = self.colors

        return f"""
        /* ===== Global Styles ===== */
        * {{
            font-family: "Inter", "Pretendard Variable", "Apple SD Gothic Neo", sans-serif;
        }}

        QMainWindow {{
            background-color: {colors['bg_layer_1']};
        }}

        QWidget {{
            background-color: transparent;
            color: {colors['text_primary']};
        }}

        /* ===== Scrollbar ===== */
        QScrollBar:vertical {{
            background: {colors['bg_layer_2']};
            width: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors['text_tertiary']};
            min-height: 20px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors['text_secondary']};
        }}

        QScrollBar:horizontal {{
            background: {colors['bg_layer_2']};
            height: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors['text_tertiary']};
            min-width: 20px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors['text_secondary']};
        }}

        /* ===== Button (Modern Gradient Style) ===== */
        QPushButton {{
            background: {GRADIENTS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            font-size: 15px;
            min-height: 40px;
        }}

        QPushButton:hover {{
            background: {GRADIENTS['primary_hover']};
        }}

        QPushButton:pressed {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['primary_pressed']},
                stop:1 #1E40AF
            );
        }}

        QPushButton:disabled {{
            background: rgba(42, 48, 64, 0.4);
            color: rgba(139, 150, 171, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* Accent Button Variant */
        QPushButton[accent="true"] {{
            background: {GRADIENTS['accent']};
        }}

        QPushButton[accent="true"]:hover {{
            background: {GRADIENTS['accent_hover']};
        }}

        QPushButton[accent="true"]:pressed {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['accent_pressed']},
                stop:1 #D44315
            );
        }}

        /* Outlined Button Variant */
        QPushButton[variant="outlined"] {{
            background: transparent;
            color: {colors['primary']};
            border: 2px solid {colors['primary']};
            border-radius: 8px;
            padding: 9px 19px;
        }}

        QPushButton[variant="outlined"]:hover {{
            background: {colors['primary_subtle']};
            border-color: {colors['primary_hover']};
        }}

        QPushButton[variant="outlined"]:pressed {{
            background: {colors['primary_subtle']};
            border-color: {colors['primary_pressed']};
        }}

        /* Ghost Button Variant */
        QPushButton[variant="ghost"] {{
            background: transparent;
            color: {colors['text_primary']};
            border: none;
            padding: 10px 20px;
        }}

        QPushButton[variant="ghost"]:hover {{
            background: {colors['hover_bg']};
        }}

        QPushButton[variant="ghost"]:pressed {{
            background: {colors['active_bg']};
        }}

        /* ===== Input ===== */
        QLineEdit {{
            background: {colors['bg_glass']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 15px;
        }}

        QLineEdit:focus {{
            border-color: {colors['primary']};
            background: {colors['bg_glass_hover']};
        }}

        /* ===== ComboBox ===== */
        QComboBox {{
            background: {colors['bg_glass']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 15px;
        }}

        QComboBox:hover {{
            border-color: {colors['border_hover']};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {colors['text_secondary']};
            margin-right: 8px;
        }}

        /* ===== CheckBox ===== */
        QCheckBox {{
            color: {colors['text_primary']};
            font-size: 15px;
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {colors['border']};
            background: {colors['bg_layer_3']};
        }}

        QCheckBox::indicator:checked {{
            background: {colors['primary']};
            border-color: {colors['primary']};
        }}

        /* ===== Table ===== */
        QTableWidget {{
            background: {colors['bg_layer_2']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            gridline-color: {colors['divider']};
        }}

        QTableWidget::item {{
            padding: 8px;
            color: {colors['text_primary']};
        }}

        QTableWidget::item:selected {{
            background: {colors['primary_subtle']};
            color: {colors['text_primary']};
        }}

        QHeaderView::section {{
            background: {colors['bg_layer_3']};
            color: {colors['text_secondary']};
            padding: 12px;
            border: none;
            border-bottom: 1px solid {colors['divider']};
            font-weight: 600;
            font-size: 13px;
        }}

        /* ===== Splitter ===== */
        QSplitter::handle {{
            background: {colors['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 1px;
        }}

        QSplitter::handle:vertical {{
            height: 1px;
        }}

        QSplitter::handle:hover {{
            background: {colors['primary']};
        }}

        /* ===== ProgressBar (3-Color Gradient) ===== */
        QProgressBar {{
            background: {colors['bg_layer_3']};
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: 600;
            font-size: 13px;
            height: 20px;
        }}

        QProgressBar::chunk {{
            background: {GRADIENTS['progress_animated']};
            border-radius: 10px;
        }}

        /* ===== TabWidget ===== */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 8px;
            background: {colors['bg_layer_2']};
        }}

        QTabBar::tab {{
            background: {colors['bg_layer_3']};
            color: {colors['text_secondary']};
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background: {colors['primary']};
            color: white;
        }}

        QTabBar::tab:hover {{
            background: {colors['primary_subtle']};
        }}

        /* ===== Menu ===== */
        QMenu {{
            background: {colors['bg_layer_3']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 4px;
        }}

        QMenu::item {{
            background: transparent;
            color: {colors['text_primary']};
            padding: 8px 24px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background: {colors['primary_subtle']};
        }}

        /* ===== ToolTip ===== */
        QToolTip {{
            background: {colors['bg_layer_3']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }}
        """

# 싱글톤 인스턴스
theme_manager = ThemeManager()
