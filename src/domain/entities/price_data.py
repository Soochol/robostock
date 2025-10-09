"""
Price Data Entity
주가 데이터 도메인 엔티티
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class PriceData:
    """
    주가 데이터 엔티티 (OHLCV)

    순수 비즈니스 객체
    """

    stock_id: int
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    trading_value: Optional[float] = None
    market_cap: Optional[float] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """유효성 검증"""
        if self.stock_id <= 0:
            raise ValueError("Invalid stock_id")

        if self.open <= 0 or self.high <= 0 or self.low <= 0 or self.close <= 0:
            raise ValueError("Price must be positive")

        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than Low ({self.low})")

        if self.high < self.open or self.high < self.close:
            raise ValueError("High must be greater than or equal to Open and Close")

        if self.low > self.open or self.low > self.close:
            raise ValueError("Low must be less than or equal to Open and Close")

        if self.volume < 0:
            raise ValueError("Volume cannot be negative")

    def price_change(self) -> float:
        """가격 변화량"""
        return self.close - self.open

    def price_change_pct(self) -> float:
        """가격 변화율 (%)"""
        if self.open == 0:
            return 0.0
        return (self.close - self.open) / self.open * 100

    def is_up(self) -> bool:
        """상승 여부"""
        return self.close > self.open

    def is_down(self) -> bool:
        """하락 여부"""
        return self.close < self.open

    def body_size(self) -> float:
        """캔들 몸통 크기"""
        return abs(self.close - self.open)

    def upper_shadow(self) -> float:
        """위꼬리 길이"""
        return self.high - max(self.open, self.close)

    def lower_shadow(self) -> float:
        """아래꼬리 길이"""
        return min(self.open, self.close) - self.low

    def total_range(self) -> float:
        """전체 가격 범위"""
        return self.high - self.low

    def calculate_trading_value(self) -> float:
        """거래대금 계산 (거래량 × 종가)"""
        return self.volume * self.close

    def get_trading_value_billion(self) -> float:
        """거래대금 (억원)"""
        trading_val = self.trading_value if self.trading_value else self.calculate_trading_value()
        return trading_val / 100_000_000

    def __repr__(self) -> str:
        return (
            f"<PriceData stock_id={self.stock_id} "
            f"date={self.date} close={self.close} volume={self.volume}>"
        )
