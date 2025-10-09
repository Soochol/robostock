"""
Volume Block Entity
거래량 블록 도메인 엔티티
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from core.enums import BlockType, NewHighGrade, PatternType


@dataclass
class VolumeBlock:
    """
    거래량 블록 엔티티

    순수 비즈니스 객체
    """

    stock_id: int
    block_type: BlockType
    date: date
    volume: int
    trading_value: float
    close_price: float

    # 1번 블록 전용
    new_high_grade: Optional[NewHighGrade] = None
    max_volume_period_days: Optional[int] = None

    # 2번 블록 전용
    parent_block_id: Optional[int] = None
    days_from_parent: Optional[int] = None
    volume_ratio: Optional[float] = None
    pattern_type: Optional[PatternType] = None

    # Range 정보
    range_end_date: Optional[date] = None
    range_duration_days: Optional[int] = None
    range_high: Optional[float] = None
    range_high_date: Optional[date] = None
    range_low: Optional[float] = None
    range_low_date: Optional[date] = None
    range_avg_volume: Optional[int] = None
    ma60_at_start: Optional[float] = None
    ma60_at_end: Optional[float] = None
    range_end_reason: Optional[str] = None

    # 시장 대비 성과
    market_index: Optional[str] = None
    range_return: Optional[float] = None
    index_return: Optional[float] = None
    relative_return: Optional[float] = None
    beta: Optional[float] = None
    alpha: Optional[float] = None
    outperformance: Optional[bool] = None

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """유효성 검증"""
        # 공통 필드 검증
        if self.stock_id <= 0:
            raise ValueError("Invalid stock_id")

        if not isinstance(self.block_type, BlockType):
            raise ValueError(f"Invalid block_type: {self.block_type}")

        if self.volume <= 0:
            raise ValueError("Volume must be positive")

        if self.trading_value <= 0:
            raise ValueError("Trading value must be positive")

        if self.close_price <= 0:
            raise ValueError("Close price must be positive")

        # 1번 블록 검증
        if self.block_type == BlockType.BLOCK_1:
            if self.new_high_grade is None:
                raise ValueError("Block 1 requires new_high_grade")
            if not isinstance(self.new_high_grade, NewHighGrade):
                raise ValueError(f"Invalid new_high_grade: {self.new_high_grade}")

        # 2번 블록 검증
        if self.block_type == BlockType.BLOCK_2:
            if self.parent_block_id is None:
                raise ValueError("Block 2 requires parent_block_id")
            if self.volume_ratio is None or self.volume_ratio <= 0:
                raise ValueError("Block 2 requires valid volume_ratio")
            # pattern_type은 Optional이지만 있으면 검증
            if self.pattern_type is not None and not isinstance(self.pattern_type, PatternType):
                raise ValueError(f"Invalid pattern_type: {self.pattern_type}")

        # 3번, 4번 블록 검증
        if self.block_type in [BlockType.BLOCK_3, BlockType.BLOCK_4]:
            if self.parent_block_id is None:
                raise ValueError(f"Block {self.block_type.value} requires parent_block_id")

    def is_block_1(self) -> bool:
        """1번 블록 여부"""
        return self.block_type == BlockType.BLOCK_1

    def is_block_2(self) -> bool:
        """2번 블록 여부"""
        return self.block_type == BlockType.BLOCK_2

    def is_high_grade(self) -> bool:
        """고등급 신고가 여부 (S, A, B)"""
        if self.new_high_grade is None:
            return False
        return self.new_high_grade in [
            NewHighGrade.S,
            NewHighGrade.A,
            NewHighGrade.B
        ]

    def is_block_3(self) -> bool:
        """3번 블록 여부"""
        return self.block_type == BlockType.BLOCK_3

    def is_block_4(self) -> bool:
        """4번 블록 여부"""
        return self.block_type == BlockType.BLOCK_4

    def get_trading_value_billion(self) -> float:
        """거래대금 (억원)"""
        return self.trading_value / 100_000_000

    def has_pattern(self) -> bool:
        """2번 블록 패턴 존재 여부"""
        return self.pattern_type is not None

    def __repr__(self) -> str:
        return (
            f"<VolumeBlock stock_id={self.stock_id} "
            f"type={self.block_type.value} date={self.date}>"
        )
