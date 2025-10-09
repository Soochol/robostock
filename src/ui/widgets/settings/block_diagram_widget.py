"""
Block Diagram Widget
블록 탐지 캔들차트 다이어그램 위젯
"""

import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath


class BlockDiagramWidget(QWidget):
    """블록 탐지 시각화 다이어그램 (캔들차트 스타일)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 900)

        # 예시 설정값
        self.block1_settings = {
            'max_volume_period': 20,
            'max_volume_ratio': 150,
            'min_trading_value': 100_000_000_000,  # 1000억
            'min_market_cap': 1_000_000_000,  # 10억
            'price_high_enabled': True,  # N개월 신고가 조건
            'price_high_period_months': 3,  # 3개월
        }

        self.block2_settings = {
            'gap_min': 1,
            'gap_max': 10,
            'volume_ratio': 80,
            'min_trading_value': 30_000_000_000,  # 300억
            'pattern_enabled': True,
            'pattern_d1_threshold_pct': 80,
            'pattern_d2_threshold_pct': 80,
            'price_breakthrough_enabled': True,  # 고점 돌파 조건
            'price_breakthrough_pct': 30,  # 1번 블록 고점 대비 30% 이상
        }

        # 랜덤 캔들 데이터 생성
        self._generate_sample_data()

    def _generate_sample_data(self):
        """샘플 캔들 데이터 생성"""
        random.seed(42)
        self.block1_candles = []

        # 1번 블록: 20일 캔들 (마지막 날 거래량 급등 + 신고가)
        base_volume = 100
        base_price = 10000

        # D일이 3개월 신고가가 되도록 가격 설정
        d_day_high = base_price + 2000  # D일 고점

        for i in range(20):
            if i == 19:  # D일
                volume = base_volume * 2.0  # 150% 이상

                # D일은 신고가 (다른 날보다 높게)
                open_price = d_day_high - 500 + random.uniform(-100, 100)
                close_price = d_day_high - 200 + random.uniform(-100, 100)
                high_price = d_day_high  # 신고가!
                low_price = min(open_price, close_price) - random.uniform(0, 100)
            else:
                volume = base_volume + random.uniform(-20, 20)

                # D일 이전 날들은 D일 고점보다 낮게 (신고가 조건 만족)
                max_price_before_d = d_day_high - 300  # D일보다 최소 300원 낮게
                open_price = base_price + random.uniform(-500, 500)
                close_price = open_price + random.uniform(-300, 300)
                high_price = min(max(open_price, close_price) + random.uniform(0, 200), max_price_before_d)
                low_price = min(open_price, close_price) - random.uniform(0, 200)

            self.block1_candles.append({
                'open': open_price,
                'close': close_price,
                'high': high_price,
                'low': low_price,
                'volume': volume,
                'is_d_day': (i == 19)
            })

        # 2번 블록: D일 + 갭 + (D, D+1, D+2 후보들)
        self.block2_d_candle = self.block1_candles[-1].copy()
        self.block2_gap_days = 5  # 예시: 5일 갭

        # D일 거래량
        d_volume = self.block2_d_candle['volume']

        # 1번 블록의 최고가 (20일 기간 내) = D일 고점
        self.block1_high_price = max([c['high'] for c in self.block1_candles])

        # 3개월(약 90일) 전 데이터의 최고가 (D일이 3개월 신고가인지 비교용)
        # D일 20일 기간 내 최고가보다 낮아야 신고가 조건 만족
        # 20일 기간 전의 최고가를 D일보다 낮게 설정
        before_20days_high = max([c['high'] for c in self.block1_candles[:-1]])  # D일 제외 최고가
        self.three_month_high_price = before_20days_high  # D일 전 최고가 (D일보다 낮음)

        # 고점 돌파 기준가 (1번 블록 고점 + 30%)
        breakthrough_price = self.block1_high_price * 1.30

        # 갭 후 D일 캔들 (고점 돌파 안함)
        self.block2_d_repeat_candle = {
            'open': 11200 + random.uniform(-500, 500),
            'close': 11200 + random.uniform(-300, 300),
            'high': self.block1_high_price * 1.15,  # 15% 상승 (돌파 실패)
            'low': 10800,
            'volume': d_volume * 0.9,  # D일 대비 90%
            'label': 'D'
        }

        # D+1일 캔들 (고점 돌파!)
        self.block2_d1_candle = {
            'open': 10800 + random.uniform(-500, 500),
            'close': 11500 + random.uniform(-300, 300),
            'high': breakthrough_price + random.uniform(0, 500),  # 30% 이상 돌파!
            'low': 10400,
            'volume': d_volume * 0.85,  # D일 대비 85%
            'label': 'D+1'
        }

        # D+2일 캔들 (고점 돌파 안함)
        self.block2_d2_candle = {
            'open': 10700 + random.uniform(-500, 500),
            'close': 10700 + random.uniform(-300, 300),
            'high': self.block1_high_price * 1.20,  # 20% 상승 (돌파 실패)
            'low': 10300,
            'volume': d_volume * 0.82,  # D일 대비 82%
            'label': 'D+2'
        }

        # 2번 블록 후보들 (갭 후)
        self.block2_candidates = [
            self.block2_d_repeat_candle,
            self.block2_d1_candle,
            self.block2_d2_candle
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 배경
        painter.fillRect(self.rect(), QColor(30, 30, 35))

        # 통합 캔들차트 (1번 블록 → 2번 블록)
        self._draw_unified_candlestick(painter, 50, 50)

    def _draw_block1_candlestick(self, painter: QPainter, x: int, y: int):
        """1번 블록 캔들차트"""

        # 타이틀
        painter.setPen(QPen(QColor(79, 195, 247), 2))
        font = QFont("맑은 고딕", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(x, y, "🔷 1번 블록: 초기 대량 거래일 탐지")

        # 설정 파라미터 표시
        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(180, 180, 190)))
        period = self.block1_settings['max_volume_period']
        ratio = self.block1_settings['max_volume_ratio']
        trading = self.block1_settings['min_trading_value'] / 100_000_000  # 억

        painter.drawText(x, y + 20, f"📌 조건: {period}일 기간 내 거래량 {ratio}% 이상, 거래대금 {trading:.0f}억 이상")

        # 캔들 영역
        chart_y = y + 50
        candle_width = 18
        candle_spacing = 6
        max_candle_height = 120
        volume_height = 80

        # 가격/거래량 정규화
        all_prices = []
        all_volumes = []
        for candle in self.block1_candles:
            all_prices.extend([candle['high'], candle['low']])
            all_volumes.append(candle['volume'])

        min_price = min(all_prices)
        max_price = max(all_prices)
        max_volume = max(all_volumes)
        price_range = max_price - min_price if max_price > min_price else 1

        # 기준선 (150% 거래량)
        avg_volume = sum(all_volumes[:-1]) / len(all_volumes[:-1])  # D일 제외 평균
        threshold_volume = max(all_volumes[:-1]) * (ratio / 100)  # 최대값의 150%
        threshold_y = chart_y + max_candle_height + volume_height - int((threshold_volume / max_volume) * volume_height)

        painter.setPen(QPen(QColor(255, 193, 7), 2, Qt.DashLine))
        painter.drawLine(x, threshold_y, x + len(self.block1_candles) * (candle_width + candle_spacing), threshold_y)

        painter.setFont(QFont("맑은 고딕", 8))
        painter.setPen(QPen(QColor(255, 193, 7)))
        painter.drawText(x + len(self.block1_candles) * (candle_width + candle_spacing) + 5, threshold_y + 5, f"{ratio}% 기준선")

        # 캔들스틱 그리기
        for i, candle in enumerate(self.block1_candles):
            candle_x = x + i * (candle_width + candle_spacing)

            # 가격 캔들
            is_bullish = candle['close'] > candle['open']
            is_d_day = candle['is_d_day']

            # 정규화된 좌표
            open_y = chart_y + max_candle_height - int((candle['open'] - min_price) / price_range * max_candle_height)
            close_y = chart_y + max_candle_height - int((candle['close'] - min_price) / price_range * max_candle_height)
            high_y = chart_y + max_candle_height - int((candle['high'] - min_price) / price_range * max_candle_height)
            low_y = chart_y + max_candle_height - int((candle['low'] - min_price) / price_range * max_candle_height)

            # 심지 (고가-저가)
            wick_x = candle_x + candle_width // 2
            if is_d_day:
                painter.setPen(QPen(QColor(244, 67, 54), 2))
            else:
                painter.setPen(QPen(QColor(100, 100, 110), 1))
            painter.drawLine(wick_x, high_y, wick_x, low_y)

            # 몸통 (시가-종가)
            body_height = abs(close_y - open_y)
            body_y = min(open_y, close_y)

            if is_d_day:
                # D일 - 빨간색 강조
                painter.setBrush(QBrush(QColor(244, 67, 54, 200)))
                painter.setPen(QPen(QColor(244, 67, 54), 2))
            elif is_bullish:
                painter.setBrush(QBrush(QColor(66, 165, 245, 150)))
                painter.setPen(QPen(QColor(33, 150, 243), 1))
            else:
                painter.setBrush(QBrush(QColor(239, 83, 80, 150)))
                painter.setPen(QPen(QColor(211, 47, 47), 1))

            if body_height < 2:
                body_height = 2
            painter.drawRect(candle_x, body_y, candle_width, body_height)

            # 거래량 막대
            volume_bar_height = int((candle['volume'] / max_volume) * volume_height)
            volume_y = chart_y + max_candle_height + volume_height - volume_bar_height

            if is_d_day:
                painter.setBrush(QBrush(QColor(244, 67, 54, 200)))
            else:
                painter.setBrush(QBrush(QColor(100, 100, 110, 100)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(candle_x, volume_y, candle_width, volume_bar_height)

            # D일 라벨
            if is_d_day:
                painter.setFont(QFont("맑은 고딕", 9, QFont.Bold))
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(candle_x - 5, chart_y + max_candle_height + volume_height + 20, "D일")

        # 브래킷 (기간 표시)
        bracket_y = chart_y + max_candle_height + volume_height + 40
        bracket_start = x
        bracket_end = x + len(self.block1_candles) * (candle_width + candle_spacing)

        painter.setPen(QPen(QColor(150, 150, 160), 1))
        painter.drawLine(bracket_start, bracket_y, bracket_end, bracket_y)
        painter.drawLine(bracket_start, bracket_y - 3, bracket_start, bracket_y)
        painter.drawLine(bracket_end, bracket_y - 3, bracket_end, bracket_y)

        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(180, 180, 190)))
        painter.drawText(bracket_start + 200, bracket_y + 15, f"{period}일 기간")

    def _draw_block2_candlestick(self, painter: QPainter, x: int, y: int):
        """2번 블록 캔들차트"""

        # 타이틀
        painter.setPen(QPen(QColor(79, 195, 247), 2))
        font = QFont("맑은 고딕", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(x, y, "🔷 2번 블록: 후속 대량 거래일 탐지")

        # 설정 파라미터 표시
        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(180, 180, 190)))
        gap_min = self.block2_settings['gap_min']
        gap_max = self.block2_settings['gap_max']
        ratio = self.block2_settings['volume_ratio']
        trading = self.block2_settings['min_trading_value'] / 100_000_000  # 억

        painter.drawText(x, y + 20, f"📌 조건: 갭 {gap_min}~{gap_max}일, D일 대비 거래량 {ratio}% 이상, 거래대금 {trading:.0f}억 이상")

        # 캔들 영역
        chart_y = y + 50
        candle_width = 60
        gap_width = 150

        # D일 캔들 (1번 블록)
        d_candle = self.block2_d_candle
        dn_candle = self.block2_dn_candle

        # 정규화
        all_prices = [d_candle['high'], d_candle['low'], dn_candle['high'], dn_candle['low']]
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_range = max_price - min_price if max_price > min_price else 1

        max_candle_height = 150
        volume_height = 100

        # D일 캔들 그리기
        self._draw_single_candle(painter, x, chart_y, candle_width, max_candle_height,
                                d_candle, min_price, price_range, QColor(244, 67, 54), "D일 (1번 블록)")

        # 갭 표시 (점선)
        gap_x = x + candle_width + 20
        gap_end_x = gap_x + gap_width

        painter.setPen(QPen(QColor(255, 193, 7), 2, Qt.DashLine))
        painter.drawLine(gap_x, chart_y + max_candle_height // 2,
                        gap_end_x, chart_y + max_candle_height // 2)

        # 갭 텍스트
        painter.setFont(QFont("맑은 고딕", 10))
        painter.setPen(QPen(QColor(255, 193, 7)))
        painter.drawText(gap_x + 40, chart_y + max_candle_height // 2 - 10,
                        f"갭: {self.block2_gap_days}일")

        # D+N일 캔들 그리기
        dn_x = gap_end_x + 20
        self._draw_single_candle(painter, dn_x, chart_y, candle_width, max_candle_height,
                                dn_candle, min_price, price_range, QColor(33, 150, 243), "D+N일 (2번 블록)")

        # 거래량 비교 (하단)
        volume_y = chart_y + max_candle_height + 20
        max_volume = max(d_candle['volume'], dn_candle['volume'])

        # D일 거래량 막대
        d_vol_height = int((d_candle['volume'] / max_volume) * volume_height)
        painter.setBrush(QBrush(QColor(244, 67, 54, 200)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, volume_y + volume_height - d_vol_height, candle_width, d_vol_height)

        # D+N일 거래량 막대
        dn_vol_height = int((dn_candle['volume'] / max_volume) * volume_height)
        painter.setBrush(QBrush(QColor(33, 150, 243, 200)))
        painter.drawRect(dn_x, volume_y + volume_height - dn_vol_height, candle_width, dn_vol_height)

        # 거래량 비율 표시
        vol_ratio = (dn_candle['volume'] / d_candle['volume']) * 100
        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(102, 187, 106)))
        painter.drawText(dn_x, volume_y + volume_height + 20, f"✓ {vol_ratio:.0f}% (D일 대비)")

        # 기준선 (80%)
        threshold_vol_height = int((d_candle['volume'] * (ratio / 100) / max_volume) * volume_height)
        threshold_y = volume_y + volume_height - threshold_vol_height

        painter.setPen(QPen(QColor(255, 193, 7), 2, Qt.DashLine))
        painter.drawLine(x, threshold_y, dn_x + candle_width, threshold_y)

        painter.setFont(QFont("맑은 고딕", 8))
        painter.setPen(QPen(QColor(255, 193, 7)))
        painter.drawText(dn_x + candle_width + 10, threshold_y + 5, f"{ratio}% 기준")

        # 패턴 매칭 정보 (우측)
        if self.block2_settings.get('pattern_enabled', False):
            pattern_x = x + 400
            pattern_y = chart_y + 50

            painter.setFont(QFont("맑은 고딕", 10, QFont.Bold))
            painter.setPen(QPen(QColor(186, 104, 200)))
            painter.drawText(pattern_x, pattern_y, "🔍 패턴 매칭")

            painter.setFont(QFont("맑은 고딕", 9))
            painter.setPen(QPen(QColor(180, 180, 190)))

            d1_th = self.block2_settings.get('pattern_d1_threshold_pct', 80)
            d2_th = self.block2_settings.get('pattern_d2_threshold_pct', 80)

            painter.drawText(pattern_x, pattern_y + 25, f"D+1 임계값: D일 × {d1_th}%")
            painter.drawText(pattern_x, pattern_y + 45, f"D+2 임계값: D일 × {d2_th}%")

    def _draw_unified_candlestick(self, painter: QPainter, x: int, y: int):
        """통합 캔들차트 (1번 블록 → 갭 → 2번 블록)"""

        # 타이틀
        painter.setPen(QPen(QColor(79, 195, 247), 2))
        font = QFont("맑은 고딕", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(x, y, "📊 블록 탐지 시각화")

        # 설정 파라미터 표시
        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(180, 180, 190)))

        b1_period = self.block1_settings['max_volume_period']
        b1_ratio = self.block1_settings['max_volume_ratio']
        b1_trading = self.block1_settings['min_trading_value'] / 100_000_000  # 억

        b2_gap_min = self.block2_settings['gap_min']
        b2_gap_max = self.block2_settings['gap_max']
        b2_ratio = self.block2_settings['volume_ratio']
        b2_trading = self.block2_settings['min_trading_value'] / 100_000_000  # 억

        b1_price_months = self.block1_settings.get('price_high_period_months', 3)
        painter.drawText(x, y + 25, f"🔷 1번 블록: {b1_period}일 기간, 거래량 {b1_ratio}% 이상, {b1_price_months}개월 신고가")

        b2_price_pct = self.block2_settings.get('price_breakthrough_pct', 30)
        painter.drawText(x, y + 45, f"🔷 2번 블록: 기간 {b2_gap_min}~{b2_gap_max}일, D일 대비 거래량 {b2_ratio}% 이상, 1번 블록 고점 대비 {b2_price_pct}% 이상 돌파")

        # 캔들 영역
        chart_y = y + 80
        candle_width = 18
        candle_spacing = 18  # 9 → 18 (2배)
        gap_width = 60  # 갭 영역 너비
        max_candle_height = 150
        volume_height = 100

        # 모든 가격/거래량 수집
        all_prices = []
        all_volumes = []

        for candle in self.block1_candles:
            all_prices.extend([candle['high'], candle['low']])
            all_volumes.append(candle['volume'])

        for candidate in self.block2_candidates:
            all_prices.extend([candidate['high'], candidate['low']])
            all_volumes.append(candidate['volume'])

        min_price = min(all_prices)
        max_price = max(all_prices)
        max_volume = max(all_volumes)
        price_range = max_price - min_price if max_price > min_price else 1

        # 1번 블록 기준선 (150%)
        b1_threshold_volume = max(all_volumes[:20]) * (b1_ratio / 100)
        b1_threshold_y = chart_y + max_candle_height + volume_height - int((b1_threshold_volume / max_volume) * volume_height)

        # 2번 블록 기준선 (D일의 80%)
        d_volume = self.block1_candles[-1]['volume']
        b2_threshold_volume = d_volume * (b2_ratio / 100)
        b2_threshold_y = chart_y + max_candle_height + volume_height - int((b2_threshold_volume / max_volume) * volume_height)

        # 1번 블록 영역 배경
        b1_bg_width = len(self.block1_candles) * (candle_width + candle_spacing)
        painter.fillRect(x - 10, chart_y - 10, b1_bg_width + 20, max_candle_height + volume_height + 20,
                        QColor(244, 67, 54, 20))

        # 1번 블록 라벨
        painter.setFont(QFont("맑은 고딕", 10, QFont.Bold))
        painter.setPen(QPen(QColor(244, 67, 54)))
        painter.drawText(x, chart_y - 15, "1번 블록 조건")

        # 1번 블록 캔들 그리기
        for i, candle in enumerate(self.block1_candles):
            candle_x = x + i * (candle_width + candle_spacing)
            is_d_day = candle['is_d_day']

            self._draw_candle(painter, candle_x, chart_y, candle_width, max_candle_height, volume_height,
                            candle, min_price, price_range, max_volume, is_d_day, is_block2=False)

            # D일 마커
            if is_d_day:
                painter.setFont(QFont("맑은 고딕", 10, QFont.Bold))
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(candle_x - 8, chart_y + max_candle_height + volume_height + 25, "D일")

                # 위쪽 화살표
                arrow_y = chart_y - 30
                painter.setPen(QPen(QColor(244, 67, 54), 3))
                painter.drawLine(candle_x + candle_width // 2, arrow_y, candle_x + candle_width // 2, chart_y - 5)
                self._draw_arrow_head_down(painter, candle_x + candle_width // 2, chart_y - 5, QColor(244, 67, 54))

        # 1번 블록 기준선
        painter.setPen(QPen(QColor(255, 193, 7), 2, Qt.DashLine))
        painter.drawLine(x, b1_threshold_y, x + b1_bg_width, b1_threshold_y)

        painter.setFont(QFont("맑은 고딕", 8))
        painter.setPen(QPen(QColor(255, 193, 7)))
        painter.drawText(x + b1_bg_width + 5, b1_threshold_y + 5, f"1번 {b1_ratio}%")

        # 3개월 신고가 기준선 (활성 시)
        if self.block1_settings.get('price_high_enabled', False):
            months = self.block1_settings.get('price_high_period_months', 3)

            # 3개월 신고가 기준선 (D일 이전 3개월 최고가, 하늘색)
            three_month_y = chart_y + max_candle_height - int((self.three_month_high_price - min_price) / price_range * max_candle_height)

            painter.setPen(QPen(QColor(0, 188, 212), 2, Qt.DashLine))  # 하늘색
            painter.drawLine(x, three_month_y, x + b1_bg_width, three_month_y)

            painter.setFont(QFont("맑은 고딕", 8))
            painter.setPen(QPen(QColor(0, 188, 212)))
            painter.drawText(x, three_month_y - 5, f"{months}개월 신고가 기준")

            # D일 고점이 3개월 신고가보다 높은지 체크 표시
            if self.block1_high_price > self.three_month_high_price:
                painter.setFont(QFont("맑은 고딕", 9, QFont.Bold))
                painter.setPen(QPen(QColor(76, 175, 80)))
                painter.drawText(x + b1_bg_width - 100, three_month_y - 15, f"✓ {months}개월 신고가 달성")

        # 기간 영역 (갭 → 기간으로 변경)
        gap_x = x + b1_bg_width + 20
        painter.setPen(QPen(QColor(100, 100, 110), 1, Qt.DashLine))
        painter.drawLine(gap_x, chart_y + max_candle_height // 2,
                        gap_x + gap_width, chart_y + max_candle_height // 2)

        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(255, 193, 7)))
        painter.drawText(gap_x + 5, chart_y + max_candle_height // 2 - 5,
                        f"기간 {self.block2_gap_days}일")

        # 2번 블록 후보 캔들들 (D, D+1, D+2)
        candidate_x = gap_x + gap_width + 20
        num_candidates = len(self.block2_candidates)
        candidate_bg_width = num_candidates * (candle_width + candle_spacing) - candle_spacing

        # 2번 블록 영역 배경 (초록색으로 변경)
        painter.fillRect(candidate_x - 10, chart_y - 10, candidate_bg_width + 20, max_candle_height + volume_height + 20,
                        QColor(76, 175, 80, 20))

        # 2번 블록 라벨
        painter.setFont(QFont("맑은 고딕", 10, QFont.Bold))
        painter.setPen(QPen(QColor(76, 175, 80)))
        painter.drawText(candidate_x, chart_y - 15, "2번 블록 후보 (기간 후)")

        # 각 후보 캔들 그리기
        for i, candidate in enumerate(self.block2_candidates):
            candle_x = candidate_x + i * (candle_width + candle_spacing)

            self._draw_candle(painter, candle_x, chart_y, candle_width, max_candle_height, volume_height,
                            candidate, min_price, price_range, max_volume, False, is_block2=True)

            # 라벨 (D, D+1, D+2)
            painter.setFont(QFont("맑은 고딕", 9, QFont.Bold))
            painter.setPen(QPen(QColor(255, 255, 255)))
            label = candidate['label']
            offset = -15 if label == 'D+2' else (-10 if label == 'D+1' else -5)
            painter.drawText(candle_x + offset, chart_y + max_candle_height + volume_height + 25, label)

            # 위쪽 화살표 (첫 번째 후보만) - 초록색으로 변경
            if i == 0:
                arrow_y = chart_y - 30
                painter.setPen(QPen(QColor(76, 175, 80), 3))
                painter.drawLine(candle_x + candle_width // 2, arrow_y, candle_x + candle_width // 2, chart_y - 5)
                self._draw_arrow_head_down(painter, candle_x + candle_width // 2, chart_y - 5, QColor(76, 175, 80))

        # 2번 블록 기준선 (1번 블록 D일 거래량의 80% - 1번 블록까지 확장)
        painter.setPen(QPen(QColor(186, 104, 200), 2, Qt.DashLine))
        # D일 캔들 위치 찾기
        d_day_x = x + (len(self.block1_candles) - 1) * (candle_width + candle_spacing)

        # D일부터 2번 블록 후보까지 기준선 그리기
        painter.drawLine(d_day_x, b2_threshold_y, candidate_x + candidate_bg_width + 20, b2_threshold_y)

        painter.setFont(QFont("맑은 고딕", 8))
        painter.setPen(QPen(QColor(186, 104, 200)))
        painter.drawText(candidate_x + candidate_bg_width + 25, b2_threshold_y + 5, f"D일 거래량 × {b2_ratio}%")

        # D일 거래량 막대에 표시
        painter.setFont(QFont("맑은 고딕", 8, QFont.Bold))
        painter.setPen(QPen(QColor(186, 104, 200)))
        painter.drawText(d_day_x - 30, b2_threshold_y - 5, "← D일 기준")

        # 고점 돌파 기준선 (활성 시)
        if self.block2_settings.get('price_breakthrough_enabled', False):
            price_pct = self.block2_settings.get('price_breakthrough_pct', 30)

            # 1번 블록 고점 기준선 (노란색)
            block1_high_y = chart_y + max_candle_height - int((self.block1_high_price - min_price) / price_range * max_candle_height)

            painter.setPen(QPen(QColor(255, 152, 0), 2, Qt.DashLine))  # 주황색
            painter.drawLine(x, block1_high_y, candidate_x + candidate_bg_width + 50, block1_high_y)

            painter.setFont(QFont("맑은 고딕", 8))
            painter.setPen(QPen(QColor(255, 152, 0)))
            painter.drawText(x, block1_high_y - 5, "1번 블록 고점")

            # 돌파 기준선 (30% 이상, 빨간색)
            breakthrough_price = self.block1_high_price * (1 + price_pct / 100)
            breakthrough_y = chart_y + max_candle_height - int((breakthrough_price - min_price) / price_range * max_candle_height)

            painter.setPen(QPen(QColor(244, 67, 54), 2, Qt.DashDotLine))  # 빨간색 점선
            painter.drawLine(x, breakthrough_y, candidate_x + candidate_bg_width + 50, breakthrough_y)

            painter.setFont(QFont("맑은 고딕", 8, QFont.Bold))
            painter.setPen(QPen(QColor(244, 67, 54)))
            painter.drawText(x, breakthrough_y - 5, f"돌파 기준 (+{price_pct}%)")

        # 패턴 매칭 정보 (활성 시)
        if self.block2_settings.get('pattern_enabled', False):
            d1_th = self.block2_settings.get('pattern_d1_threshold_pct', 80)
            d2_th = self.block2_settings.get('pattern_d2_threshold_pct', 80)

            # D+1, D+2 임계값 기준선
            d1_threshold_vol = d_volume * (d1_th / 100)
            d1_threshold_y = chart_y + max_candle_height + volume_height - int((d1_threshold_vol / max_volume) * volume_height)

            painter.setPen(QPen(QColor(156, 39, 176), 1, Qt.DashLine))
            painter.drawLine(candidate_x - 10, d1_threshold_y, candidate_x + candidate_bg_width + 10, d1_threshold_y)

            painter.setFont(QFont("맑은 고딕", 7))
            painter.setPen(QPen(QColor(156, 39, 176)))
            painter.drawText(candidate_x - 10, d1_threshold_y - 3, f"패턴: {d1_th}%")

        # 브래킷 (1번 블록 기간)
        bracket_y = chart_y + max_candle_height + volume_height + 70
        bracket_start = x
        bracket_end = x + b1_bg_width

        painter.setPen(QPen(QColor(150, 150, 160), 1))
        painter.drawLine(bracket_start, bracket_y, bracket_end, bracket_y)
        painter.drawLine(bracket_start, bracket_y - 3, bracket_start, bracket_y)
        painter.drawLine(bracket_end, bracket_y - 3, bracket_end, bracket_y)

        painter.setFont(QFont("맑은 고딕", 9))
        painter.setPen(QPen(QColor(180, 180, 190)))
        painter.drawText(bracket_start + b1_bg_width // 2 - 30, bracket_y + 15, f"{b1_period}일 기간")

        # 패턴 매칭 정보 (하단)
        if self.block2_settings.get('pattern_enabled', False):
            pattern_y = chart_y + max_candle_height + volume_height + 100

            painter.setFont(QFont("맑은 고딕", 10, QFont.Bold))
            painter.setPen(QPen(QColor(186, 104, 200)))
            painter.drawText(x, pattern_y, "🔍 패턴 매칭 활성")

            painter.setFont(QFont("맑은 고딕", 9))
            painter.setPen(QPen(QColor(180, 180, 190)))

            d1_th = self.block2_settings.get('pattern_d1_threshold_pct', 80)
            d2_th = self.block2_settings.get('pattern_d2_threshold_pct', 80)

            painter.drawText(x, pattern_y + 20, f"• D+1 임계값: D일 거래량 × {d1_th}%")
            painter.drawText(x, pattern_y + 40, f"• D+2 임계값: D일 거래량 × {d2_th}%")

    def _draw_candle(self, painter: QPainter, x: int, y: int, width: int, max_height: int, volume_height: int,
                    candle: dict, min_price: float, price_range: float, max_volume: float,
                    is_d_day: bool, is_block2: bool):
        """단일 캔들 그리기 (가격 + 거래량)"""

        # 정규화된 좌표
        open_y = y + max_height - int((candle['open'] - min_price) / price_range * max_height)
        close_y = y + max_height - int((candle['close'] - min_price) / price_range * max_height)
        high_y = y + max_height - int((candle['high'] - min_price) / price_range * max_height)
        low_y = y + max_height - int((candle['low'] - min_price) / price_range * max_height)

        # 색상 결정
        is_bullish = candle['close'] > candle['open']

        if is_d_day:
            color = QColor(244, 67, 54)  # 빨간색
        elif is_block2:
            color = QColor(76, 175, 80)  # 초록색 (파란색 → 초록색 변경)
        else:
            color = QColor(66, 165, 245) if is_bullish else QColor(239, 83, 80)

        # 심지
        wick_x = x + width // 2
        painter.setPen(QPen(color, 2 if (is_d_day or is_block2) else 1))
        painter.drawLine(wick_x, high_y, wick_x, low_y)

        # 몸통
        body_height = abs(close_y - open_y)
        body_y = min(open_y, close_y)

        if is_d_day or is_block2:
            # 투명도 적용 (200 → 150)
            transparent_color = QColor(color.red(), color.green(), color.blue(), 150)
            painter.setBrush(QBrush(transparent_color))
            painter.setPen(QPen(color, 2))
        else:
            # 일반 캔들도 투명도 적용 (150 → 100)
            base_color = color.lighter(120) if is_bullish else color
            transparent_color = QColor(base_color.red(), base_color.green(), base_color.blue(), 100)
            painter.setBrush(QBrush(transparent_color))
            painter.setPen(QPen(color, 1))

        if body_height < 2:
            body_height = 2
        painter.drawRect(x, body_y, width, body_height)

        # 거래량 막대
        volume_bar_height = int((candle['volume'] / max_volume) * volume_height)
        volume_y = y + max_height + volume_height - volume_bar_height

        if is_d_day or is_block2:
            # 투명도 적용 (200 → 120)
            volume_color = QColor(color.red(), color.green(), color.blue(), 120)
            painter.setBrush(QBrush(volume_color))
        else:
            painter.setBrush(QBrush(QColor(100, 100, 110, 80)))

        painter.setPen(Qt.NoPen)
        painter.drawRect(x, volume_y, width, volume_bar_height)

    def _draw_arrow_head_down(self, painter: QPainter, x: int, y: int, color: QColor):
        """아래 방향 화살촉"""
        size = 10
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x - size // 2, y - size)
        path.lineTo(x + size // 2, y - size)
        path.closeSubpath()

        painter.drawPath(path)

    def _draw_single_candle(self, painter: QPainter, x: int, y: int, width: int, max_height: int,
                           candle: dict, min_price: float, price_range: float, color: QColor, label: str):
        """단일 캔들 그리기"""

        # 정규화된 좌표
        open_y = y + max_height - int((candle['open'] - min_price) / price_range * max_height)
        close_y = y + max_height - int((candle['close'] - min_price) / price_range * max_height)
        high_y = y + max_height - int((candle['high'] - min_price) / price_range * max_height)
        low_y = y + max_height - int((candle['low'] - min_price) / price_range * max_height)

        # 심지
        wick_x = x + width // 2
        painter.setPen(QPen(color, 2))
        painter.drawLine(wick_x, high_y, wick_x, low_y)

        # 몸통
        is_bullish = candle['close'] > candle['open']
        body_height = abs(close_y - open_y)
        body_y = min(open_y, close_y)

        painter.setBrush(QBrush(color.lighter(120) if is_bullish else color))
        painter.setPen(QPen(color, 2))

        if body_height < 2:
            body_height = 2
        painter.drawRect(x, body_y, width, body_height)

        # 라벨
        painter.setFont(QFont("맑은 고딕", 9, QFont.Bold))
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(x - 10, y + max_height + 20, label)


    def update_settings(self, block1_settings: dict, block2_settings: dict):
        """
        설정 업데이트 및 다이어그램 재생성

        Args:
            block1_settings: 1번 블록 설정
            block2_settings: 2번 블록 설정
        """
        self.block1_settings.update(block1_settings)
        self.block2_settings.update(block2_settings)

        # 데이터 재생성
        self._generate_sample_data()

        # 화면 갱신
        self.update()
