"""
Block Detection Domain Service
블록 탐지 순수 비즈니스 로직 (DB 독립적)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from domain.entities.price_data import PriceData
from domain.entities.volume_block import VolumeBlock
from core.enums import BlockType, NewHighGrade, PatternType
from core.config import BLOCK_CRITERIA
from core.exceptions import InsufficientDataException, InvalidBlockCriteriaException


class BlockDetectionService:
    """
    블록 탐지 도메인 서비스

    순수 비즈니스 로직만 포함, Repository 의존성 없음
    """

    # 최소 데이터 요구사항
    MIN_DATA_POINTS = 100

    def __init__(self):
        self.criteria = BLOCK_CRITERIA

    def detect_block_1_from_data(
        self,
        stock_id: int,
        price_data_list: List[PriceData],
        settings: Optional[Dict] = None
    ) -> List[VolumeBlock]:
        """
        주가 데이터로부터 1번 블록 탐지

        Args:
            stock_id: 종목 ID
            price_data_list: 주가 데이터 리스트 (시간순 정렬)
            settings: 탐지 설정 (None이면 기본값 사용)

        Returns:
            탐지된 1번 블록 리스트
        """
        if not price_data_list or len(price_data_list) < self.MIN_DATA_POINTS:
            raise InsufficientDataException(
                self.MIN_DATA_POINTS,
                len(price_data_list) if price_data_list else 0
            )

        blocks_1 = []

        # DataFrame으로 변환
        df = self._to_dataframe(price_data_list)

        # 설정 적용 (settings 우선, 없으면 기본값)
        if settings and 'block1' in settings:
            block1_settings = settings['block1']
            min_trading_value = block1_settings.get('min_trading_value', self.criteria['block_1']['min_trading_value'])
            max_period_days = self.criteria['block_1']['max_volume_period_days']
        else:
            min_trading_value = self.criteria['block_1']['min_trading_value']
            max_period_days = self.criteria['block_1']['max_volume_period_days']

        for idx in range(len(df)):
            row = df.iloc[idx]
            current_date = df.index[idx]

            # 조건 1: 거래대금 >= 500억
            if row['trading_value'] < min_trading_value:
                continue

            # 조건 2: max_period_days 이내 최대 거래량
            lookback_start = max(0, idx - max_period_days)
            lookback_data = df.iloc[lookback_start:idx + 1]

            if lookback_data.empty:
                continue

            max_volume = lookback_data['volume'].max()
            if row['volume'] < max_volume:
                continue

            # 신고가 등급 계산
            new_high_grade = self._calculate_new_high_grade(df, idx)

            # 1번 블록 생성
            block = VolumeBlock(
                stock_id=stock_id,
                block_type=BlockType.BLOCK_1,
                date=current_date.date() if hasattr(current_date, 'date') else current_date,
                volume=int(row['volume']),
                trading_value=float(row['trading_value']),
                close_price=float(row['close']),
                new_high_grade=new_high_grade,
                max_volume_period_days=max_period_days
            )

            blocks_1.append(block)

        return blocks_1

    def detect_block_2_from_data(
        self,
        stock_id: int,
        block_1: VolumeBlock,
        price_data_after_block1: List[PriceData],
        settings: Optional[Dict] = None
    ) -> List[VolumeBlock]:
        """
        1번 블록 이후 데이터로부터 2번 블록 탐지

        Args:
            stock_id: 종목 ID
            block_1: 1번 블록
            price_data_after_block1: 1번 블록 이후 주가 데이터
            settings: 탐지 설정 (None이면 기본값 사용)

        Returns:
            탐지된 2번 블록 리스트
        """
        if not price_data_after_block1:
            return []

        blocks_2 = []

        # 설정 적용 (settings 우선, 없으면 기본값)
        if settings and 'block2' in settings:
            block2_settings = settings['block2']
            min_volume_ratio = block2_settings.get('min_volume_ratio', self.criteria['block_2']['volume_ratio_min'])
            max_days = self.criteria['block_2']['max_days_from_block1']
            min_trading_value = block2_settings.get('min_trading_value')
        else:
            min_volume_ratio = self.criteria['block_2']['volume_ratio_min']
            max_days = self.criteria['block_2']['max_days_from_block1']
            min_trading_value = None

        for price in price_data_after_block1:
            # 기간 체크
            days_from_block1 = (price.date - block_1.date).days
            if days_from_block1 > max_days:
                break

            # 거래량 비율 체크
            volume_ratio = price.volume / block_1.volume
            if min_volume_ratio and volume_ratio < min_volume_ratio:
                continue

            # 거래대금 처리 (None일 경우 계산)
            trading_value = price.trading_value if price.trading_value else price.calculate_trading_value()

            # 거래대금 조건 체크
            if min_trading_value and trading_value < min_trading_value:
                continue

            # 패턴 분류 (간단 버전 - 실제로는 더 많은 데이터 필요)
            pattern_type = PatternType.D_ONLY  # 기본값

            # 2번 블록 생성
            # NOTE: parent_block_id는 이 서비스를 호출하는 상위 계층에서 설정해야 함
            block = VolumeBlock(
                stock_id=stock_id,
                block_type=BlockType.BLOCK_2,
                date=price.date,
                volume=price.volume,
                trading_value=trading_value,
                close_price=price.close,
                parent_block_id=block_1.id,  # 아직 저장 전이면 None일 수 있음
                days_from_parent=days_from_block1,
                volume_ratio=volume_ratio,
                pattern_type=pattern_type
            )

            blocks_2.append(block)

        return blocks_2

    def _calculate_new_high_grade(
        self,
        df: pd.DataFrame,
        current_idx: int
    ) -> NewHighGrade:
        """
        신고가 등급 계산

        S: 역사적 신고가 (전체)
        A: 10년래 신고가
        B: 5년래 신고가
        C: 2년래 신고가
        D: 1년래 신고가
        E: 6개월래 신고가
        F: 해당없음
        """
        current_date = df.index[current_idx]
        current_high = df.iloc[current_idx]['high']

        periods = {
            NewHighGrade.S: None,  # 전체
            NewHighGrade.A: 3650,  # 10년
            NewHighGrade.B: 1825,  # 5년
            NewHighGrade.C: 730,   # 2년
            NewHighGrade.D: 365,   # 1년
            NewHighGrade.E: 180,   # 6개월
        }

        for grade, days in periods.items():
            if days is None:
                # 전체 기간
                lookback_data = df.iloc[:current_idx + 1]
            else:
                lookback_start = max(0, current_idx - days)
                lookback_data = df.iloc[lookback_start:current_idx + 1]

            if lookback_data.empty:
                continue

            max_high = lookback_data['high'].max()

            # 현재 고가가 과거 최대 고가 이상이면 해당 등급
            if current_high >= max_high:
                return grade

        return NewHighGrade.F

    def _to_dataframe(self, price_data_list: List[PriceData]) -> pd.DataFrame:
        """
        PriceData 리스트 → DataFrame 변환

        Raises:
            ValueError: 변환 실패 시
        """
        try:
            data = []
            for price in price_data_list:
                # trading_value가 None이면 계산
                trading_value = (
                    price.trading_value if price.trading_value
                    else price.calculate_trading_value()
                )

                data.append({
                    'date': price.date,
                    'open': price.open,
                    'high': price.high,
                    'low': price.low,
                    'close': price.close,
                    'volume': price.volume,
                    'trading_value': trading_value
                })

            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()

            return df

        except Exception as e:
            raise ValueError(f"Failed to convert price data to DataFrame: {str(e)}")

    def calculate_support_levels(
        self,
        block_2: VolumeBlock,
        price_data: List[PriceData]
    ) -> List[Dict[str, any]]:
        """
        지지선 계산 (2번 블록 기준)

        Args:
            block_2: 2번 블록
            price_data: 주가 데이터 리스트

        Returns:
            [{'level': 1, 'price': 10000.0, 'label': 'S1'}, ...]
        """
        # 간단한 구현 - 실제로는 더 복잡한 알고리즘 필요
        support_levels: List[Dict[str, any]] = []

        if not price_data:
            return support_levels

        try:
            df = self._to_dataframe(price_data)

            # 2번 블록 날짜까지의 데이터 필터링
            block_date_data = df[df.index <= pd.Timestamp(block_2.date)]

            if block_date_data.empty:
                return support_levels

            # S1: 2번 블록 저가
            s1_price = float(block_date_data.iloc[-1]['low'])
            support_levels.append({
                'level': 1,
                'price': s1_price,
                'label': 'S1 (Block2 Low)'
            })

            # TODO: S2, S3 추가 구현 필요
            # S2: 1번 블록 저가 (필요시)
            # S3: 60일 이동평균

        except Exception as e:
            # 계산 실패 시 빈 리스트 반환
            pass

        return support_levels
