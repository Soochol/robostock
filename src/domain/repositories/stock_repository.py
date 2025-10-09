"""
Stock Repository Interface
종목 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from domain.entities.stock import Stock
from core.enums import MarketType


class StockRepository(ABC):
    """종목 Repository 인터페이스"""

    @abstractmethod
    def get_by_id(self, stock_id: int) -> Optional[Stock]:
        """ID로 종목 조회"""
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Stock]:
        """종목 코드로 조회"""
        pass

    @abstractmethod
    def get_all(self, market: Optional[MarketType] = None) -> List[Stock]:
        """전체 종목 조회 (시장 필터링 가능)"""
        pass

    @abstractmethod
    def save(self, stock: Stock) -> Stock:
        """종목 저장 (생성 또는 업데이트)"""
        pass

    @abstractmethod
    def delete(self, stock_id: int) -> bool:
        """종목 삭제"""
        pass

    @abstractmethod
    def exists(self, code: str) -> bool:
        """종목 코드 존재 여부 확인"""
        pass

    @abstractmethod
    def count(self, market: Optional[MarketType] = None) -> int:
        """종목 수 카운트"""
        pass
