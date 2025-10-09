"""
Chart Viewer Panel
차트 뷰어 패널 - 캔들스틱 + 거래량
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QScrollBar
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont

from datetime import datetime, timedelta
from core.config import SPACING
from core.enums import BlockType
from styles.theme import theme_manager
from styles.typography import FONT_SIZES
from ui.widgets.charts.candlestick_chart import CandlestickChart
from ui.widgets.common.glass_card import GlassCard
from resources.icons import get_menu_icon, get_primary_icon
from infrastructure.database import get_session
from infrastructure.database.models import Stock, VolumeBlock


class ChartViewerPanel(QWidget):
    """
    차트 뷰어 패널

    구조:
    - 상단: 종목 선택 + 컨트롤
    - 중앙: 캔들스틱 + 거래량 통합 차트
    - 타임라인 컨트롤
    """

    stock_changed = Signal(str)  # ticker

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_ticker = None
        self._sync_in_progress = False  # 재귀 방지 플래그
        self._total_data_range = None  # 전체 데이터 범위
        self._visible_range = 180  # 표시할 일 수 (기본 6개월)
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(SPACING['md'])

        # 상단 헤더 (고정 크기)
        header = self._create_header()
        layout.addWidget(header, stretch=0)

        # 스플리터로 좌우 분할 (블록 결과 | 차트)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {theme_manager.colors['border']};
            }}
        """)

        # 좌측: 블록탐지 결과 섹션
        result_section = self._create_block_result_section()
        splitter.addWidget(result_section)

        # 우측: 차트 섹션
        chart_section = self._create_chart_section()
        splitter.addWidget(chart_section)

        # 비율 설정 (블록 결과: 차트 = 30:70)
        splitter.setSizes([300, 700])  # 30% : 70%
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        layout.addWidget(splitter, stretch=1)

        # 초기 차트 로드 (샘플 데이터)
        self._load_sample_chart()

    def _create_header(self) -> QWidget:
        """헤더 생성"""
        header = QWidget()
        header.setFixedHeight(40)  # 고정 높이 설정
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])

        # 제목
        title_icon = QLabel()
        title_icon.setPixmap(
            get_primary_icon('bar-chart', 24).pixmap(QSize(24, 24))
        )
        layout.addWidget(title_icon, stretch=0)

        title = QLabel("차트 분석")
        title_font = QFont("Pretendard Variable", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, stretch=0)

        layout.addStretch(1)

        return header

    def _create_block_result_section(self) -> QWidget:
        """블록탐지 결과 섹션 (좌측)"""
        section = GlassCard()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(SPACING['md'], SPACING['md'],
                                  SPACING['md'], SPACING['md'])
        layout.setSpacing(SPACING['sm'])

        # 제목
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(get_menu_icon('search', 16).pixmap(QSize(16, 16)))
        title_layout.addWidget(title_icon)

        title = QLabel("블록 탐지 결과")
        title_font = QFont("Pretendard Variable", 14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addWidget(title_container)

        # 날짜 범위 선택 (세로 배치로 변경)
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(4)

        date_label = QLabel("조회 기간:")
        date_label.setStyleSheet(
            f"color: {theme_manager.colors['text_secondary']}; "
            f"font-size: {FONT_SIZES['small']}px;"
        )
        date_layout.addWidget(date_label)

        # 시작일
        date_row1 = QHBoxLayout()
        date_row1.addWidget(QLabel("시작:"))
        self.result_start_date = QDateEdit()
        self.result_start_date.setDate(QDate.currentDate().addYears(-1))
        self.result_start_date.setCalendarPopup(True)
        date_row1.addWidget(self.result_start_date)
        date_layout.addLayout(date_row1)

        # 종료일
        date_row2 = QHBoxLayout()
        date_row2.addWidget(QLabel("종료:"))
        self.result_end_date = QDateEdit()
        self.result_end_date.setDate(QDate.currentDate())
        self.result_end_date.setCalendarPopup(True)
        date_row2.addWidget(self.result_end_date)
        date_layout.addLayout(date_row2)

        layout.addWidget(date_container)

        # 조회 버튼
        search_btn = QPushButton("  조회")
        search_btn.setIcon(get_primary_icon('search', 16))
        search_btn.setIconSize(QSize(16, 16))
        search_btn.setMinimumHeight(36)
        search_btn.clicked.connect(self._on_load_blocks)
        layout.addWidget(search_btn)

        # 검색 필드
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("종목명 또는 코드 검색...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.setMinimumHeight(32)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_container)

        # 결과 트리 (종목별 그룹핑)
        self.block_tree = QTreeWidget()
        self.block_tree.setHeaderLabels(["종목/블록", "타입", "발생일", "거래량"])

        # 컬럼 너비 설정
        header = self.block_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 종목명/블록
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 타입
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 날짜
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 거래량

        self.block_tree.setAlternatingRowColors(True)
        self.block_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.block_tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.block_tree.setRootIsDecorated(True)
        self.block_tree.setIndentation(16)

        # 클릭 이벤트
        self.block_tree.itemClicked.connect(self._on_tree_item_clicked)

        layout.addWidget(self.block_tree, stretch=1)

        # 하단 정보 (더 컴팩트하게)
        self.result_info_label = QLabel("조회 버튼을 눌러 결과를 확인하세요.")
        self.result_info_label.setStyleSheet(
            f"color: {theme_manager.colors['text_secondary']}; "
            f"font-size: {FONT_SIZES['caption']}px; "
            f"padding: 4px;"
        )
        layout.addWidget(self.result_info_label)

        return section

    def _create_chart_section(self) -> QWidget:
        """차트 섹션"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])

        # 차트 헤더 (종목 정보)
        chart_header = QWidget()
        chart_header_layout = QHBoxLayout(chart_header)
        chart_header_layout.setContentsMargins(0, 0, 0, 0)

        self.chart_stock_label = QLabel("종목을 선택하세요")
        chart_label_font = QFont("Pretendard Variable", 14)
        chart_label_font.setBold(True)
        self.chart_stock_label.setFont(chart_label_font)
        chart_header_layout.addWidget(self.chart_stock_label)

        chart_header_layout.addStretch()

        layout.addWidget(chart_header)

        # 캔들스틱 + 거래량 통합 차트
        self.candlestick_chart = CandlestickChart()
        layout.addWidget(self.candlestick_chart, stretch=1)

        # X축 스크롤바
        self.chart_scrollbar = QScrollBar(Qt.Horizontal)
        self.chart_scrollbar.setMinimum(0)
        self.chart_scrollbar.setMaximum(100)
        self.chart_scrollbar.setValue(100)  # 기본값: 최신 데이터
        self.chart_scrollbar.valueChanged.connect(self._on_scrollbar_changed)
        self.chart_scrollbar.setStyleSheet(f"""
            QScrollBar:horizontal {{
                background: {theme_manager.colors['bg_layer_1']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {theme_manager.colors['primary']};
                min-width: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {theme_manager.colors['primary_hover']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
        layout.addWidget(self.chart_scrollbar)

        # 타임라인 컨트롤
        timeline = self._create_timeline_control()
        layout.addWidget(timeline)

        return section

    def _create_timeline_control(self) -> QWidget:
        """타임라인 컨트롤"""
        control = QFrame()
        control.setObjectName("timeline_control")
        control.setStyleSheet(f"""
            #timeline_control {{
                background: {theme_manager.colors['bg_glass']};
                border: 1px solid {theme_manager.colors['border']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)

        layout = QHBoxLayout(control)
        layout.setSpacing(SPACING['sm'])

        # 기간 버튼
        periods = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y', 'ALL']
        self.period_buttons = QButtonGroup(self)

        for i, period in enumerate(periods):
            btn = QPushButton(period)
            btn.setFont(QFont("Pretendard Variable", FONT_SIZES['small']))
            btn.setCheckable(True)
            btn.setFixedWidth(50)

            # 기본 선택 (6M)
            if period == '6M':
                btn.setChecked(True)

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {theme_manager.colors['text_secondary']};
                    border: 1px solid {theme_manager.colors['border']};
                    border-radius: 6px;
                    padding: 6px;
                    font-size: {FONT_SIZES['small']}px;
                    font-weight: 600;
                }}
                QPushButton:checked {{
                    background: {theme_manager.colors['primary']};
                    color: white;
                    border-color: {theme_manager.colors['primary']};
                }}
                QPushButton:hover {{
                    background: {theme_manager.colors['primary_subtle']};
                }}
            """)

            # 버튼 클릭 이벤트 연결
            btn.clicked.connect(lambda checked, p=period: self._on_period_changed(p))

            self.period_buttons.addButton(btn, i)
            layout.addWidget(btn)

        layout.addStretch()

        # 블록 중심 버튼
        block_center_btn = QPushButton("📍 블록 중심")
        block_center_btn.setFont(
            QFont("Pretendard Variable", FONT_SIZES['body_small'])
        )
        block_center_btn.setFixedWidth(100)
        layout.addWidget(block_center_btn)

        return control

    def _on_period_changed(self, period: str):
        """기간 버튼 클릭 시 표시 범위 변경"""
        period_days = {
            '1D': 1,
            '1W': 7,
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '1Y': 365,
            '5Y': 1825,
            'ALL': 999999
        }

        self._visible_range = period_days.get(period, 180)

        # 스크롤바를 최신 데이터로 이동
        self.chart_scrollbar.setValue(100)

        # 차트 업데이트
        self._update_chart_view()

    def _on_scrollbar_changed(self, value):
        """스크롤바 값 변경 시 차트 X축 범위 업데이트"""
        self._update_chart_view()

    def _update_chart_view(self):
        """차트 뷰 업데이트 (스크롤바 값과 표시 범위에 따라)"""
        if self.candlestick_chart.df is None or len(self.candlestick_chart.df) == 0:
            return

        import matplotlib.dates as mdates

        df = self.candlestick_chart.df
        total_days = len(df)

        # 표시할 범위가 전체보다 크면 전체 표시
        if self._visible_range >= total_days:
            dates = mdates.date2num(df.index.to_pydatetime())
            self.candlestick_chart.ax.set_xlim(dates[0], dates[-1])
            self.candlestick_chart.draw()
            # 스크롤바 비활성화
            self.chart_scrollbar.setEnabled(False)
            return

        # 스크롤바 활성화
        self.chart_scrollbar.setEnabled(True)

        # 스크롤바 값에 따라 시작 인덱스 계산 (0~100)
        value = self.chart_scrollbar.value()
        max_start_idx = total_days - self._visible_range
        start_idx = int((value / 100.0) * max_start_idx)
        end_idx = start_idx + self._visible_range

        # 인덱스 범위 체크
        start_idx = max(0, min(start_idx, total_days - self._visible_range))
        end_idx = min(total_days, start_idx + self._visible_range)

        # 날짜 범위로 변환
        dates = mdates.date2num(df.index.to_pydatetime())
        self.candlestick_chart.ax.set_xlim(dates[start_idx], dates[end_idx])
        self.candlestick_chart.draw()

    def _load_sample_chart(self):
        """샘플 차트 로드"""
        # 캔들스틱 + 거래량 통합 차트에 샘플 데이터 로드 (자동으로 샘플 생성됨)
        self.candlestick_chart.plot_stock(ticker="삼성전자 (005930)")

    def _on_load_blocks(self):
        """DB에서 블록탐지 결과 조회 (종목별 그룹핑)"""
        start_date = self.result_start_date.date().toPython()
        end_date = self.result_end_date.date().toPython()

        try:
            with get_session() as session:
                # 블록 조회 (Stock 조인)
                blocks = session.query(VolumeBlock, Stock).join(
                    Stock, VolumeBlock.stock_id == Stock.id
                ).filter(
                    VolumeBlock.date >= start_date,
                    VolumeBlock.date <= end_date
                ).order_by(
                    Stock.name,  # 종목명순
                    VolumeBlock.date.desc()  # 종목 내에서는 날짜 역순
                ).all()

                # 종목별로 그룹핑 (세션 내에서 데이터 추출)
                stock_groups = {}
                for block, stock in blocks:
                    stock_key = stock.code
                    if stock_key not in stock_groups:
                        stock_groups[stock_key] = {
                            'name': stock.name,
                            'code': stock.code,
                            'blocks': []
                        }
                    # 블록 데이터를 딕셔너리로 변환 (DetachedInstanceError 방지)
                    block_data = {
                        'id': block.id,
                        'date': block.date,
                        'volume': block.volume,
                        'block_type': block.block_type,
                        'trading_value': block.trading_value,
                        'close_price': block.close_price
                    }
                    stock_groups[stock_key]['blocks'].append(block_data)

                # 전체 블록 데이터 저장 (검색용)
                self.all_blocks_data = stock_groups

                # 트리 위젯 업데이트
                self._update_tree_widget(stock_groups)

                # 정보 레이블 업데이트
                total_blocks = len(blocks)
                total_stocks = len(stock_groups)
                self.result_info_label.setText(
                    f"총 {total_stocks}개 종목, {total_blocks}개의 블록"
                )

        except Exception as e:
            self.result_info_label.setText(f"조회 실패: {str(e)}")
            print(f"[ERROR] Failed to load blocks: {e}")
            import traceback
            traceback.print_exc()

    def _update_tree_widget(self, stock_groups):
        """트리 위젯 업데이트"""
        self.block_tree.clear()

        for stock_code, stock_data in sorted(
            stock_groups.items(),
            key=lambda x: x[1]['name']
        ):
            # 종목 노드 (부모)
            stock_item = QTreeWidgetItem(self.block_tree)
            stock_name = stock_data['name']
            stock_code = stock_data['code']
            block_count = len(stock_data['blocks'])

            stock_item.setText(0, f"{stock_name} ({stock_code})")
            stock_item.setText(1, f"{block_count}개")
            stock_item.setData(0, Qt.UserRole, {
                'type': 'stock',
                'code': stock_code,
                'name': stock_name
            })

            # 종목 노드 스타일
            font = QFont("Pretendard Variable", FONT_SIZES['body_small'])
            font.setBold(True)
            stock_item.setFont(0, font)

            # 블록 노드 (자식)
            for block_data in stock_data['blocks']:
                block_item = QTreeWidgetItem(stock_item)

                # 블록 타입
                block_type_str = "1번" if block_data['block_type'] == BlockType.BLOCK_1 else "2번"
                block_item.setText(1, block_type_str)

                # 발생일
                block_date = block_data['date']
                if hasattr(block_date, 'strftime'):
                    date_str = block_date.strftime("%Y-%m-%d")
                else:
                    date_str = str(block_date)
                block_item.setText(2, date_str)

                # 거래량
                volume = block_data['volume']
                if volume >= 1000000:
                    volume_str = f"{volume / 1000000:.1f}M"
                elif volume >= 1000:
                    volume_str = f"{volume / 1000:.0f}K"
                else:
                    volume_str = f"{volume:,}"
                block_item.setText(3, volume_str)

                # 블록 데이터 저장 (딕셔너리로 저장)
                block_item.setData(0, Qt.UserRole, {
                    'type': 'block',
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'block_date': block_date  # date만 저장
                })

        # 모든 종목 노드를 기본적으로 펼침
        self.block_tree.expandAll()

    def _on_search_text_changed(self, text):
        """검색어 변경 시 필터링"""
        if not hasattr(self, 'all_blocks_data'):
            return

        search_text = text.strip().lower()

        if not search_text:
            # 검색어가 없으면 전체 표시
            self._update_tree_widget(self.all_blocks_data)
            # 전체 데이터 정보 표시
            total_stocks = len(self.all_blocks_data)
            total_blocks = sum(len(s['blocks']) for s in self.all_blocks_data.values())
            self.result_info_label.setText(
                f"총 {total_stocks}개 종목, {total_blocks}개의 블록"
            )
            return

        # 검색어로 필터링
        filtered_groups = {}
        for stock_code, stock_data in self.all_blocks_data.items():
            stock_name = stock_data['name'].lower()
            code = stock_data['code'].lower()

            # 종목명 또는 코드에 검색어 포함되면 표시
            if search_text in stock_name or search_text in code:
                filtered_groups[stock_code] = stock_data

        self._update_tree_widget(filtered_groups)

        # 정보 레이블 업데이트
        if filtered_groups:
            total_stocks = len(filtered_groups)
            total_blocks = sum(len(s['blocks']) for s in filtered_groups.values())
            self.result_info_label.setText(
                f"검색 결과: {total_stocks}개 종목, {total_blocks}개의 블록"
            )
        else:
            self.result_info_label.setText("검색 결과가 없습니다.")

    def _on_tree_item_clicked(self, item, column):
        """트리 항목 클릭 시 차트 로드"""
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return

        # 블록 항목만 차트 로드
        if item_data['type'] == 'block':
            stock_code = item_data['stock_code']
            stock_name = item_data['stock_name']
            block_date = item_data['block_date']

            # 차트 로드
            self._load_stock_chart(stock_code, stock_name, block_date)

    def _on_block_row_selected(self):
        """블록 테이블 행 선택 이벤트"""
        print("[DEBUG] _on_block_row_selected called")
        selected_rows = self.block_table.selectedItems()
        if not selected_rows:
            print("[DEBUG] No selected rows")
            return

        # 선택된 행의 첫 번째 아이템 가져오기
        row = selected_rows[0].row()
        print(f"[DEBUG] Selected row: {row}")

        # 종목 정보 가져오기 (새로운 컬럼 구조)
        name_item = self.block_table.item(row, 0)
        stock_code = name_item.data(Qt.UserRole)  # UserRole에 저장된 종목코드
        stock_name = name_item.text().split('\n')[0]  # 첫 줄이 종목명

        date_item = self.block_table.item(row, 2)
        block_date = date_item.data(Qt.UserRole)  # UserRole에 저장된 전체 날짜

        print(f"[DEBUG] Stock selected: {stock_name} ({stock_code}) - {block_date}")

        # 차트 레이블 업데이트
        self.chart_stock_label.setText(
            f"{stock_name} ({stock_code}) - {block_date}"
        )

        # 차트 업데이트
        print(f"[DEBUG] Calling _load_stock_chart with code: {stock_code}")
        self._load_stock_chart(stock_code)

    def _load_stock_chart(self, stock_code: str, stock_name: str = None, block_date=None):
        """종목 차트 로드 (DB에서 실제 데이터 + 블록 정보)"""
        print(f"[DEBUG] _load_stock_chart called with code: {stock_code}, block_date: {block_date}")
        try:
            import pandas as pd
            from infrastructure.database.models import PriceData

            with get_session() as session:
                # 종목 조회
                stock = session.query(Stock).filter_by(
                    code=stock_code
                ).first()

                if not stock:
                    print(f"[ERROR] Stock {stock_code} not found")
                    return

                # 세션 안에서 필요한 데이터 미리 추출
                stock_id = stock.id
                stock_name = stock.name
                print(f"[DEBUG] Stock found: {stock_name} (ID: {stock_id})")

                # 가격 데이터 조회
                from datetime import datetime, timedelta

                # block_date가 있으면 해당 날짜 중심으로, 없으면 최근 1년
                if block_date:
                    # 블록 날짜를 datetime으로 변환
                    if not isinstance(block_date, datetime):
                        if hasattr(block_date, 'year'):
                            # date 객체
                            block_date = datetime.combine(block_date, datetime.min.time())
                        else:
                            # 문자열
                            block_date = pd.to_datetime(block_date)

                    # 블록 날짜 기준 ±6개월
                    start_date = block_date - timedelta(days=180)
                    end_date = block_date + timedelta(days=180)
                else:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=365)

                price_data = session.query(PriceData).filter(
                    PriceData.stock_id == stock_id,
                    PriceData.date >= start_date,
                    PriceData.date <= end_date
                ).order_by(PriceData.date).all()

                print(f"[DEBUG] Found {len(price_data)} price data records")

                if not price_data:
                    print(f"[WARN] No price data found for {stock_name}")
                    # 샘플 데이터로 폴백
                    df = None
                else:
                    # DataFrame 생성
                    data = []
                    for p in price_data:
                        data.append({
                            'Date': p.date,
                            'Open': p.open,
                            'High': p.high,
                            'Low': p.low,
                            'Close': p.close,
                            'Volume': p.volume
                        })
                    df = pd.DataFrame(data)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date')
                    print(f"[DEBUG] Created DataFrame with {len(df)} rows")

                # 블록 조회
                blocks = session.query(VolumeBlock).filter_by(
                    stock_id=stock_id
                ).order_by(VolumeBlock.date).all()

                print(f"[DEBUG] Found {len(blocks)} blocks for {stock_name}")

                # 블록 정보를 dict 리스트로 변환
                block_list = []
                for block in blocks:
                    block_list.append({
                        'date': block.date,
                        'type': block.block_type,
                        'volume': block.volume,
                        'trading_value': block.trading_value,
                        'new_high_grade': block.new_high_grade,
                        'volume_ratio': block.volume_ratio,
                        'pattern_type': block.pattern_type
                    })

            # 차트 업데이트 (실제 데이터 + 블록 정보 전달, 거래량 포함)
            print(f"[DEBUG] Updating candlestick chart with actual data and {len(block_list)} blocks")
            self.candlestick_chart.plot_stock(
                ticker=f"{stock_name} ({stock_code})",
                df=df,
                blocks=block_list
            )

        except Exception as e:
            print(f"[ERROR] Failed to load stock chart: {e}")
            import traceback
            traceback.print_exc()

    def load_stock(self, ticker: str):
        """
        종목 로드

        Args:
            ticker: 종목 코드
        """
        self._current_ticker = ticker
        self._load_stock_chart(ticker)
