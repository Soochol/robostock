"""
Block Detector Service
거래량 블록 탐지 알고리즘
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
import logging

from infrastructure.database import get_session
from infrastructure.database.models import Stock, PriceData, VolumeBlock
from core.enums import BlockType, NewHighGrade, PatternType
from core.config import BLOCK_CRITERIA

logger = logging.getLogger(__name__)


class BlockDetector:
    """
    거래량 블록 탐지 서비스

    알고리즘:
    1. 1번 블록 탐지: 최대거래량 + 신고가 조건
    2. 2번 블록 탐지: 1번 블록 이후 거래량 조건
    3. 지지선 계산
    """

    def __init__(self):
        self.detected_blocks = []

    def detect_block_1(
        self,
        stock_id: int,
        start_date: datetime,
        end_date: datetime,
        settings: dict = None
    ) -> List[Dict]:
        """
        1번 블록 탐지

        조건:
        - 거래대금 >= 500억원
        - 해당 날짜 기준 2년 이내 최대 거래량
        - 신고가 등급 계산

        Returns:
            [{date, volume, trading_value, close_price, new_high_grade, ...}, ...]
        """
        blocks_1 = []

        with get_session() as session:
            # 주가 데이터 조회
            price_data = session.query(PriceData).filter(
                PriceData.stock_id == stock_id,
                PriceData.date >= start_date,
                PriceData.date <= end_date
            ).order_by(PriceData.date).all()

            if not price_data:
                return blocks_1  # 데이터 없으면 조용히 스킵

            print(f"[DEBUG] Stock {stock_id}: Found {len(price_data)} price records")

            # DataFrame으로 변환
            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume,
                'trading_value': p.trading_value
            } for p in price_data])

            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # 샘플 데이터 출력 (첫 3개, 최대 거래대금 3개)
            print(f"[DEBUG] Stock {stock_id}: Sample first 3 records:")
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                print(f"  {df.index[i].date()}: "
                      f"Vol={row['volume']:,}, "
                      f"Trading={row['trading_value']/1e8:.1f}억")

            # 최대 거래대금 상위 3개
            top_trading = df.nlargest(3, 'trading_value')
            print(f"[DEBUG] Stock {stock_id}: Top 3 by trading value:")
            for idx, row in top_trading.iterrows():
                print(f"  {idx.date()}: "
                      f"Vol={row['volume']:,}, "
                      f"Trading={row['trading_value']/1e8:.1f}억")

            # 1번 블록 조건 체크 (설정값 또는 기본값 사용)
            if settings and 'block1' in settings:
                block1_settings = settings['block1']
                min_trading_value = block1_settings.get('min_trading_value', BLOCK_CRITERIA['block_1']['min_trading_value'])
                if min_trading_value is None:
                    min_trading_value = 0  # 조건 비활성화
            else:
                min_trading_value = BLOCK_CRITERIA['block_1']['min_trading_value']

            max_period_days = BLOCK_CRITERIA['block_1']['max_volume_period_days']

            print(f"[DEBUG] Stock {stock_id}: Criteria - "
                  f"min_trading_value={min_trading_value/1e8:.0f}억, "
                  f"max_period={max_period_days}days")
            if settings:
                print(f"[DEBUG] Stock {stock_id}: Using custom settings: {settings}")

            candidates = 0
            failed_trading = 0
            failed_volume = 0

            for idx, row in df.iterrows():
                # 조건 1: 거래대금 >= 500억원
                if row['trading_value'] < min_trading_value:
                    failed_trading += 1
                    continue

                candidates += 1

                # 조건 2: 2년 이내 최대 거래량 확인
                lookback_start = idx - timedelta(days=max_period_days)
                lookback_data = df[lookback_start:idx]

                if lookback_data.empty:
                    continue

                max_volume_in_period = lookback_data['volume'].max()
                if row['volume'] < max_volume_in_period:
                    failed_volume += 1
                    continue

                # 신고가 등급 계산
                new_high_grade = self._calculate_new_high_grade(df, idx)

                # 1번 블록 발견
                block_info = {
                    'date': idx.date(),
                    'volume': int(row['volume']),
                    'trading_value': float(row['trading_value']),
                    'close_price': float(row['close']),
                    'new_high_grade': new_high_grade,
                    'max_volume_period_days': max_period_days
                }

                blocks_1.append(block_info)
                print(f"[DEBUG] Stock {stock_id}: Block 1 found on {idx.date()} - "
                      f"Trading={row['trading_value']/1e8:.0f}억")

            print(f"[DEBUG] Stock {stock_id}: Candidates={candidates}, "
                  f"Failed(trading)={failed_trading}, "
                  f"Failed(volume)={failed_volume}, "
                  f"Found={len(blocks_1)}")

        return blocks_1

    def _calculate_new_high_grade(self, df: pd.DataFrame, current_date) -> NewHighGrade:
        """
        신고가 등급 계산

        S: 역사적 신고가 (전체 데이터)
        A: 10년래 신고가
        B: 5년래 신고가
        C: 2년래 신고가
        D: 1년래 신고가
        E: 6개월래 신고가
        F: 해당없음
        """
        current_price = df.loc[current_date, 'high']

        # 각 기간별 최고가 확인
        periods = {
            NewHighGrade.S: None,  # 전체
            NewHighGrade.A: timedelta(days=3650),  # 10년
            NewHighGrade.B: timedelta(days=1825),  # 5년
            NewHighGrade.C: timedelta(days=730),   # 2년
            NewHighGrade.D: timedelta(days=365),   # 1년
            NewHighGrade.E: timedelta(days=180),   # 6개월
        }

        for grade, period in periods.items():
            if period is None:
                # 전체 기간
                lookback_data = df[:current_date]
            else:
                lookback_start = current_date - period
                lookback_data = df[lookback_start:current_date]

            if lookback_data.empty:
                continue

            max_high = lookback_data['high'].max()

            if current_price >= max_high:
                return grade

        return NewHighGrade.F

    def detect_block_2(
        self,
        stock_id: int,
        block_1_date: datetime,
        block_1_volume: int,
        settings: dict = None
    ) -> List[Dict]:
        """
        2번 블록 탐지

        조건:
        - 1번 블록 이후 180일 이내
        - 거래량 >= 1번 블록의 80%
        - D/D+1/D+2 패턴 분류

        Returns:
            [{date, volume, trading_value, close_price, pattern_type, ...}, ...]
        """
        blocks_2 = []

        # 설정값 또는 기본값 사용
        if settings and 'block2' in settings:
            block2_settings = settings['block2']
            max_days = BLOCK_CRITERIA['block_2']['max_days_from_block1']
            min_volume_ratio = block2_settings.get('min_volume_ratio', BLOCK_CRITERIA['block_2']['volume_ratio_min'])
            if min_volume_ratio is None:
                min_volume_ratio = 0  # 조건 비활성화
            min_trading_value = block2_settings.get('min_trading_value')
        else:
            max_days = BLOCK_CRITERIA['block_2']['max_days_from_block1']
            min_volume_ratio = BLOCK_CRITERIA['block_2']['volume_ratio_min']
            min_trading_value = None

        end_date = block_1_date + timedelta(days=max_days)

        with get_session() as session:
            # 1번 블록 이후 데이터 조회
            price_data = session.query(PriceData).filter(
                PriceData.stock_id == stock_id,
                PriceData.date > block_1_date,
                PriceData.date <= end_date
            ).order_by(PriceData.date).all()

            for idx, price in enumerate(price_data):
                # 거래량 조건 체크
                volume_ratio = price.volume / block_1_volume

                if volume_ratio >= min_volume_ratio:
                    # 거래대금 조건 체크
                    if min_trading_value and price.trading_value < min_trading_value:
                        continue

                    # 패턴 분류
                    pattern_type = self._classify_pattern(price_data, idx)

                    days_from_block1 = (price.date - block_1_date).days

                    block_info = {
                        'date': price.date,
                        'volume': price.volume,
                        'trading_value': price.trading_value,
                        'close_price': price.close,
                        'volume_ratio': volume_ratio,
                        'days_from_block1': days_from_block1,
                        'pattern_type': pattern_type
                    }

                    blocks_2.append(block_info)
                    logger.info(f"Block 2 found: {price.date} - Volume ratio {volume_ratio*100:.1f}%, Pattern {pattern_type.value}")

        return blocks_2

    def _classify_pattern(self, price_data: List[PriceData], current_idx: int) -> PatternType:
        """
        2번 블록 패턴 분류

        D: 당일만 거래량 급증
        D+D+1: 당일 + 다음날 연속 거래량
        D+D+2: 당일 + 2일 후 거래량
        D+D+1+D+2: 3일 연속 거래량
        """
        if current_idx >= len(price_data):
            return PatternType.D_ONLY

        current = price_data[current_idx]
        current_volume = current.volume

        # 평균 거래량 계산 (이전 20일)
        if current_idx >= 20:
            prev_20_volumes = [price_data[i].volume for i in range(current_idx - 20, current_idx)]
            avg_volume = np.mean(prev_20_volumes)
        else:
            avg_volume = current_volume * 0.5

        threshold = avg_volume * 0.8  # 평균의 80% 이상

        # D+1 확인
        has_d1 = False
        if current_idx + 1 < len(price_data):
            next_volume = price_data[current_idx + 1].volume
            if next_volume >= threshold:
                has_d1 = True

        # D+2 확인
        has_d2 = False
        if current_idx + 2 < len(price_data):
            d2_volume = price_data[current_idx + 2].volume
            if d2_volume >= threshold:
                has_d2 = True

        # 패턴 분류
        if has_d1 and has_d2:
            return PatternType.D_D1_D2
        elif has_d1:
            return PatternType.D_D1
        elif has_d2:
            return PatternType.D_D2
        else:
            return PatternType.D_ONLY

    def save_blocks_to_db(
        self,
        stock_id: int,
        blocks_1: List[Dict],
        blocks_2: List[Dict] = None
    ) -> Tuple[int, int]:
        """
        탐지된 블록을 DB에 저장

        Returns:
            (저장된 1번 블록 수, 저장된 2번 블록 수)
        """
        saved_1 = 0
        saved_2 = 0

        with get_session() as session:
            # 1번 블록 저장
            for block_info in blocks_1:
                # 기존 블록 확인
                existing = session.query(VolumeBlock).filter_by(
                    stock_id=stock_id,
                    block_type=BlockType.BLOCK_1,
                    date=block_info['date']
                ).first()

                if existing:
                    continue  # 이미 존재

                new_block = VolumeBlock(
                    stock_id=stock_id,
                    block_type=BlockType.BLOCK_1,
                    date=block_info['date'],
                    volume=block_info['volume'],
                    trading_value=block_info['trading_value'],
                    close_price=block_info['close_price'],
                    new_high_grade=block_info['new_high_grade'],
                    max_volume_period_days=block_info['max_volume_period_days']
                )
                session.add(new_block)
                saved_1 += 1

            # 2번 블록 저장 (있는 경우)
            if blocks_2:
                for block_info in blocks_2:
                    existing = session.query(VolumeBlock).filter_by(
                        stock_id=stock_id,
                        block_type=BlockType.BLOCK_2,
                        date=block_info['date']
                    ).first()

                    if existing:
                        continue

                    new_block = VolumeBlock(
                        stock_id=stock_id,
                        block_type=BlockType.BLOCK_2,
                        date=block_info['date'],
                        volume=block_info['volume'],
                        trading_value=block_info['trading_value'],
                        close_price=block_info['close_price'],
                        days_from_parent=block_info['days_from_block1'],
                        volume_ratio=block_info['volume_ratio'],
                        pattern_type=block_info['pattern_type']
                    )
                    session.add(new_block)
                    saved_2 += 1

        return saved_1, saved_2

    def detect_all_blocks(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        settings: dict = None
    ) -> Dict:
        """
        종목의 모든 블록 탐지

        Args:
            stock_code: 종목 코드
            start_date: 시작 날짜
            end_date: 종료 날짜
            settings: 탐지 설정 (None이면 기본값 사용)

        Returns:
            {
                'blocks_1': [...],
                'blocks_2': [...],
                'stock_id': int
            }
        """
        with get_session() as session:
            stock = session.query(Stock).filter_by(code=stock_code).first()
            if not stock:
                logger.warning(f"Stock {stock_code} not found")
                return {'blocks_1': [], 'blocks_2': [], 'stock_id': None}

            # stock_id를 변수에 저장 (세션 종료 후에도 사용 가능)
            stock_id = stock.id
            stock_name = stock.name

            # 1번 블록 탐지 (settings 전달)
            logger.info(f"{stock_name} ({stock_code}) - Block 1 detection started...")
            if settings:
                logger.info(f"Using custom settings for detection")
            blocks_1 = self.detect_block_1(stock_id, start_date, end_date, settings)

            logger.info(f"Found {len(blocks_1)} Block 1")

            # 각 1번 블록에 대해 2번 블록 탐지 (settings 전달)
            all_blocks_2 = []
            for block_1 in blocks_1:
                blocks_2 = self.detect_block_2(
                    stock_id,
                    block_1['date'],
                    block_1['volume'],
                    settings
                )
                all_blocks_2.extend(blocks_2)

            logger.info(f"Found {len(all_blocks_2)} Block 2")

        # DB 저장 (세션 밖에서 실행, 내부에서 새 세션 생성)
        saved_1, saved_2 = self.save_blocks_to_db(stock_id, blocks_1, all_blocks_2)
        logger.info(f"DB saved: Block 1 {saved_1}, Block 2 {saved_2}")

        return {
            'blocks_1': blocks_1,
            'blocks_2': all_blocks_2,
            'stock_id': stock_id
        }


# 전역 블록 탐지 인스턴스
block_detector = BlockDetector()
