"""
Block Detector Panel
블록 탐지 패널 - 카드 기반 3-Step UI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QPushButton, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QFrame, QSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QFont, QFontDatabase

from core.config import BLOCK_CRITERIA, DATA_COLLECTION, SPACING, ICONS
from styles.typography import FONT_SIZES
from core.enums import BlockType
from styles.theme import theme_manager
from resources.icons import IconManager, get_menu_icon, get_primary_icon, get_status_icon
from ui.widgets.common.gradient_progress_bar import GradientProgressBar
from ui.widgets.common.glass_card import GlassCard
from ui.widgets.common.step_progress import StepProgressWidget
from ui.workers.block_detection_worker import BlockDetectionWorker
from infrastructure.database import get_session
from infrastructure.database.models import PriceData


class BlockDetectorPanel(QWidget):
    """
    블록 탐지 패널

    구조:
    - 3-Step 카드: 기간 선택 → 조건 설정 → 실행
    - 실시간 진행률
    - 탐지 결과 테이블
    """

    detection_started = Signal()
    detection_finished = Signal(int)  # total_cases

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        layout.setSpacing(SPACING['lg'])

        # 헤더
        header = self._create_header()
        layout.addWidget(header)

        # 3-Step 카드
        step_cards = self._create_step_cards()
        layout.addWidget(step_cards)

        # 진행률
        self.progress_section = self._create_progress_section()
        self.progress_section.setVisible(False)  # 초기 숨김
        layout.addWidget(self.progress_section)

        # 결과 테이블
        self.result_section = self._create_result_section()
        layout.addWidget(self.result_section, stretch=1)

    def _create_header(self) -> QWidget:
        """헤더 생성"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # 제목 (아이콘 + 텍스트)
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)

        # 검색 아이콘
        icon_label = QLabel()
        icon_label.setPixmap(get_primary_icon('search', 20).pixmap(QSize(20, 20)))
        title_layout.addWidget(icon_label)

        # 제목 텍스트
        title = QLabel("거래량 블록 탐지")
        title_font = QFont("Pretendard Variable", FONT_SIZES['h2'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title_layout.addWidget(title)

        layout.addWidget(title_container)
        layout.addStretch()

        # 고급 설정 버튼
        advanced_btn = QPushButton("  고급 설정")
        advanced_btn.setIcon(get_menu_icon('settings', 16))
        advanced_btn.setIconSize(QSize(16, 16))
        advanced_btn.setFixedWidth(120)
        layout.addWidget(advanced_btn)

        return header

    def _create_step_cards(self) -> QWidget:
        """3-Step 카드 레이아웃"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(SPACING['md'])

        # Step 1: 기간 선택
        step1 = self._create_step1_card()
        layout.addWidget(step1)

        # Step 2: 조건 설정
        step2 = self._create_step2_card()
        layout.addWidget(step2)

        # Step 3: 실행
        step3 = self._create_step3_card()
        layout.addWidget(step3)

        return container

    def _create_preset_buttons(self) -> QHBoxLayout:
        """프리셋 버튼 생성"""
        layout = QHBoxLayout()
        layout.setSpacing(SPACING['sm'])

        # 프리셋 데이터
        presets = [
            {
                "name": "최근 1년",
                "icon": "zap",
                "tooltip": "최근 1년 데이터 탐지",
            },
            {
                "name": "최근 3년",
                "icon": "database",
                "tooltip": "최근 3년 데이터 탐지",
            },
            {
                "name": "전체 기간",
                "icon": "hard-drive",
                "tooltip": "전체 기간 (10년) 탐지",
            },
        ]

        for preset in presets:
            btn = QPushButton(f"  {preset['name']}")
            btn.setIcon(get_primary_icon(preset['icon'], 14))
            btn.setIconSize(QSize(14, 14))
            btn.setFont(QFont("Pretendard Variable", FONT_SIZES['small']))
            btn.setFixedHeight(36)
            btn.setToolTip(preset['tooltip'])
            btn.clicked.connect(
                lambda checked, p=preset['name']: self._apply_preset(p)
            )
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {theme_manager.colors['bg_layer_2']};
                    color: {theme_manager.colors['text_secondary']};
                    border: 1px solid {theme_manager.colors['border']};
                    border-radius: 6px;
                    padding: 0 {SPACING['md']}px;
                }}
                QPushButton:hover {{
                    background: {theme_manager.colors['bg_layer_3']};
                    border-color: {theme_manager.colors['primary']};
                    color: {theme_manager.colors['primary']};
                }}
                QPushButton:pressed {{
                    background: {theme_manager.colors['bg_layer_1']};
                }}
            """)
            layout.addWidget(btn)

        layout.addStretch()
        return layout

    def _apply_preset(self, preset_name: str):
        """프리셋 적용"""
        from datetime import date

        if preset_name == "최근 1년":
            self.start_date.setDate(QDate(date.today().year - 1, 1, 1))
            self.end_date.setDate(QDate.currentDate())
        elif preset_name == "최근 3년":
            self.start_date.setDate(QDate(date.today().year - 3, 1, 1))
            self.end_date.setDate(QDate.currentDate())
        elif preset_name == "전체 기간":
            self.start_date.setDate(QDate(DATA_COLLECTION['start_year'], 1, 1))
            self.end_date.setDate(QDate(DATA_COLLECTION['end_year'], 10, 8))

    def _create_step1_card(self) -> QWidget:
        """Step 1: 기간 선택 카드"""
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        layout.setSpacing(SPACING['md'])

        # 카드 제목
        title = QLabel("1. 기간 선택")
        title_font = QFont("Pretendard Variable", FONT_SIZES['body_large'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)

        # 프리셋 버튼
        preset_layout = self._create_preset_buttons()
        layout.addLayout(preset_layout)

        # 시작일
        start_label = QLabel("시작일")
        start_label.setFont(QFont("Pretendard Variable", FONT_SIZES['body']))
        start_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        layout.addWidget(start_label)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(DATA_COLLECTION['start_year'], 1, 1))
        self.start_date.setCalendarPopup(True)
        layout.addWidget(self.start_date)

        # 화살표
        arrow = QLabel("↓")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setFont(QFont("Pretendard Variable", FONT_SIZES['body_large']))
        layout.addWidget(arrow)

        # 종료일
        end_label = QLabel("종료일")
        end_label.setFont(QFont("Pretendard Variable", FONT_SIZES['body']))
        end_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        layout.addWidget(end_label)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate(DATA_COLLECTION['end_year'], 10, 8))
        self.end_date.setCalendarPopup(True)
        layout.addWidget(self.end_date)

        # 기간 표시
        period_label = QLabel("10년 9개월")
        period_label.setAlignment(Qt.AlignCenter)
        period_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 13px;
            margin-top: 8px;
        """)
        layout.addWidget(period_label)

        # 빠른 선택
        quick_select = QPushButton("빠른선택 ▼")
        quick_select.setFont(QFont("Pretendard Variable", FONT_SIZES['body_small']))
        quick_select.setStyleSheet(f"""
            QPushButton {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_primary']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: {FONT_SIZES['body_small']}px;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['primary_subtle']};
                border-color: {theme_manager.colors['primary']};
            }}
        """)
        layout.addWidget(quick_select)

        layout.addStretch()

        return card

    def _create_step2_card(self) -> QWidget:
        """Step 2: 조건 설정 카드"""
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        layout.setSpacing(SPACING['md'])

        # 카드 제목
        title = QLabel("2. 조건 설정")
        title_font = QFont("Pretendard Variable", FONT_SIZES['body_large'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)

        # 1번 블록 조건
        block1_label = QLabel("1번 블록:")
        block1_label.setFont(QFont("Pretendard Variable", FONT_SIZES['body']))
        block1_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: {FONT_SIZES['body']}px;
            font-weight: 600;
        """)
        layout.addWidget(block1_label)

        checkbox_font = QFont("Pretendard Variable", FONT_SIZES['body'])

        self.cb_2y_max = QCheckBox("2년래 최대 거래량")
        self.cb_2y_max.setFont(checkbox_font)
        self.cb_2y_max.setChecked(True)
        layout.addWidget(self.cb_2y_max)

        # 거래대금 조건 (입력 가능)
        trading_value_container = QWidget()
        trading_value_layout = QHBoxLayout(trading_value_container)
        trading_value_layout.setContentsMargins(0, 0, 0, 0)
        trading_value_layout.setSpacing(8)

        self.cb_trading_value = QCheckBox("거래대금 ")
        self.cb_trading_value.setFont(checkbox_font)
        self.cb_trading_value.setChecked(True)
        trading_value_layout.addWidget(self.cb_trading_value)

        self.trading_value_input = QSpinBox()
        self.trading_value_input.setRange(1, 100000)
        self.trading_value_input.setValue(500)
        self.trading_value_input.setSuffix("백만")
        self.trading_value_input.setFixedWidth(120)
        self.trading_value_input.setFont(QFont("Pretendard Variable", FONT_SIZES['body_small']))
        trading_value_layout.addWidget(self.trading_value_input)

        trading_value_label = QLabel("원 이상")
        trading_value_label.setFont(checkbox_font)
        trading_value_label.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        trading_value_layout.addWidget(trading_value_label)

        trading_value_layout.addStretch()
        layout.addWidget(trading_value_container)

        # N개월 신고가 조건
        new_high_container = QWidget()
        new_high_layout = QHBoxLayout(new_high_container)
        new_high_layout.setContentsMargins(0, 0, 0, 0)
        new_high_layout.setSpacing(8)

        self.cb_new_high_1 = QCheckBox("")
        self.cb_new_high_1.setFont(checkbox_font)
        new_high_layout.addWidget(self.cb_new_high_1)

        self.new_high_months = QSpinBox()
        self.new_high_months.setRange(1, 60)
        self.new_high_months.setValue(24)
        self.new_high_months.setSuffix("개월")
        self.new_high_months.setFixedWidth(100)
        self.new_high_months.setFont(QFont("Pretendard Variable", FONT_SIZES['body_small']))
        new_high_layout.addWidget(self.new_high_months)

        new_high_label = QLabel("신고가 포함")
        new_high_label.setFont(checkbox_font)
        new_high_label.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        new_high_layout.addWidget(new_high_label)

        new_high_layout.addStretch()
        layout.addWidget(new_high_container)

        # 2번 블록 조건
        block2_label = QLabel("2번 블록:")
        block2_label.setFont(QFont("Pretendard Variable", FONT_SIZES['body']))
        block2_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: {FONT_SIZES['body']}px;
            font-weight: 600;
            margin-top: 12px;
        """)
        layout.addWidget(block2_label)

        self.cb_80_percent = QCheckBox("80% 이상 거래량")
        self.cb_80_percent.setFont(checkbox_font)
        self.cb_80_percent.setChecked(True)
        layout.addWidget(self.cb_80_percent)

        self.cb_6_months = QCheckBox("6개월 이내 발생")
        self.cb_6_months.setFont(checkbox_font)
        self.cb_6_months.setChecked(True)
        layout.addWidget(self.cb_6_months)

        self.cb_pattern = QCheckBox("패턴 매칭 (D+D+1+D+2)")
        self.cb_pattern.setFont(checkbox_font)
        self.cb_pattern.setChecked(True)
        layout.addWidget(self.cb_pattern)

        # 2번 블록 거래대금 조건 (입력 가능)
        trading_value_2_container = QWidget()
        trading_value_2_layout = QHBoxLayout(trading_value_2_container)
        trading_value_2_layout.setContentsMargins(0, 0, 0, 0)
        trading_value_2_layout.setSpacing(8)

        self.cb_trading_value_2 = QCheckBox("거래대금 ")
        self.cb_trading_value_2.setFont(checkbox_font)
        self.cb_trading_value_2.setChecked(True)
        trading_value_2_layout.addWidget(self.cb_trading_value_2)

        self.trading_value_2_input = QSpinBox()
        self.trading_value_2_input.setRange(1, 1000000)
        self.trading_value_2_input.setValue(2000)
        self.trading_value_2_input.setSuffix("백만")
        self.trading_value_2_input.setFixedWidth(120)
        self.trading_value_2_input.setFont(QFont("Pretendard Variable", FONT_SIZES['body_small']))
        trading_value_2_layout.addWidget(self.trading_value_2_input)

        trading_value_2_label = QLabel("원 이상 (중 1일)")
        trading_value_2_label.setFont(checkbox_font)
        trading_value_2_label.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        trading_value_2_layout.addWidget(trading_value_2_label)

        trading_value_2_layout.addStretch()
        layout.addWidget(trading_value_2_container)

        layout.addStretch()

        return card

    def _create_step3_card(self) -> QWidget:
        """Step 3: 실행 카드"""
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        layout.setSpacing(SPACING['md'])

        # 카드 제목
        title = QLabel("3. 실행")
        title_font = QFont("Pretendard Variable", FONT_SIZES['body_large'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        # 시작 버튼
        self.start_btn = QPushButton("  탐지 시작")
        self.start_btn.setIcon(get_primary_icon('search', 20))
        self.start_btn.setIconSize(QSize(20, 20))
        btn_font = QFont("Pretendard Variable", FONT_SIZES['body'])
        btn_font.setWeight(QFont.Weight.DemiBold)
        self.start_btn.setFont(btn_font)
        self.start_btn.setMinimumHeight(60)
        self.start_btn.clicked.connect(self._on_start_detection)
        layout.addWidget(self.start_btn)

        # 중지 버튼
        self.stop_btn = QPushButton("  중지")
        self.stop_btn.setIcon(get_status_icon('x-circle', 20))
        self.stop_btn.setIconSize(QSize(20, 20))
        self.stop_btn.setFont(btn_font)
        self.stop_btn.setMinimumHeight(60)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_detection)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme_manager.colors['error']};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {theme_manager.colors['error_hover']};
            }}
            QPushButton:disabled {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_disabled']};
            }}
        """)
        layout.addWidget(self.stop_btn)

        # 예상 정보
        info_label = QLabel("예상 소요 시간:\n약 3~5분")
        info_label.setFont(QFont("Pretendard Variable", FONT_SIZES['caption']))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: {FONT_SIZES['caption']}px;
            margin-top: 8px;
        """)
        layout.addWidget(info_label)

        layout.addStretch()

        return card

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

        # 섹션 제목
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(get_status_icon('info', 18).pixmap(QSize(18, 18)))
        title_layout.addWidget(title_icon)

        title = QLabel("실시간 진행률")
        title_font = QFont("Pretendard Variable", FONT_SIZES['h3'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addWidget(title_container)

        # 단계별 진행 표시
        self.step_progress = StepProgressWidget()
        self.step_progress.set_steps([
            "1. 종목 리스트 로드",
            "2. 1번 블록 탐지",
            "3. 2번 블록 탐지",
            "4. 결과 정리"
        ])
        layout.addWidget(self.step_progress)

        # 프로그레스 바
        self.progress_bar = GradientProgressBar()
        self.progress_bar.setFixedHeight(40)
        layout.addWidget(self.progress_bar)

        # 현재 작업 및 통계 정보 (1줄로 압축)
        info_layout = QHBoxLayout()
        info_font = QFont("Pretendard Variable", FONT_SIZES['body_small'])

        self.status_label = QLabel("대기 중...")
        self.status_label.setFont(info_font)
        self.status_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        info_layout.addWidget(self.status_label)

        info_layout.addStretch()

        # 통계 레이블들
        self.total_stocks_label = QLabel("총 종목: 0")
        self.total_stocks_label.setFont(info_font)
        self.total_stocks_label.setStyleSheet(f"color: {theme_manager.colors['text_tertiary']};")
        info_layout.addWidget(self.total_stocks_label)

        self.completed_stocks_label = QLabel("완료: 0")
        self.completed_stocks_label.setFont(info_font)
        self.completed_stocks_label.setStyleSheet(f"color: {theme_manager.colors['success']};")
        info_layout.addWidget(self.completed_stocks_label)

        self.found_blocks_label = QLabel("발견: 0블록")
        self.found_blocks_label.setFont(info_font)
        self.found_blocks_label.setStyleSheet(f"color: {theme_manager.colors['primary']};")
        info_layout.addWidget(self.found_blocks_label)

        self.eta_label = QLabel("예상 완료: 계산 중...")
        self.eta_label.setFont(info_font)
        self.eta_label.setStyleSheet(f"color: {theme_manager.colors['text_tertiary']};")
        info_layout.addWidget(self.eta_label)

        layout.addLayout(info_layout)

        return section

    def _create_result_section(self) -> QWidget:
        """결과 섹션"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])

        # 섹션 제목
        header_layout = QHBoxLayout()

        # 제목 (아이콘 + 텍스트)
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(get_menu_icon('folder', 18).pixmap(QSize(18, 18)))
        title_layout.addWidget(title_icon)

        title = QLabel("탐지 결과 (최근 10개)")
        title_font = QFont("Pretendard Variable", FONT_SIZES['h3'])
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title_layout.addWidget(title)

        header_layout.addWidget(title_container)
        header_layout.addStretch()

        # 내보내기 버튼
        export_btn = QPushButton("  CSV 내보내기")
        export_btn.setIcon(get_menu_icon('save', 16))
        export_btn.setIconSize(QSize(16, 16))
        export_btn.setFixedWidth(150)
        header_layout.addWidget(export_btn)

        layout.addLayout(header_layout)

        # 테이블
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels([
            "No", "종목명", "1번일", "2번일", "Level", "성공률"
        ])

        # 테이블 스타일
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 샘플 데이터 추가
        self._add_sample_data()

        layout.addWidget(self.result_table)

        # 전체 보기 버튼
        view_all_btn = QPushButton("  전체 결과 보기 (487개)")
        view_all_btn.setIcon(get_menu_icon('bar-chart', 16))
        view_all_btn.setIconSize(QSize(16, 16))
        layout.addWidget(view_all_btn)

        return section

    def _add_sample_data(self):
        """샘플 데이터 추가"""
        sample_data = [
            ("487", "삼성전자", "03-15", "08-20", "🥇", "78%"),
            ("486", "SK하이닉스", "02-10", "07-15", "🥈", "65%"),
            ("485", "LG에너지솔루션", "01-20", "06-25", "🏆", "92%"),
        ]

        self.result_table.setRowCount(len(sample_data))

        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(row, col, item)

    def _on_start_detection(self):
        """탐지 시작"""
        print("[DEBUG] _on_start_detection called")

        # 설정 가져오기
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        print(f"[DEBUG] Date range: {start_date} to {end_date}")

        # 데이터 존재 여부 확인
        with get_session() as session:
            from datetime import datetime
            start_dt = datetime.combine(start_date.toPython(), datetime.min.time())
            end_dt = datetime.combine(end_date.toPython(), datetime.max.time())

            price_count = session.query(PriceData).filter(
                PriceData.date >= start_dt,
                PriceData.date <= end_dt
            ).count()

            print(f"[DEBUG] Found {price_count} price data records in date range")

            if price_count == 0:
                self.status_label.setText("에러: 선택한 기간에 데이터가 없습니다.")
                return

        # 진행률 섹션 표시
        self.progress_section.setVisible(True)

        # 버튼 상태 변경
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 시작 시그널 발행
        self.detection_started.emit()

        # UI 초기화
        self.progress_bar.set_progress(0, animate=False)
        self.status_label.setText("초기화 중...")
        self.total_stocks_label.setText("총 종목: 0")
        self.completed_stocks_label.setText("완료: 0")
        self.found_blocks_label.setText("발견: 0블록")
        self.eta_label.setText("예상 완료: 계산 중...")
        self.step_progress.reset()

        # 통계 초기화
        self.total_blocks_found = 0
        self.start_time = None

        # 1단계 시작: 종목 리스트 로드
        self.step_progress.update_step(0, "in_progress")

        # 결과 테이블 초기화
        self.result_table.setRowCount(0)

        # 설정 수집
        settings = {
            # 1번 블록 조건
            'block1': {
                'two_year_max': self.cb_2y_max.isChecked(),
                'min_trading_value': self.trading_value_input.value() * 1_000_000 if self.cb_trading_value.isChecked() else None,
                'new_high_months': self.new_high_months.value() if self.cb_new_high_1.isChecked() else None,
            },
            # 2번 블록 조건
            'block2': {
                'min_volume_ratio': 0.8 if self.cb_80_percent.isChecked() else None,
                'within_6_months': self.cb_6_months.isChecked(),
                'pattern_matching': self.cb_pattern.isChecked(),
                'min_trading_value': self.trading_value_2_input.value() * 1_000_000 if self.cb_trading_value_2.isChecked() else None,
            }
        }

        # Worker 생성 및 시작
        self.worker = BlockDetectionWorker(
            start_date=start_date,
            end_date=end_date,
            market_filter=None,  # 전체 시장
            settings=settings
        )
        print("[DEBUG] Worker created")

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
        print(f"[DEBUG] _on_progress: {current}/{total} - {message}")

        # 시작 시간 기록
        if self.start_time is None:
            import time
            self.start_time = time.time()

        if total > 0:
            progress_percent = int((current / total) * 100)
            self.progress_bar.set_progress(progress_percent, animate=True)

        self.status_label.setText(message)
        self.total_stocks_label.setText(f"총 종목: {total}")
        self.completed_stocks_label.setText(f"완료: {current}")
        self.found_blocks_label.setText(f"발견: {self.total_blocks_found}블록")

        # ETA 계산 (데이터 수집 패널과 동일한 로직)
        if self.start_time and current > 0 and total > 0:
            from datetime import datetime, timedelta
            import time

            elapsed = time.time() - self.start_time
            avg_time_per_stock = elapsed / current
            remaining_stocks = total - current
            remaining_seconds = remaining_stocks * avg_time_per_stock

            # 완료 예상 시간
            eta = datetime.now() + timedelta(seconds=remaining_seconds)

            # 포맷팅
            if remaining_seconds < 60:
                eta_str = f"약 {int(remaining_seconds)}초 후 완료"
            elif remaining_seconds < 3600:
                minutes = int(remaining_seconds // 60)
                eta_str = f"약 {minutes}분 후 완료 ({eta.strftime('%H:%M')})"
            else:
                hours = int(remaining_seconds // 3600)
                minutes = int((remaining_seconds % 3600) // 60)
                eta_str = f"약 {hours}시간 {minutes}분 후 완료 ({eta.strftime('%H:%M')})"

            self.eta_label.setText(f"예상 완료: {eta_str}")
        else:
            self.eta_label.setText("예상 완료: 계산 중...")

        # 단계 업데이트 로직
        self._update_step_from_message(message, current, total)

    def _update_step_from_message(self, message: str, current: int, total: int):
        """메시지 기반으로 단계 상태 업데이트"""
        count_text = f"({current}/{total})"

        if "종목" in message and "로드" in message:
            # 1단계: 종목 리스트 로드
            self.step_progress.update_step(0, "in_progress", count_text)
        elif "1번" in message or current < total * 0.5:
            # 1단계 완료, 2단계 진행 (1번 블록 탐지)
            self.step_progress.update_step(0, "completed")
            self.step_progress.update_step(1, "in_progress", count_text)
        elif "2번" in message or current >= total * 0.5:
            # 2단계 완료, 3단계 진행 (2번 블록 탐지)
            self.step_progress.update_step(1, "completed")
            self.step_progress.update_step(2, "in_progress", count_text)
        elif "완료" in message or current == total:
            # 3단계 완료, 4단계 진행 (결과 정리)
            self.step_progress.update_step(2, "completed")
            self.step_progress.update_step(3, "in_progress")

    def _on_stock_completed(self, stock_name: str, blocks_1: int, blocks_2: int):
        """종목 탐지 완료 - 결과 테이블에 추가"""
        print(f"[DEBUG] _on_stock_completed: {stock_name} B1={blocks_1} B2={blocks_2}")

        # 블록 카운터 업데이트
        self.total_blocks_found += blocks_1 + blocks_2
        self.found_blocks_label.setText(f"발견: {self.total_blocks_found}블록")

        if blocks_1 > 0:
            row_position = self.result_table.rowCount()
            self.result_table.insertRow(row_position)

            self.result_table.setItem(row_position, 0, QTableWidgetItem(stock_name))
            self.result_table.setItem(row_position, 1, QTableWidgetItem(str(blocks_1)))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(str(blocks_2)))
            self.result_table.setItem(row_position, 3, QTableWidgetItem("성공"))

    def _stop_detection(self):
        """탐지 중지"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("중지됨")

    def _on_finished(self, success: bool, total_blocks_1: int, total_blocks_2: int):
        """탐지 완료"""
        print(f"[DEBUG] _on_finished: success={success} B1={total_blocks_1} B2={total_blocks_2}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if success:
            self.status_label.setText(f"탐지 완료!")
            self.progress_bar.set_progress(100, animate=True)
            # 모든 단계 완료
            self.step_progress.update_step(3, "completed")
        else:
            self.status_label.setText("탐지 중지됨")

        self.detection_finished.emit(total_blocks_1 + total_blocks_2)

    def _on_error(self, error_message: str):
        """에러 발생"""
        print(f"[DEBUG] _on_error: {error_message}")
        self.status_label.setText(f"에러: {error_message}")
        self.start_btn.setEnabled(True)

    def update_progress(self, progress: int, message: str):
        """진행률 업데이트"""
        self.progress_bar.set_progress(progress)
        self.status_label.setText(f"현재: {message}")
