"""
Main Window
메인 윈도우 - 3-Zone 레이아웃
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QFrame, QStackedWidget, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from core.config import UI_CONFIG, ICONS
from core.enums import LayoutMode, PanelType
from core.signals import global_signals
from styles.theme import theme_manager
from resources.icons import IconManager, get_menu_icon, get_primary_icon
from ui.panels.block_detector_settings_panel import BlockDetectorSettingsPanel
from ui.panels.chart_viewer_panel import ChartViewerPanel
from ui.panels.data_collection_panel import DataCollectionPanel


class MainWindow(QMainWindow):
    """
    메인 윈도우

    구조:
        ┌─────────────────────────────────────┐
        │ Header                              │
        ├──────┬──────────────────┬───────────┤
        │Sidebar│   Main Canvas    │  Insight  │
        └──────┴──────────────────┴───────────┘
        │ Status Bar                          │
        └─────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()
        self._current_layout_mode = LayoutMode.STANDARD
        self._current_panel = PanelType.BLOCK_DETECTOR  # 기본 패널
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()

    def _setup_window(self):
        """윈도우 기본 설정"""
        window_config = UI_CONFIG['window']
        self.setWindowTitle(window_config['title'])

        # 윈도우 크기
        width, height = window_config['default_size']
        self.setGeometry(100, 50, width, height)

        # 최소 크기
        min_width, min_height = window_config['min_size']
        self.setMinimumSize(min_width, min_height)

    def _setup_ui(self):
        """UI 레이아웃 구성"""
        # 중앙 위젯
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 헤더
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        # 2. 바디 (3-Zone: Sidebar + Canvas + Insight)
        body_splitter = QSplitter(Qt.Horizontal)

        # 2-2. Main Canvas (비주얼존) - QStackedWidget으로 변경
        self.main_canvas = QStackedWidget()
        self.main_canvas.setObjectName("main_canvas")

        # 패널 추가
        self.data_collection_panel = DataCollectionPanel()
        self.block_detector_panel = BlockDetectorSettingsPanel()
        self.chart_viewer_panel = ChartViewerPanel()
        self.main_canvas.addWidget(self.data_collection_panel)
        self.main_canvas.addWidget(self.block_detector_panel)
        self.main_canvas.addWidget(self.chart_viewer_panel)

        # 2-1. Sidebar (컨트롤존) - 패널 생성 후에 생성
        self.sidebar = self._create_sidebar()
        layout_config = UI_CONFIG['layout_modes'][self._current_layout_mode]
        self.sidebar.setFixedWidth(layout_config['sidebar_width'])
        body_splitter.addWidget(self.sidebar)

        # 환영 화면 (나중에 제거 가능)
        welcome_panel = self._create_welcome_panel()
        self.main_canvas.addWidget(welcome_panel)

        # 기본 패널 설정 (블록 탐지)
        self.main_canvas.setCurrentWidget(self.block_detector_panel)

        body_splitter.addWidget(self.main_canvas)

        body_splitter.setStretchFactor(0, 0)  # Sidebar 고정
        body_splitter.setStretchFactor(1, 1)  # Canvas 가변

        main_layout.addWidget(body_splitter)

        # 3. 상태바
        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)

        self.setCentralWidget(central_widget)

    def _create_header(self) -> QWidget:
        """헤더 생성"""
        header = QFrame()
        header.setFixedHeight(UI_CONFIG['header_height'])
        header.setObjectName("header")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)

        # 로고 + 타이틀 (아이콘 버튼 + 텍스트)
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(8)

        # 타겟 아이콘
        logo_btn = QPushButton()
        logo_btn.setIcon(get_primary_icon('target', 28))
        logo_btn.setIconSize(QSize(28, 28))
        logo_btn.setFlat(True)
        logo_btn.setFixedSize(40, 40)
        logo_layout.addWidget(logo_btn)

        # 타이틀 텍스트
        title_label = QLabel("RoboStock")
        logo_font = QFont("Poppins", 20)
        logo_font.setBold(True)
        title_label.setFont(logo_font)
        logo_layout.addWidget(title_label)

        layout.addWidget(logo_container)
        layout.addStretch()

        # 검색 버튼
        search_btn = QPushButton()
        search_btn.setIcon(get_menu_icon('search', 20))
        search_btn.setIconSize(QSize(20, 20))
        search_btn.setFlat(True)
        search_btn.setFixedSize(36, 36)
        layout.addWidget(search_btn)

        # 알림 버튼
        notification_btn = QPushButton()
        notification_btn.setIcon(get_menu_icon('bell', 20))
        notification_btn.setIconSize(QSize(20, 20))
        notification_btn.setFlat(True)
        notification_btn.setFixedSize(36, 36)
        layout.addWidget(notification_btn)

        # 설정 버튼
        settings_btn = QPushButton()
        settings_btn.setIcon(get_menu_icon('settings', 20))
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.setFlat(True)
        settings_btn.setFixedSize(36, 36)
        layout.addWidget(settings_btn)

        # 사용자 버튼
        user_btn = QPushButton()
        user_btn.setIcon(get_menu_icon('user', 20))
        user_btn.setIconSize(QSize(20, 20))
        user_btn.setFlat(True)
        user_btn.setFixedSize(36, 36)
        layout.addWidget(user_btn)

        # 날짜
        date_label = QLabel("2025-10-08")
        layout.addWidget(date_label)

        colors = theme_manager.colors
        header.setStyleSheet(f"""
            #header {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(26, 31, 46, 0.95),
                    stop:1 rgba(26, 31, 46, 0.7)
                );
                border-bottom: 1px solid {colors['border']};
            }}
        """)

        return header

    def _create_sidebar(self) -> QWidget:
        """사이드바 생성 (컨트롤존)"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)

        # 로고 버튼
        logo_btn = QPushButton()
        logo_btn.setIcon(get_primary_icon('target', 32))
        logo_btn.setIconSize(QSize(32, 32))
        logo_btn.setFlat(True)
        logo_btn.setFixedSize(48, 48)
        logo_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['bg_layer_3']};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(logo_btn, 0, Qt.AlignCenter)

        # 메뉴 항목 (아이콘 + 텍스트)
        menu_items = [
            ("데이터 수집", ICONS['data_collection'], self.data_collection_panel),
            ("블록 탐지", ICONS['block_detector'], self.block_detector_panel),
            ("차트 뷰어", ICONS['chart_viewer'], self.chart_viewer_panel),
            ("케이스", ICONS['case_manager'], None),
            ("팩터분석", ICONS['factor_analysis'], None),
            ("학습", ICONS['pattern_learning'], None),
            ("백테스팅", ICONS['backtesting'], None),
        ]

        self.menu_buttons = []
        for item_text, icon_name, panel_widget in menu_items:
            btn = QPushButton(f"  {item_text}")
            btn.setIcon(get_menu_icon(icon_name, 18))
            btn.setIconSize(QSize(18, 18))
            btn.setFont(QFont("Inter", 12))
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 12px;
                    border-radius: 8px;
                    color: {theme_manager.colors['text_secondary']};
                    border: none;
                    background: transparent;
                }}
                QPushButton:hover {{
                    background: {theme_manager.colors['bg_layer_3']};
                    color: {theme_manager.colors['text_primary']};
                }}
                QPushButton:pressed {{
                    background: {theme_manager.colors['primary_subtle']};
                }}
            """)

            # 패널 전환 연결 - 클로저 문제 해결
            if panel_widget is not None:
                def make_switch_panel(widget):
                    return lambda: self.main_canvas.setCurrentWidget(widget)
                btn.clicked.connect(make_switch_panel(panel_widget))

            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # 설정 버튼 (하단)
        settings_btn = QPushButton("  설정")
        settings_btn.setIcon(get_menu_icon('settings', 18))
        settings_btn.setIconSize(QSize(18, 18))
        settings_btn.setFont(QFont("Inter", 12))
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px 12px;
                border-radius: 8px;
                color: {theme_manager.colors['text_secondary']};
                border: none;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_primary']};
            }}
        """)
        layout.addWidget(settings_btn)

        colors = theme_manager.colors
        sidebar.setStyleSheet(f"""
            #sidebar {{
                background: {colors['bg_layer_2']};
                border-right: 1px solid {colors['border']};
            }}
        """)

        return sidebar

    def _create_welcome_panel(self) -> QWidget:
        """환영 패널 생성"""
        panel = QFrame()
        panel.setObjectName("welcome_panel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)

        # 환영 메시지
        welcome = QLabel("🎯 RoboStock\n거래량 블록 기반 장기투자 분석 플랫폼")
        welcome_font = QFont("Poppins", 32)
        welcome_font.setBold(True)
        welcome.setFont(welcome_font)
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")

        layout.addStretch()
        layout.addWidget(welcome)
        layout.addStretch()

        colors = theme_manager.colors
        panel.setStyleSheet(f"""
            #welcome_panel {{
                background: {colors['bg_layer_1']};
            }}
        """)

        return panel

    def _connect_signals(self):
        """시그널 연결"""
        # 패널 변경 시그널
        global_signals.panel_changed.connect(self._on_panel_changed)

        # 블록 탐지 시그널
        self.block_detector_panel.detection_started.connect(
            lambda: global_signals.block_detection_started.emit()
        )
        self.block_detector_panel.detection_finished.connect(
            lambda count: global_signals.block_detection_finished.emit(True, count)
        )


    def _create_status_bar(self) -> QWidget:
        """상태바 생성"""
        status_bar = QFrame()
        status_bar.setFixedHeight(UI_CONFIG['statusbar_height'])
        status_bar.setObjectName("status_bar")

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(16, 0, 16, 0)

        # 상태 정보
        status_label = QLabel("⚡ 시스템: 정상 | 📊 DB: 연결 대기 | 🔗 API: 준비")
        status_label.setFont(QFont("Inter", 11))
        layout.addWidget(status_label)

        layout.addStretch()

        colors = theme_manager.colors
        status_bar.setStyleSheet(f"""
            #status_bar {{
                background: {colors['bg_layer_2']};
                border-top: 1px solid {colors['border']};
                color: {colors['text_secondary']};
            }}
        """)

        return status_bar

    def _apply_theme(self):
        """테마 적용"""
        # 전역 스타일시트는 이미 app에 적용되어 있음
        # 개별 위젯 스타일은 각 위젯 생성 시 적용됨
        colors = theme_manager.colors
        self.main_canvas.setStyleSheet(f"""
            #main_canvas {{
                background: {colors['bg_layer_1']};
            }}
        """)

    def _on_panel_changed(self, panel_type: str):
        """패널 변경 핸들러"""
        panel_map = {
            PanelType.DATA_COLLECTION: self.data_collection_panel,
            PanelType.BLOCK_DETECTOR: self.block_detector_panel,
            PanelType.CHART_VIEWER: self.chart_viewer_panel,
        }

        panel = panel_map.get(panel_type)
        if panel:
            self.main_canvas.setCurrentWidget(panel)

    def closeEvent(self, event):
        """윈도우 종료 이벤트 처리"""
        print("[DEBUG] MainWindow closeEvent triggered")

        # 데이터 수집 워커 정리
        if hasattr(self.data_collection_panel, 'worker'):
            worker = self.data_collection_panel.worker
            if worker and worker.isRunning():
                print("[DEBUG] Stopping data collection worker...")
                worker.stop()
                worker.wait(500)  # 최대 0.5초 대기 (빠른 종료)
                if worker.isRunning():
                    print("[DEBUG] Force terminating data worker...")
                    worker.terminate()  # 강제 종료

        # 블록 탐지 워커 정리
        if hasattr(self.block_detector_panel, 'worker'):
            worker = self.block_detector_panel.worker
            if worker and worker.isRunning():
                print("[DEBUG] Stopping block detection worker...")
                worker.stop()
                worker.wait(500)  # 최대 0.5초 대기
                if worker.isRunning():
                    print("[DEBUG] Force terminating block worker...")
                    worker.terminate()

        print("[DEBUG] closeEvent complete")
        event.accept()
