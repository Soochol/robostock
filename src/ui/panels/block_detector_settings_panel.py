"""
Block Detector Settings Panel (VS Code Style)
블록 탐지 설정 패널 - VS Code Settings 스타일
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QSplitter, QFrame, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont

from datetime import datetime
from styles.theme import theme_manager
from core.config import SPACING, DATA_COLLECTION, DATA_DIR
from core.settings_manager import SettingsManager
from resources.icons import get_primary_icon, get_menu_icon, get_status_icon
from ui.widgets.settings import (
    ParameterSlider,
    CollapsibleSection,
    SettingItem
)
from ui.widgets.settings.block1_settings_section import Block1SettingsSection
from ui.widgets.settings.block2_settings_section import Block2SettingsSection
from ui.widgets.settings.block_diagram_widget import BlockDiagramWidget
from ui.widgets.common.gradient_progress_bar import GradientProgressBar
from ui.widgets.common.toast_notification import (
    show_success, show_error, show_info, show_warning, get_toast_manager
)
from ui.widgets.common.interactive_button import InteractiveButton
from ui.workers.block_detection_worker import BlockDetectionWorker
from infrastructure.database import get_session
from infrastructure.database.models import PriceData


class BlockDetectorSettingsPanel(QWidget):
    """
    블록 탐지 설정 패널 (VS Code Style)

    Layout:
    - 상단: 제목 + 액션 버튼
    - 중앙: 2-Column (설정 패널 | 미리보기 패널)
    - 하단: 상태 바
    """

    detection_started = Signal()
    detection_finished = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

        # 설정 관리자 초기화
        self.settings_manager = SettingsManager(
            DATA_DIR / "block_detector_settings.json"
        )

        self._setup_ui()

        # UI 생성 후 저장된 설정 복원
        self._load_saved_settings()

        # Toast manager 초기화
        get_toast_manager(self)

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더
        header = self._create_header()
        layout.addWidget(header)

        # 진행률 섹션 (검색창 위치에 배치)
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(24, 16, 24, 16)
        self.progress_section = self._create_progress_section()
        self.progress_section.setVisible(False)  # 초기 숨김
        progress_layout.addWidget(self.progress_section)
        layout.addWidget(progress_container)

        # 구분선
        separator = self._create_separator()
        layout.addWidget(separator)

        # 2-Column 레이아웃 (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {theme_manager.colors['border']};
            }}
        """)

        # 좌측: 설정 패널
        settings_panel = self._create_settings_panel()
        splitter.addWidget(settings_panel)

        # 우측: 미리보기 패널
        preview_panel = self._create_preview_panel()
        splitter.addWidget(preview_panel)

        # 초기 비율 설정 (60:40)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter, stretch=1)

        # 하단 상태 바
        status_bar = self._create_status_bar()
        layout.addWidget(status_bar)

    def _create_header(self) -> QWidget:
        """헤더 생성"""
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet(f"""
            #header {{
                background: {theme_manager.colors['bg_layer_2']};
                border-bottom: 1px solid {theme_manager.colors['border']};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        # 제목
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setPixmap(get_menu_icon('settings', 20).pixmap(QSize(20, 20)))
        title_layout.addWidget(icon_label)

        title_label = QLabel("블록 탐지 설정")
        title_font = QFont("Inter", 20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        title_layout.addWidget(title_label)

        layout.addWidget(title_container)
        layout.addStretch()

        # 액션 버튼들
        # 프리셋 버튼
        preset_btn = QPushButton("  프리셋")
        preset_btn.setIcon(get_menu_icon('save', 18))
        preset_btn.setIconSize(QSize(18, 18))
        preset_btn.setFixedHeight(44)
        self._style_action_button(preset_btn)
        layout.addWidget(preset_btn)

        # 초기화 버튼
        reset_btn = QPushButton("  초기화")
        reset_btn.setIcon(get_menu_icon('refresh-cw', 18))
        reset_btn.setIconSize(QSize(18, 18))
        reset_btn.setFixedHeight(44)
        reset_btn.clicked.connect(self._on_reset)
        self._style_action_button(reset_btn)
        layout.addWidget(reset_btn)

        # 탐지 시작 버튼
        self.start_btn = QPushButton("  탐지 시작")
        self.start_btn.setIcon(get_primary_icon('play', 18))
        self.start_btn.setIconSize(QSize(18, 18))
        self.start_btn.setFixedHeight(44)
        self.start_btn.clicked.connect(self._on_start_detection)
        self._style_primary_button(self.start_btn)
        layout.addWidget(self.start_btn)

        return header

    def _create_separator(self) -> QWidget:
        """구분선 생성"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"""
            background: {theme_manager.colors['border']};
            max-height: 1px;
        """)
        return separator

    def _create_settings_panel(self) -> QWidget:
        """설정 패널 생성 (좌측)"""
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {theme_manager.colors['bg_layer_1']};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme_manager.colors['bg_layer_1']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {theme_manager.colors['bg_layer_3']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme_manager.colors['primary_subtle']};
            }}
        """)

        # 컨텐츠
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 기간 선택 섹션
        period_section = CollapsibleSection("탐지 기간 선택", icon="📅", expanded=True)
        period_content = QWidget()
        period_layout = QVBoxLayout(period_content)
        period_layout.setContentsMargins(16, 8, 16, 8)
        period_layout.setSpacing(8)

        # 시작일
        start_label = QLabel("시작일")
        start_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        period_layout.addWidget(start_label)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(DATA_COLLECTION['start_year'], 1, 1))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self._on_date_changed)
        period_layout.addWidget(self.start_date)

        # 종료일
        end_label = QLabel("종료일")
        end_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        period_layout.addWidget(end_label)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate(DATA_COLLECTION['end_year'], 10, 8))
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self._on_date_changed)
        period_layout.addWidget(self.end_date)

        period_section.add_widget(period_content)
        layout.addWidget(period_section)

        # 1번 블록 조건 섹션
        self.block1_section = Block1SettingsSection()
        self.block1_section.settingsChanged.connect(self._on_settings_changed)
        layout.addWidget(self.block1_section)

        # 2번 블록 조건 섹션
        self.block2_section = Block2SettingsSection()
        self.block2_section.settingsChanged.connect(self._on_settings_changed)
        layout.addWidget(self.block2_section)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_preview_panel(self) -> QWidget:
        """미리보기 패널 생성 (우측)"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            background: {theme_manager.colors['bg_layer_1']};
            border-left: 1px solid {theme_manager.colors['border']};
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 타이틀 컨테이너
        title_container = QWidget()
        title_layout_preview = QHBoxLayout(title_container)
        title_layout_preview.setContentsMargins(0, 0, 0, 0)
        title_layout_preview.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(get_primary_icon('bar-chart', 14).pixmap(QSize(14, 14)))
        title_layout_preview.addWidget(title_icon)

        title = QLabel("현재 설정 요약")
        title_layout_preview.addWidget(title)
        title_layout_preview.addStretch()
        title_font = QFont("Inter", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        layout.addWidget(title_container)

        # 블록 다이어그램 위젯
        self.diagram_widget = BlockDiagramWidget()
        self.diagram_widget.setMinimumHeight(600)
        layout.addWidget(self.diagram_widget)

        layout.addStretch()

        return panel

    def _create_progress_section(self) -> QWidget:
        """진행률 섹션"""
        section = QFrame()
        section.setObjectName("progress_section")
        section.setStyleSheet(f"""
            #progress_section {{
                background: {theme_manager.colors['bg_glass']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(section)
        layout.setSpacing(SPACING['md'])

        # 섹션 제목 컨테이너
        title_container_progress = QWidget()
        title_layout_progress = QHBoxLayout(title_container_progress)
        title_layout_progress.setContentsMargins(0, 0, 0, 0)
        title_layout_progress.setSpacing(8)

        title_icon_progress = QLabel()
        title_icon_progress.setPixmap(get_status_icon('zap', 14).pixmap(QSize(14, 14)))
        title_layout_progress.addWidget(title_icon_progress)

        title = QLabel("실시간 진행률")
        title_layout_progress.addWidget(title)
        title_layout_progress.addStretch()
        title_font = QFont("Inter", 14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title_container_progress)

        # 프로그레스 바
        self.progress_bar = GradientProgressBar()
        layout.addWidget(self.progress_bar)

        # 상태 정보
        self.progress_status_label = QLabel("현재: 초기화 중...")
        self.progress_status_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        layout.addWidget(self.progress_status_label)

        self.progress_count_label = QLabel("탐지: 0개 종목")
        self.progress_count_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        layout.addWidget(self.progress_count_label)

        return section

    def _create_status_bar(self) -> QWidget:
        """하단 상태 바"""
        status_bar = QWidget()
        status_bar.setObjectName("status_bar")
        status_bar.setStyleSheet(f"""
            #status_bar {{
                background: {theme_manager.colors['bg_layer_2']};
                border-top: 1px solid {theme_manager.colors['border']};
            }}
        """)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(24, 12, 24, 12)

        # 상태 텍스트
        self.status_label = QLabel("예상 소요 시간: 계산 중...")
        self.status_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 통계
        stats_label = QLabel("마지막 저장: - | 설정 변경: 0회")
        stats_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_tertiary']};
            font-size: 11px;
        """)
        layout.addWidget(stats_label)

        return status_bar

    def _style_action_button(self, button: QPushButton):
        """액션 버튼 스타일"""
        button.setStyleSheet(f"""
            QPushButton {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_primary']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['bg_layer_3']};
                border-color: {theme_manager.colors['primary']};
            }}
            QPushButton:pressed {{
                background: {theme_manager.colors['primary_subtle']};
            }}
        """)

    def _style_primary_button(self, button: QPushButton):
        """주요 버튼 스타일"""
        button.setStyleSheet(f"""
            QPushButton {{
                background: {theme_manager.colors['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background: {theme_manager.colors['primary']};
                padding: 9px 19px 7px 21px;
            }}
        """)

    def _load_saved_settings(self):
        """저장된 설정 불러와서 UI에 적용"""
        saved = self.settings_manager.load_settings()

        # 기간 설정 복원
        if 'period' in saved:
            self.start_date.setDate(QDate(
                saved['period']['start_year'],
                saved['period']['start_month'],
                saved['period']['start_day']
            ))
            self.end_date.setDate(QDate(
                saved['period']['end_year'],
                saved['period']['end_month'],
                saved['period']['end_day']
            ))

        # 블록 설정 복원
        if 'block1' in saved:
            self.block1_section.apply_settings(saved['block1'])
        if 'block2' in saved:
            self.block2_section.apply_settings(saved['block2'])

    def _auto_save_settings(self):
        """현재 설정을 자동으로 저장"""
        current_settings = {
            'block1': self.block1_section.get_settings(),
            'block2': self.block2_section.get_settings(),
            'period': {
                'start_year': self.start_date.date().year(),
                'start_month': self.start_date.date().month(),
                'start_day': self.start_date.date().day(),
                'end_year': self.end_date.date().year(),
                'end_month': self.end_date.date().month(),
                'end_day': self.end_date.date().day(),
            }
        }

        self.settings_manager.save_settings(current_settings)
        print("[DEBUG] Settings auto-saved")

    def _on_reset(self):
        """설정 초기화"""
        print("[DEBUG] Reset settings")

        # 기본값으로 초기화
        default_settings = self.settings_manager.reset_settings()

        # UI에 적용
        if 'period' in default_settings:
            self.start_date.setDate(QDate(
                default_settings['period']['start_year'],
                default_settings['period']['start_month'],
                default_settings['period']['start_day']
            ))
            self.end_date.setDate(QDate(
                default_settings['period']['end_year'],
                default_settings['period']['end_month'],
                default_settings['period']['end_day']
            ))

        if 'block1' in default_settings:
            self.block1_section.apply_settings(default_settings['block1'])
        if 'block2' in default_settings:
            self.block2_section.apply_settings(default_settings['block2'])

    def _on_settings_changed(self, settings: dict):
        """설정 변경 시"""
        print(f"[DEBUG] Settings changed: {len(settings)} items")

        # 다이어그램 업데이트
        block1_settings = self.block1_section.get_settings()
        block2_settings = self.block2_section.get_settings()
        self.diagram_widget.update_settings(block1_settings, block2_settings)

        # 자동 저장
        self._auto_save_settings()

    def _on_date_changed(self):
        """날짜 변경 시"""
        self._auto_save_settings()

    def _on_start_detection(self):
        """탐지 시작/중지 토글"""
        # 이미 실행 중이면 중지
        if self.worker and self.worker.isRunning():
            print("[DEBUG] Stop detection")
            self.worker.stop()
            self.start_btn.setText("탐지 시작")
            self.start_btn.setIcon(get_primary_icon('play', 16))
            self.status_label.setText("사용자가 탐지를 중지했습니다.")
            return

        print("[DEBUG] Start detection")

        # 설정 수집
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        block1_settings = self.block1_section.get_settings()
        block2_settings = self.block2_section.get_settings()

        # 통합 settings dict 생성
        settings = {}
        settings.update(block1_settings)
        settings.update(block2_settings)

        print(f"[DEBUG] Date range: {start_date} to {end_date}")
        print(f"[DEBUG] Combined settings: {settings}")

        # 데이터 존재 여부 확인
        with get_session() as session:
            start_dt = datetime.combine(start_date.toPython(), datetime.min.time())
            end_dt = datetime.combine(end_date.toPython(), datetime.max.time())

            price_count = session.query(PriceData).filter(
                PriceData.date >= start_dt,
                PriceData.date <= end_dt
            ).count()

            print(f"[DEBUG] Found {price_count} price data records in date range")

            if price_count == 0:
                self.status_label.setText("에러: 선택한 기간에 데이터가 없습니다.")
                show_error("선택한 기간에 데이터가 없습니다.")
                return

        # 진행률 섹션 표시
        self.progress_section.setVisible(True)

        # 버튼 상태 변경
        self.start_btn.setText("탐지 중지")
        self.start_btn.setIcon(get_status_icon('pause', 16))

        # 시작 시그널 발행
        self.detection_started.emit()

        # UI 초기화
        self.progress_bar.set_progress(0)
        self.progress_status_label.setText("현재: 탐지 시작...")
        self.progress_count_label.setText("탐지: 0개 종목")

        # Worker 생성 및 시작
        self.worker = BlockDetectionWorker(
            start_date=start_date,
            end_date=end_date,
            market_filter=None,
            settings=settings  # 커스텀 설정 전달
        )
        print("[DEBUG] Worker created with custom settings")

        # 시그널 연결
        self.worker.progress.connect(self._on_progress)
        self.worker.stock_completed.connect(self._on_stock_completed)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        print("[DEBUG] Signals connected")

        # Worker 시작
        self.worker.start()
        print("[DEBUG] Worker started")

    def _on_progress(self, current: int, total: int, message: str):
        """진행률 업데이트"""
        print(f"[DEBUG] Progress: {current}/{total} - {message}")
        if total > 0:
            progress_percent = int((current / total) * 100)
            self.progress_bar.set_progress(progress_percent)

        self.progress_status_label.setText(f"현재: {message}")
        self.progress_count_label.setText(f"진행: {current}/{total} 종목")

    def _on_stock_completed(self, stock_name: str, blocks_1: int, blocks_2: int):
        """종목 탐지 완료"""
        print(f"[DEBUG] Stock completed: {stock_name} B1={blocks_1} B2={blocks_2}")
        # 결과 테이블이 있으면 추가 (Phase 8)

    def _on_finished(self, success: bool, total_blocks_1: int, total_blocks_2: int):
        """탐지 완료"""
        print(f"[DEBUG] Finished: success={success} B1={total_blocks_1} B2={total_blocks_2}")
        self.start_btn.setText("탐지 시작")
        self.start_btn.setIcon(get_primary_icon('play', 16))

        if success:
            self.progress_status_label.setText(f"현재: 탐지 완료!")
            self.progress_count_label.setText(
                f"탐지: 1번 블록 {total_blocks_1}개, 2번 블록 {total_blocks_2}개"
            )
            self.progress_bar.set_progress(100)
            self.status_label.setText(f"탐지 완료: 1번 블록 {total_blocks_1}개, 2번 블록 {total_blocks_2}개")
            # Toast 알림
            show_success(f"탐지 완료! 1번 블록 {total_blocks_1}개, 2번 블록 {total_blocks_2}개 발견")
        else:
            self.progress_status_label.setText("현재: 탐지 중지됨")
            self.status_label.setText("탐지 중지됨")
            show_info("탐지가 중지되었습니다.")

        # 진행률 섹션 숨기기
        self.progress_section.setVisible(False)

        self.detection_finished.emit(total_blocks_1 + total_blocks_2)

    def _on_error(self, error_message: str):
        """에러 발생"""
        print(f"[DEBUG] Error: {error_message}")
        self.progress_status_label.setText(f"에러: {error_message}")
        self.status_label.setText(f"에러: {error_message}")
        self.start_btn.setText("탐지 시작")
        self.start_btn.setIcon(get_primary_icon('play', 16))
        # 진행률 섹션 숨기기
        self.progress_section.setVisible(False)
        # Toast 에러 알림
        show_error(f"에러 발생: {error_message}")
