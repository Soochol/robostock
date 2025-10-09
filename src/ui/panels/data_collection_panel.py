"""
Data Collection Panel
데이터 수집 패널
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QComboBox, QProgressBar, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QDate, QSize, Signal
from PySide6.QtGui import QFont
from datetime import datetime, timedelta
import time

from styles.theme import theme_manager
from styles.typography import FONT_SIZES
from core.config import SPACING, DATA_COLLECTION
from ui.widgets.common.glass_card import GlassCard
from ui.widgets.common.gradient_progress_bar import GradientProgressBar
from ui.widgets.common.step_progress import StepProgressWidget
from ui.workers.data_collection_worker import DataCollectionWorker
from resources.icons import get_primary_icon, get_status_icon, get_menu_icon


class DataCollectionPanel(QWidget):
    """
    데이터 수집 패널

    기능:
    - KOSPI/KOSDAQ 종목 리스트 수집
    - 일별 OHLCV 데이터 수집 (10년치)
    - 재무제표 데이터 수집 (DART)
    - 진행 상황 표시
    """

    collection_started = Signal()
    collection_finished = Signal(bool, int)  # (success, total_count)
    collection_progress = Signal(int, int, str)  # (current, total, message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.start_time = None  # 수집 시작 시간
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더
        header = self._create_header()
        layout.addWidget(header)

        # 진행률 섹션 (헤더 아래 배치, 초기 숨김)
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

        # 3-Step 카드
        step_cards = self._create_step_cards()
        layout.addWidget(step_cards)

        layout.addStretch()

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
        icon_label.setPixmap(get_primary_icon('download', 20).pixmap(QSize(20, 20)))
        title_layout.addWidget(icon_label)

        title_label = QLabel("데이터 수집")
        title_font = QFont("Inter", 20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme_manager.colors['text_primary']};")
        title_layout.addWidget(title_label)

        layout.addWidget(title_container)
        layout.addStretch()

        # 액션 버튼들
        # 프리셋 메뉴 버튼
        preset_btn = QPushButton("  프리셋")
        preset_btn.setIcon(get_menu_icon('save', 18))
        preset_btn.setIconSize(QSize(18, 18))
        preset_btn.setFixedHeight(44)
        preset_btn.clicked.connect(lambda: self._show_preset_menu())
        self._style_action_button(preset_btn)
        layout.addWidget(preset_btn)

        # 설정 초기화 버튼
        reset_btn = QPushButton("  초기화")
        reset_btn.setIcon(get_menu_icon('refresh-cw', 18))
        reset_btn.setIconSize(QSize(18, 18))
        reset_btn.setFixedHeight(44)
        reset_btn.clicked.connect(self._reset_to_defaults)
        self._style_action_button(reset_btn)
        layout.addWidget(reset_btn)

        # 수집 시작/중지 버튼
        self.start_btn = QPushButton("  수집 시작")
        self.start_btn.setIcon(get_primary_icon('play', 18))
        self.start_btn.setIconSize(QSize(18, 18))
        self.start_btn.setFixedHeight(44)
        self.start_btn.clicked.connect(self._start_collection)
        self._style_primary_button(self.start_btn)
        layout.addWidget(self.start_btn)

        return header

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
            QPushButton:disabled {{
                background: {theme_manager.colors['bg_layer_3']};
                color: {theme_manager.colors['text_disabled']};
            }}
        """)

    def _show_preset_menu(self):
        """프리셋 메뉴 표시"""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import QPoint

        menu = QMenu(self)
        menu.addAction("빠른 시작", lambda: self._apply_preset("빠른 시작"))
        menu.addAction("표준 수집", lambda: self._apply_preset("표준 수집"))
        menu.addAction("전체 수집", lambda: self._apply_preset("전체 수집"))
        menu.addAction("업데이트만", lambda: self._apply_preset("업데이트만"))

        # 버튼 위치에서 메뉴 표시
        menu.exec(self.sender().mapToGlobal(QPoint(0, self.sender().height())))

    def _reset_to_defaults(self):
        """설정을 기본값으로 초기화"""
        from datetime import date

        self.market_combo.setCurrentIndex(0)
        self.range_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate(DATA_COLLECTION['start_year'], 1, 1))
        self.end_date.setDate(QDate.currentDate())
        self.collect_price.setChecked(True)
        self.collect_financial.setChecked(True)
        self.skip_existing.setChecked(True)
        self.validate_data.setChecked(True)

        self._add_log("[INFO] 설정이 기본값으로 초기화되었습니다.")

    def _create_separator(self) -> QWidget:
        """구분선 생성"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"""
            background: {theme_manager.colors['border']};
            max-height: 1px;
        """)
        return separator

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
        title_icon.setPixmap(get_status_icon('zap', 14).pixmap(QSize(14, 14)))
        title_layout.addWidget(title_icon)

        title = QLabel("실시간 진행률")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_font = QFont("Inter", 14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title_container)

        # 프로그레스 바
        self.progress_bar = GradientProgressBar()
        layout.addWidget(self.progress_bar)

        # 상태 정보
        self.progress_status_label = QLabel("현재: 초기화 중...")
        self.progress_status_label.setStyleSheet(
            f"color: {theme_manager.colors['text_secondary']};"
        )
        layout.addWidget(self.progress_status_label)

        self.progress_count_label = QLabel("수집: 0개 종목")
        self.progress_count_label.setStyleSheet(
            f"color: {theme_manager.colors['text_secondary']};"
        )
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
        self.status_label = QLabel("준비 완료")
        self.status_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 통계 (옵션)
        stats_label = QLabel("예상 소요 시간: 약 5~10분")
        stats_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_tertiary']};
            font-size: 11px;
        """)
        layout.addWidget(stats_label)

        return status_bar

    def _create_step_cards(self) -> QWidget:
        """설정 패널 생성"""
        from ui.widgets.settings import CollapsibleSection

        # 스크롤 영역
        from PySide6.QtWidgets import QScrollArea
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

        # Step 1: 수집 설정
        config_section = self._create_config_section()
        layout.addWidget(config_section)

        # Step 2: 진행 옵션
        options_section = self._create_options_section()
        layout.addWidget(options_section)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_config_section(self) -> QWidget:
        """수집 설정 섹션"""
        from ui.widgets.settings import CollapsibleSection

        section = CollapsibleSection("수집 설정", icon="⚙️", expanded=True)

        # 컨텐츠 위젯
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 공통 폰트
        label_font = QFont("Pretendard Variable", FONT_SIZES['body_small'])
        combo_font = QFont("Pretendard Variable", FONT_SIZES['body_small'])

        # 시장 선택
        market_row = QHBoxLayout()
        market_label = QLabel("시장:")
        market_label.setFont(label_font)
        market_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        market_label.setFixedWidth(140)
        market_row.addWidget(market_label)

        self.market_combo = QComboBox()
        self.market_combo.addItems(["전체 (KOSPI + KOSDAQ)", "KOSPI", "KOSDAQ"])
        self.market_combo.setFont(combo_font)
        market_row.addWidget(self.market_combo)
        layout.addLayout(market_row)

        # 수집 범위 선택
        range_row = QHBoxLayout()
        range_label = QLabel("수집 범위:")
        range_label.setFont(label_font)
        range_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        range_label.setFixedWidth(140)
        range_row.addWidget(range_label)

        self.range_combo = QComboBox()
        self.range_combo.addItems([
            "전체 종목",
            "주요 종목만 (시총 상위 200개)",
            "시가총액 1조 이상",
            "KOSPI 200"
        ])
        self.range_combo.setFont(combo_font)
        self.range_combo.setCurrentIndex(0)  # 기본값: 전체 종목
        range_row.addWidget(self.range_combo)
        layout.addLayout(range_row)

        # 기간 선택
        period_row = QHBoxLayout()
        period_label = QLabel("기간:")
        period_label.setFont(label_font)
        period_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        period_label.setFixedWidth(140)
        period_row.addWidget(period_label)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(DATA_COLLECTION['start_year'], 1, 1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFont(combo_font)
        period_row.addWidget(self.start_date)

        period_row.addWidget(QLabel("~"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFont(combo_font)
        period_row.addWidget(self.end_date)

        layout.addLayout(period_row)

        section.add_widget(content)
        return section

    def _create_options_section(self) -> QWidget:
        """수집 옵션 섹션"""
        from ui.widgets.settings import CollapsibleSection

        section = CollapsibleSection("수집 옵션", icon="📋", expanded=True)

        # 컨텐츠 위젯
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 수집 항목 체크박스
        checkbox_font = QFont("Pretendard Variable", FONT_SIZES['body'])

        self.collect_price = QCheckBox("주가 데이터 (OHLCV)")
        self.collect_price.setChecked(True)
        self.collect_price.setFont(checkbox_font)
        layout.addWidget(self.collect_price)

        self.collect_financial = QCheckBox("재무제표 (DART)")
        self.collect_financial.setChecked(True)
        self.collect_financial.setFont(checkbox_font)
        layout.addWidget(self.collect_financial)

        # 추가 옵션
        items_label = QLabel("추가 옵션:")
        items_label.setFont(QFont("Pretendard Variable", FONT_SIZES['body_small']))
        items_label.setStyleSheet(f"color: {theme_manager.colors['text_secondary']};")
        layout.addWidget(items_label)

        self.force_recollect = QCheckBox("완전 재수집 (기존 데이터 삭제)")
        self.force_recollect.setChecked(False)  # 기본: 증분 업데이트
        self.force_recollect.setFont(checkbox_font)
        self.force_recollect.setToolTip(
            "체크 시: 기존 데이터를 삭제하고 전체 재수집\n"
            "체크 안 함: 누락된 구간만 자동으로 채우기 (스마트 증분 업데이트)"
        )
        layout.addWidget(self.force_recollect)

        self.validate_data = QCheckBox("데이터 검증 수행")
        self.validate_data.setChecked(True)
        self.validate_data.setFont(checkbox_font)
        layout.addWidget(self.validate_data)

        section.add_widget(content)
        return section

    def _apply_preset(self, preset_name: str):
        """프리셋 적용"""
        from datetime import date

        if preset_name == "빠른 시작":
            # 주요 100개 종목, 최근 1년
            self.market_combo.setCurrentIndex(0)  # 전체
            self.range_combo.setCurrentIndex(1)  # 주요 종목만
            self.start_date.setDate(
                QDate(date.today().year - 1, 1, 1)
            )
            self.end_date.setDate(QDate.currentDate())
            self.collect_price.setChecked(True)
            self.collect_financial.setChecked(False)
            self._add_log("[INFO] 프리셋 적용: 빠른 시작")

        elif preset_name == "표준 수집":
            # 전체 종목, 최근 3년
            self.market_combo.setCurrentIndex(0)  # 전체
            self.range_combo.setCurrentIndex(0)  # 전체 종목
            self.start_date.setDate(
                QDate(date.today().year - 3, 1, 1)
            )
            self.end_date.setDate(QDate.currentDate())
            self.collect_price.setChecked(True)
            self.collect_financial.setChecked(True)
            self._add_log("[INFO] 프리셋 적용: 표준 수집")

        elif preset_name == "전체 수집":
            # 전체 종목, 10년치
            self.market_combo.setCurrentIndex(0)  # 전체
            self.range_combo.setCurrentIndex(0)  # 전체 종목
            self.start_date.setDate(
                QDate(DATA_COLLECTION['start_year'], 1, 1)
            )
            self.end_date.setDate(QDate.currentDate())
            self.collect_price.setChecked(True)
            self.collect_financial.setChecked(True)
            self._add_log("[INFO] 프리셋 적용: 전체 수집 (10년)")

        elif preset_name == "업데이트만":
            # 증분 업데이트만
            self.market_combo.setCurrentIndex(0)  # 전체
            self.range_combo.setCurrentIndex(4)  # 증분 업데이트만
            self.start_date.setDate(
                QDate(date.today().year, 1, 1)
            )
            self.end_date.setDate(QDate.currentDate())
            self.collect_price.setChecked(True)
            self.collect_financial.setChecked(True)
            self._add_log("[INFO] 프리셋 적용: 업데이트만")

    def _start_collection(self):
        """데이터 수집 시작"""
        # 이미 실행 중이면 중지
        if self.worker and self.worker.isRunning():
            print("[DEBUG] Stop collection")
            self.worker.stop()
            self.start_btn.setText("  수집 시작")
            self.start_btn.setIcon(get_primary_icon('play', 18))
            self.status_label.setText("사용자가 수집을 중지했습니다.")
            self.progress_section.setVisible(False)
            return

        print("[DEBUG] Start collection")

        # 진행률 섹션 표시
        self.progress_section.setVisible(True)

        # 버튼 상태 변경
        self.start_btn.setText("  수집 중지")
        self.start_btn.setIcon(get_status_icon('pause', 18))

        # 초기화
        self.progress_bar.set_progress(0, animate=False)
        self.progress_status_label.setText("현재: 초기화 중...")
        self.progress_count_label.setText("수집: 0개 종목")

        # 시작 시간 기록
        self.start_time = time.time()

        self._add_log("[INFO] 데이터 수집을 시작합니다...")

        # 설정 가져오기
        market_type = self.market_combo.currentText()
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        collect_price = self.collect_price.isChecked()
        collect_financial = self.collect_financial.isChecked()
        collection_range = self.range_combo.currentText()

        # 워커 생성 및 시작
        self.worker = DataCollectionWorker(
            market_type, start_date, end_date,
            collect_price, collect_financial,
            collection_range
        )

        # 시그널 연결
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)

        # 워커 시작
        self.worker.start()
        self.collection_started.emit()

    def _on_progress(self, current: int, total: int, message: str):
        """진행률 업데이트"""
        self.update_progress(current, total, message)

    def _on_finished(self, success: bool, total_count: int):
        """수집 완료"""
        self.start_btn.setText("  수집 시작")
        self.start_btn.setIcon(get_primary_icon('play', 18))

        if success:
            self._add_log(f"[SUCCESS] 데이터 수집 완료! 총 {total_count}개 종목")
            self.progress_status_label.setText("현재: 수집 완료!")
            self.progress_count_label.setText(f"완료: {total_count}개 종목")
            self.progress_bar.set_progress(100)
            self.status_label.setText(f"수집 완료: {total_count}개 종목")
        else:
            self._add_log("[ERROR] 데이터 수집 실패")
            self.progress_status_label.setText("현재: 수집 중지됨")
            self.status_label.setText("수집 중지됨")

        # 진행률 섹션 숨기기
        self.progress_section.setVisible(False)

        self.collection_finished.emit(success, total_count)

    def _on_error(self, error_message: str):
        """에러 처리"""
        self._add_log(f"[ERROR] {error_message}")
        self.progress_status_label.setText(f"에러: {error_message}")
        self.status_label.setText(f"에러: {error_message}")
        self.start_btn.setText("  수집 시작")
        self.start_btn.setIcon(get_primary_icon('play', 18))
        self.progress_section.setVisible(False)

    def _add_log(self, message: str):
        """로그 추가 (비활성화됨)"""
        pass

    def _clear_log(self):
        """로그 지우기 (비활성화됨)"""
        pass

    def update_progress(self, current: int, total: int, message: str = ""):
        """진행률 업데이트"""
        print(f"[DEBUG] Progress: {current}/{total} - {message}")
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.set_progress(percentage, animate=True)

        self.progress_count_label.setText(f"진행: {current}/{total} 종목")

        if message:
            self.progress_status_label.setText(f"현재: {message}")
            self._add_log(f"[INFO] {message}")

        # ETA 계산
        if self.start_time and current > 0 and total > 0:
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

            self.status_label.setText(f"예상 완료: {eta_str}")
        else:
            self.status_label.setText("예상 완료: 계산 중...")
