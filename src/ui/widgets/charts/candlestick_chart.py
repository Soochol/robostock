"""
Candlestick Chart Widget
캔들스틱 차트 위젯 (matplotlib 기반)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates

from styles.theme import theme_manager
from core.config import CHART_CONFIG


def rgba_to_mpl(rgba_str):
    """
    Convert CSS rgba string to matplotlib-compatible format
    'rgba(255, 255, 255, 0.1)' -> (1.0, 1.0, 1.0, 0.1)
    """
    if not isinstance(rgba_str, str) or not rgba_str.startswith('rgba'):
        return rgba_str

    match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', rgba_str)
    if match:
        r, g, b, a = match.groups()
        return (int(r)/255, int(g)/255, int(b)/255, float(a))
    return rgba_str


class CandlestickChart(FigureCanvasQTAgg):
    """
    캔들스틱 차트 위젯

    특징:
    - OHLCV 데이터 시각화
    - 60일 이동평균선
    - 블록 플로팅 마커
    - 인터랙티브 줌/팬

    사용 예시:
        chart = CandlestickChart()
        chart.plot_stock(df, blocks)
    """

    def __init__(self, parent=None, width=12, height=8):
        # Figure 생성 (다크 배경)
        self.fig = Figure(figsize=(width, height), facecolor='none')
        super().__init__(self.fig)
        self.setParent(parent)

        # 축 생성 (캔들차트용 - 상단 70%, 거래량용 - 하단 30%)
        # gridspec을 사용해서 높이 비율을 3:1로 설정
        gs = self.fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
        self.ax = self.fig.add_subplot(gs[0])  # 캔들스틱
        self.ax_volume = self.fig.add_subplot(gs[1], sharex=self.ax)  # 거래량 (X축 공유)

        # 데이터
        self.df = None
        self.blocks = []
        self.current_ticker = None

        # 줌 상태 저장
        self.original_xlim = None
        self.original_ylim = None

        # 드래그(팬) 상태
        self._pan_start = None
        self._is_panning = False
        self._pan_xlim = None
        self._pan_ylim = None
        self._pan_ylim_volume = None
        self._current_pan_axes = None

        # 툴팁 (풍선말)
        self._tooltip = None
        self._tooltip_annotation = None

        # 성능 최적화: 애니메이션 활성화
        self.fig.canvas.supports_blit = True

        # 스타일 설정
        self._setup_style()

        # 마우스 이벤트 연결
        self._connect_events()

    def _setup_style(self):
        """차트 스타일 설정"""
        colors = theme_manager.colors

        # 캔들스틱 축 배경색 및 스타일
        self.ax.set_facecolor(colors['bg_layer_1'])
        self.fig.patch.set_facecolor('none')

        # 캔들스틱 축 색상
        self.ax.tick_params(colors=colors['text_secondary'], which='both')
        self.ax.spines['bottom'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['top'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['left'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['right'].set_color(rgba_to_mpl(colors['border']))

        # 캔들스틱 그리드
        self.ax.grid(True, color=colors['grid'], alpha=0.3, linestyle='--', linewidth=0.5)

        # 거래량 축 배경색 및 스타일
        self.ax_volume.set_facecolor(colors['bg_layer_1'])

        # 거래량 축 색상
        self.ax_volume.tick_params(colors=colors['text_secondary'], which='both')
        self.ax_volume.spines['bottom'].set_color(rgba_to_mpl(colors['border']))
        self.ax_volume.spines['top'].set_color(rgba_to_mpl(colors['border']))
        self.ax_volume.spines['left'].set_color(rgba_to_mpl(colors['border']))
        self.ax_volume.spines['right'].set_color(rgba_to_mpl(colors['border']))

        # 거래량 그리드
        self.ax_volume.grid(True, color=colors['grid'], alpha=0.3, linestyle='--', linewidth=0.5, axis='y')

        # 여백 (상단 여백을 충분히 확보)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.10)

    def plot_stock(self, ticker: str = None, df: pd.DataFrame = None, blocks: list = None):
        """
        종목 차트 그리기

        Args:
            ticker: 종목 코드
            df: OHLCV 데이터프레임 (columns: Date, Open, High, Low, Close, Volume)
            blocks: 블록 리스트 (dict with keys: type, date, trading_value, etc.)
        """
        self.current_ticker = ticker
        self.blocks = blocks or []

        # 데이터 없으면 샘플 데이터 생성
        if df is None:
            df = self._generate_sample_data()

        self.df = df

        # 차트 초기화
        self.ax.clear()
        self.ax_volume.clear()
        self._setup_style()

        # 캔들스틱 그리기
        self._draw_candlestick()

        # 60일 이동평균선
        self._draw_moving_average()

        # 블록 마커
        self._draw_block_markers()

        # 거래량 그리기
        self._draw_volume()

        # 타이틀
        if ticker:
            colors = theme_manager.colors
            self.ax.set_title(
                f"{ticker} - 캔들스틱 차트",
                color=colors['text_primary'],
                fontsize=14,
                fontweight='bold',
                pad=10
            )

        # 레이블
        colors = theme_manager.colors
        self.ax.set_ylabel('가격', color=colors['text_secondary'])
        self.ax_volume.set_ylabel('거래량', color=colors['text_secondary'], fontsize=9)

        # 캔들스틱 차트의 X축 레이블 숨기기
        self.ax.tick_params(axis='x', labelbottom=False)

        # X축 범위를 데이터에 딱 맞게 설정 (여백 제거)
        if self.df is not None and len(self.df) > 0:
            dates = mdates.date2num(self.df.index.to_pydatetime())
            # 양쪽에 캔들 반개씩만 여백 추가
            margin = 0.5
            self.ax.set_xlim(dates[0] - margin, dates[-1] + margin)
            print(f"[CANDLE DEBUG] Setting xlim to {dates[0] - margin} ~ {dates[-1] + margin}")

        # 날짜 포맷 (마지막에 적용)
        self._format_xaxis()

        # 다시 그리기
        self.draw()

        # draw 후 한번 더 포맷 적용 (확실하게)
        self._format_xaxis()

    def _generate_sample_data(self) -> pd.DataFrame:
        """샘플 데이터 생성 (데모용)"""
        # 1년치 데이터
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        n = len(dates)

        # 랜덤 워크 가격 생성
        np.random.seed(42)
        base_price = 50000
        returns = np.random.randn(n) * 0.02  # 2% 변동성
        close_prices = base_price * np.exp(np.cumsum(returns))

        # OHLC 생성
        data = []
        for i, date in enumerate(dates):
            close = close_prices[i]
            open_price = close * (1 + np.random.randn() * 0.01)
            high = max(open_price, close) * (1 + abs(np.random.randn()) * 0.015)
            low = min(open_price, close) * (1 - abs(np.random.randn()) * 0.015)
            volume = int(np.random.uniform(100000, 1000000))

            data.append({
                'Date': date,
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': volume,
            })

        df = pd.DataFrame(data)
        df.set_index('Date', inplace=True)

        # 60일 이동평균 추가
        df['MA60'] = df['Close'].rolling(window=60).mean()

        # 샘플 블록 데이터
        self.blocks = [
            {'type': 1, 'date': pd.Timestamp('2024-03-15'), 'trading_value': 520, 'label': '1번\n520억'},
            {'type': 2, 'date': pd.Timestamp('2024-08-20'), 'trading_value': 2340, 'label': '2번\nD+D+1+D+2'},
        ]

        return df

    def _draw_candlestick(self):
        """캔들스틱 그리기"""
        if self.df is None or len(self.df) == 0:
            return

        colors_config = theme_manager.colors
        candle_up = colors_config['candle_up']
        candle_down = colors_config['candle_down']

        # 날짜를 숫자로 변환
        dates = mdates.date2num(self.df.index.to_pydatetime())

        # 디버깅: 첫 5개 날짜 출력
        print(f"[CANDLE DEBUG] Total candles: {len(self.df)}")
        print(f"[CANDLE DEBUG] First 5 date numbers: {dates[:5]}")
        print(f"[CANDLE DEBUG] First 5 actual dates: {self.df.index[:5].tolist()}")

        for i in range(len(self.df)):
            date = dates[i]
            open_price = self.df.iloc[i]['Open']
            high = self.df.iloc[i]['High']
            low = self.df.iloc[i]['Low']
            close = self.df.iloc[i]['Close']

            # 상승/하락 색상
            color = candle_up if close >= open_price else candle_down

            # 몸통 (body)
            height = abs(close - open_price)
            bottom = min(open_price, close)

            # 캔들 너비 (거래량 바와 동일하게)
            candle_width = 0.7

            body = Rectangle(
                (date - candle_width/2, bottom),
                candle_width,
                height,
                facecolor=color,
                edgecolor=color,
                alpha=0.8
            )
            self.ax.add_patch(body)

            # 꼬리 (wick)
            self.ax.plot([date, date], [low, high], color=color, linewidth=1.0, alpha=0.8)

            # 디버깅: 첫 3개 캔들 위치 출력
            if i < 3:
                print(f"[CANDLE DEBUG] Candle {i}: date_num={date}, x_pos={date - candle_width/2} to {date + candle_width/2}")

    def _draw_moving_average(self):
        """60일 이동평균선 그리기"""
        if self.df is None or 'MA60' not in self.df.columns:
            return

        colors = theme_manager.colors
        ma_color = colors['ma_60']

        # NaN 제거
        ma_data = self.df['MA60'].dropna()
        if len(ma_data) == 0:
            return

        dates = mdates.date2num(ma_data.index.to_pydatetime())

        self.ax.plot(
            dates,
            ma_data.values,
            color=ma_color,
            linewidth=2,
            alpha=0.7,
            label='60MA',
            linestyle='-'
        )

        # 범례
        self.ax.legend(
            loc='upper left',
            fontsize=9,
            framealpha=0.7,
            facecolor=theme_manager.colors['bg_layer_2'],
            edgecolor=rgba_to_mpl(theme_manager.colors['border'])
        )

    def _draw_volume(self):
        """거래량 그리기"""
        if self.df is None or 'Volume' not in self.df.columns:
            return

        colors_config = theme_manager.colors
        volume_up = colors_config['candle_up']
        volume_down = colors_config['candle_down']

        # 날짜를 숫자로 변환
        dates = mdates.date2num(self.df.index.to_pydatetime())

        # 상승/하락 판단 (전일 대비)
        colors_list = []
        for i in range(len(self.df)):
            if i == 0:
                color = volume_up
            else:
                if self.df.iloc[i]['Close'] >= self.df.iloc[i-1]['Close']:
                    color = volume_up
                else:
                    color = volume_down
            colors_list.append(color)

        # 바 그리기 (캔들과 동일한 너비)
        bar_width = 0.7

        self.ax_volume.bar(
            dates,
            self.df['Volume'].values,
            width=bar_width,
            color=colors_list,
            alpha=0.6,
            edgecolor='none',
            align='center'
        )

        # 블록 발생일 하이라이트
        self._highlight_volume_blocks()

    def _highlight_volume_blocks(self):
        """거래량 차트의 블록 발생일 하이라이트"""
        if not self.blocks or self.df is None:
            return

        from core.enums import BlockType

        colors = theme_manager.colors
        block_colors = {
            BlockType.BLOCK_1: colors['block_1'],
            BlockType.BLOCK_2: colors['block_2'],
            BlockType.BLOCK_3: colors['block_3'],
            BlockType.BLOCK_4: colors['block_4'],
            1: colors['block_1'],
            2: colors['block_2'],
            3: colors['block_3'],
            4: colors['block_4'],
        }

        for block in self.blocks:
            block_type = block.get('type', 1)
            block_date = block.get('date')

            if block_date is None:
                continue

            # 날짜 변환
            if isinstance(block_date, str):
                block_date = pd.Timestamp(block_date)
            elif not isinstance(block_date, pd.Timestamp):
                block_date = pd.Timestamp(block_date)

            # 해당 날짜의 거래량 찾기
            if block_date in self.df.index:
                volume = self.df.loc[block_date, 'Volume']
                date_num = mdates.date2num(block_date.to_pydatetime())

                # 블록 색상으로 바 덮어쓰기
                marker_color = block_colors.get(block_type, colors['primary'])

                bar_width = 0.7
                self.ax_volume.bar(
                    date_num,
                    volume,
                    width=bar_width,
                    color=marker_color,
                    alpha=0.9,
                    edgecolor='white',
                    linewidth=1.5,
                    zorder=10,
                    align='center'
                )

    def _draw_block_markers(self):
        """블록 플로팅 마커 그리기"""
        if not self.blocks:
            return

        from core.enums import BlockType

        colors = theme_manager.colors
        block_colors = {
            BlockType.BLOCK_1: colors['block_1'],
            BlockType.BLOCK_2: colors['block_2'],
            BlockType.BLOCK_3: colors['block_3'],
            BlockType.BLOCK_4: colors['block_4'],
            1: colors['block_1'],  # 숫자도 지원
            2: colors['block_2'],
            3: colors['block_3'],
            4: colors['block_4'],
        }

        for block in self.blocks:
            block_type = block.get('type', 1)
            block_date = block.get('date')

            if block_date is None:
                continue

            # 날짜를 숫자로 변환
            if isinstance(block_date, str):
                block_date = pd.Timestamp(block_date)
            elif not isinstance(block_date, pd.Timestamp):
                # datetime.date 또는 datetime.datetime을 Timestamp로 변환
                block_date = pd.Timestamp(block_date)

            date_num = mdates.date2num(block_date.to_pydatetime())

            # 해당 날짜의 가격 찾기
            if block_date in self.df.index:
                high_price = self.df.loc[block_date, 'High']
            else:
                # 가장 가까운 날짜 찾기
                idx = self.df.index.get_indexer([block_date], method='nearest')[0]
                high_price = self.df.iloc[idx]['High']

            # 마커 색상
            marker_color = block_colors.get(block_type, colors['primary'])

            # 마커 그리기 (삼각형)
            marker_y = high_price * 1.05
            self.ax.plot(
                date_num,
                marker_y,
                marker='v',
                markersize=15,
                color=marker_color,
                markeredgecolor='white',
                markeredgewidth=1.5,
                zorder=10
            )

            # 레이블 생성
            label = self._create_block_label(block)

            # 텍스트 레이블 추가
            if label:
                self.ax.text(
                    date_num,
                    marker_y * 1.03,
                    label,
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    color=colors['text_primary'],
                    bbox=dict(
                        boxstyle='round,pad=0.4',
                        facecolor=rgba_to_mpl(colors['bg_glass']),
                        edgecolor=marker_color,
                        linewidth=1.5,
                        alpha=0.9
                    ),
                    zorder=11
                )

    def _create_block_label(self, block: dict) -> str:
        """블록 정보에서 레이블 생성"""
        from core.enums import BlockType

        block_type = block.get('type')
        trading_value = block.get('trading_value')
        new_high_grade = block.get('new_high_grade')
        volume_ratio = block.get('volume_ratio')
        pattern_type = block.get('pattern_type')

        # 1번 블록
        if block_type == BlockType.BLOCK_1 or block_type == 1:
            label_parts = ["1번"]
            if trading_value:
                label_parts.append(f"{trading_value / 1e8:.0f}억")
            if new_high_grade:
                grade_str = new_high_grade.value if hasattr(
                    new_high_grade, 'value'
                ) else str(new_high_grade)
                label_parts.append(grade_str)
            return "\n".join(label_parts)

        # 2번 블록
        elif block_type == BlockType.BLOCK_2 or block_type == 2:
            label_parts = ["2번"]
            if volume_ratio:
                label_parts.append(f"{volume_ratio * 100:.0f}%")
            if pattern_type:
                pattern_str = pattern_type.value if hasattr(
                    pattern_type, 'value'
                ) else str(pattern_type)
                label_parts.append(pattern_str)
            return "\n".join(label_parts)

        # 기타
        return f"{block_type}번"

    def _format_xaxis(self):
        """X축 날짜 포맷"""
        if self.df is None or len(self.df) == 0:
            return

        # 중요: X축의 단위를 날짜로 명시
        import matplotlib.units as munits

        # 날짜 컨버터 등록
        converter = mdates.DateConverter()
        munits.registry[datetime] = converter
        munits.registry[pd.Timestamp] = converter

        # 거래량 차트의 X축 날짜 활성화
        self.ax_volume.xaxis_date()

        # 디버그: 현재 X축 범위 확인
        xlim = self.ax.get_xlim()
        print(f"[DEBUG] X-axis limits: {xlim}")
        print(f"[DEBUG] X-axis limits as dates: {mdates.num2date(xlim[0])} to {mdates.num2date(xlim[1])}")

        # 날짜 포맷터 설정 (년/월 형식)
        date_formatter = mdates.DateFormatter('%Y/%m')
        self.ax_volume.xaxis.set_major_formatter(date_formatter)

        # 로케이터 설정 (데이터 범위에 따라 적절한 간격)
        data_range_days = len(self.df)
        if data_range_days > 730:  # 2년 이상
            interval = 3  # 3개월마다
        elif data_range_days > 365:  # 1년 이상
            interval = 2  # 2개월마다
        else:
            interval = 1  # 1개월마다

        locator = mdates.MonthLocator(interval=interval)
        self.ax_volume.xaxis.set_major_locator(locator)

        # X축 보이기 설정
        self.ax_volume.xaxis.set_visible(True)
        self.ax_volume.xaxis.label.set_visible(False)  # xlabel은 숨김

        # 틱 레이블 설정
        self.ax_volume.tick_params(
            axis='x',
            which='major',
            direction='out',
            length=5,
            width=1,
            colors=theme_manager.colors['text_secondary'],
            labelsize=9,
            labelbottom=True,
            bottom=True,
            top=False,
            labeltop=False,
            rotation=0
        )

        # 레이블 스타일 강제 적용
        for label in self.ax_volume.get_xticklabels():
            label.set_ha('center')
            label.set_rotation(0)

        # 그리드 라인 표시
        self.ax_volume.xaxis.grid(True, color=theme_manager.colors['grid'], alpha=0.3, linestyle='--', linewidth=0.5)

    def _connect_events(self):
        """마우스 이벤트 연결"""
        self.mpl_connect('scroll_event', self._on_scroll)
        self.mpl_connect('button_press_event', self._on_mouse_press)
        self.mpl_connect('button_release_event', self._on_mouse_release)
        self.mpl_connect('motion_notify_event', self._on_mouse_move)

    def _on_scroll(self, event):
        """마우스 휠로 줌 인/아웃 (TradingView 스타일)"""
        # 줌 비율
        zoom_factor = 1.2

        # 줌 인/아웃
        if event.button == 'up':
            scale = 1 / zoom_factor
        elif event.button == 'down':
            scale = zoom_factor
        else:
            return

        # 현재 범위
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        ylim_volume = self.ax_volume.get_ylim()

        # 캔들 차트 영역 내부에서의 줌 (양방향)
        if event.inaxes == self.ax:
            xdata = event.xdata
            ydata = event.ydata

            # 새 범위 계산 (X, Y 동시 줌)
            new_xlim = [
                xdata - (xdata - xlim[0]) * scale,
                xdata + (xlim[1] - xdata) * scale
            ]
            new_ylim = [
                ydata - (ydata - ylim[0]) * scale,
                ydata + (ylim[1] - ydata) * scale
            ]

            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            # X축 공유되므로 거래량 차트도 자동으로 줌됨
            self.draw()
            return

        # 거래량 차트 영역 내부에서의 줌
        if event.inaxes == self.ax_volume:
            xdata = event.xdata
            ydata = event.ydata

            # 새 범위 계산
            new_xlim = [
                xdata - (xdata - xlim[0]) * scale,
                xdata + (xlim[1] - xdata) * scale
            ]
            new_ylim_volume = [
                ydata - (ydata - ylim_volume[0]) * scale,
                ydata + (ylim_volume[1] - ydata) * scale
            ]

            self.ax.set_xlim(new_xlim)  # X축 공유
            self.ax_volume.set_ylim(new_ylim_volume)
            self.draw()
            return

        # X축 영역에서의 줌 (수평 방향만)
        if event.inaxes in [self.ax.xaxis, self.ax_volume.xaxis]:
            # X축 중앙 기준으로 줌
            x_center = (xlim[0] + xlim[1]) / 2
            x_range = (xlim[1] - xlim[0]) / 2

            new_xlim = [
                x_center - x_range * scale,
                x_center + x_range * scale
            ]

            self.ax.set_xlim(new_xlim)
            # X축 공유되므로 거래량 차트도 자동으로 줌됨
            self.draw()
            return

        # Y축 영역에서의 줌 (수직 방향만)
        if event.inaxes == self.ax.yaxis:
            # Y축 중앙 기준으로 줌
            y_center = (ylim[0] + ylim[1]) / 2
            y_range = (ylim[1] - ylim[0]) / 2

            new_ylim = [
                y_center - y_range * scale,
                y_center + y_range * scale
            ]

            self.ax.set_ylim(new_ylim)
            self.draw()
            return

        # 거래량 Y축 영역에서의 줌
        if event.inaxes == self.ax_volume.yaxis:
            y_center = (ylim_volume[0] + ylim_volume[1]) / 2
            y_range = (ylim_volume[1] - ylim_volume[0]) / 2

            new_ylim_volume = [
                y_center - y_range * scale,
                y_center + y_range * scale
            ]

            self.ax_volume.set_ylim(new_ylim_volume)
            self.draw()
            return

    def _on_mouse_press(self, event):
        """마우스 버튼 누름"""
        # 더블클릭으로 줌 리셋
        if event.dblclick and event.inaxes in [self.ax, self.ax_volume]:
            self.reset_zoom()
            return

        # 왼쪽 버튼으로 팬 시작
        if event.button == 1 and event.inaxes in [self.ax, self.ax_volume]:
            self._is_panning = True
            self._pan_start = (event.xdata, event.ydata)
            self._pan_xlim = self.ax.get_xlim()
            self._pan_ylim = self.ax.get_ylim()
            self._pan_ylim_volume = self.ax_volume.get_ylim()
            self._current_pan_axes = event.inaxes  # 어느 축에서 팬을 시작했는지 기록
            # 커서 변경 (손 모양)
            self.setCursor(Qt.ClosedHandCursor)

            # 백그라운드 캡처 (블릿 렌더링용)
            self.ax.set_animated(False)
            self.draw_idle()

    def _on_mouse_release(self, event):
        """마우스 버튼 릴리즈"""
        if event.button == 1:
            self._is_panning = False
            self._pan_start = None
            # 커서 복원
            self.setCursor(Qt.ArrowCursor)

            # 최종 렌더링
            self.ax.set_animated(False)
            self.draw_idle()

    def _on_mouse_move(self, event):
        """마우스 이동"""
        # 팬 중이면 팬 처리
        if self._is_panning and self._pan_start is not None:
            # 차트 영역 밖으로 나가면 무시
            if event.inaxes not in [self.ax, self.ax_volume] or event.xdata is None or event.ydata is None:
                return

            # 툴팁 숨기기
            if self._tooltip_annotation:
                self._tooltip_annotation.set_visible(False)

            # 이동 거리 계산
            dx = event.xdata - self._pan_start[0]
            dy = event.ydata - self._pan_start[1]

            # 새로운 범위 계산 (드래그 방향 반대로 이동)
            new_xlim = [self._pan_xlim[0] - dx, self._pan_xlim[1] - dx]

            # X축은 항상 공유하여 이동
            self.ax.set_xlim(new_xlim)

            # Y축은 팬을 시작한 차트만 이동
            if self._current_pan_axes == self.ax:
                new_ylim = [self._pan_ylim[0] - dy, self._pan_ylim[1] - dy]
                self.ax.set_ylim(new_ylim)
            elif self._current_pan_axes == self.ax_volume:
                new_ylim_volume = [self._pan_ylim_volume[0] - dy, self._pan_ylim_volume[1] - dy]
                self.ax_volume.set_ylim(new_ylim_volume)

            # flush_events()로 즉시 렌더링
            self.flush_events()
            return

        # 팬 중이 아니면 툴팁 표시 (캔들 차트에서만)
        if event.inaxes == self.ax:
            self._show_tooltip(event)
        else:
            self._hide_tooltip()

    def _show_tooltip(self, event):
        """캔들 정보 툴팁 표시"""
        if self.df is None or event.xdata is None or event.ydata is None:
            return

        # 마우스 위치에서 가장 가까운 캔들 찾기
        x_date = mdates.num2date(event.xdata)

        # 날짜 인덱스 찾기
        try:
            # 가장 가까운 날짜 찾기
            dates = self.df.index
            time_diffs = abs(dates - x_date)
            nearest_idx = time_diffs.argmin()

            # 해당 캔들 데이터
            candle_data = self.df.iloc[nearest_idx]
            candle_date = dates[nearest_idx]

            # 툴팁 텍스트 생성
            tooltip_text = (
                f"날짜: {candle_date.strftime('%Y/%m/%d')}\n"
                f"시가: {candle_data['Open']:,.0f}\n"
                f"고가: {candle_data['High']:,.0f}\n"
                f"저가: {candle_data['Low']:,.0f}\n"
                f"종가: {candle_data['Close']:,.0f}\n"
                f"거래량: {candle_data['Volume']:,.0f}"
            )

            # 기존 툴팁이 있으면 텍스트만 업데이트 (성능 향상)
            if self._tooltip_annotation:
                self._tooltip_annotation.set_text(tooltip_text)
                self._tooltip_annotation.xy = (mdates.date2num(candle_date), candle_data['High'])
                self._tooltip_annotation.set_visible(True)
            else:
                # 새 툴팁 추가
                colors = theme_manager.colors
                self._tooltip_annotation = self.ax.annotate(
                    tooltip_text,
                    xy=(mdates.date2num(candle_date), candle_data['High']),
                    xytext=(20, 20),
                    textcoords='offset points',
                    bbox=dict(
                        boxstyle='round,pad=0.5',
                        facecolor=colors['bg_layer_2'],
                        edgecolor=colors['primary'],
                        alpha=0.95,
                        linewidth=2
                    ),
                    fontsize=9,
                    color=colors['text_primary'],
                    ha='left',
                    va='bottom',
                    zorder=100
                )

            self.draw_idle()

        except Exception as e:
            # 에러 발생 시 조용히 무시
            pass

    def _hide_tooltip(self):
        """툴팁 숨기기"""
        if self._tooltip_annotation:
            self._tooltip_annotation.set_visible(False)
            self.draw_idle()

    def reset_zoom(self):
        """줌 리셋"""
        if self.df is None or len(self.df) == 0:
            return

        # 원본 범위로 복원
        self.ax.autoscale()
        self.draw()

    def highlight_block(self, block_id: int):
        """
        특정 블록 강조

        Args:
            block_id: 블록 ID
        """
        # TODO: 블록 강조 로직
        pass

    def zoom_to_block(self, block_date):
        """
        블록 중심으로 줌

        Args:
            block_date: 블록 날짜
        """
        if self.df is None:
            return

        # 블록 날짜 기준 ±3개월
        start_date = block_date - timedelta(days=90)
        end_date = block_date + timedelta(days=90)

        # X축 범위 설정
        self.ax.set_xlim(
            mdates.date2num(start_date.to_pydatetime()),
            mdates.date2num(end_date.to_pydatetime())
        )

        self.draw()
