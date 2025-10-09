"""
Stock Entity
종목 도메인 엔티티 (순수 비즈니스 로직)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from core.enums import MarketType


@dataclass
class Stock:
    """
    종목 엔티티

    ORM 모델과 분리된 순수 비즈니스 객체
    """

    code: str
    name: str
    market: MarketType
    sector: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """유효성 검증"""
        # 종목코드 검증: 6자리 숫자
        if not self.code:
            raise ValueError("Stock code is required")

        if len(self.code) != 6:
            raise ValueError(f"Stock code must be 6 digits: {self.code}")

        if not self.code.isdigit():
            raise ValueError(f"Stock code must contain only digits: {self.code}")

        # 종목명 검증
        if not self.name or not self.name.strip():
            raise ValueError("Stock name is required")

        # 시장 타입 검증
        if not isinstance(self.market, MarketType):
            raise ValueError(f"Invalid market type: {self.market}")

    def is_kospi(self) -> bool:
        """KOSPI 종목 여부"""
        return self.market == MarketType.KOSPI

    def is_kosdaq(self) -> bool:
        """KOSDAQ 종목 여부"""
        return self.market == MarketType.KOSDAQ

    def __str__(self) -> str:
        return f"{self.name}({self.code})"

    def __repr__(self) -> str:
        return f"<Stock code={self.code} name={self.name} market={self.market.value}>"
