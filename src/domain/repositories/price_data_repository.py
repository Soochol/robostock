"""
Price Data Repository Interface
주가 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from domain.entities.price_data import PriceData


class PriceDataRepository(ABC):
    """주가 데이터 Repository 인터페이스"""

    @abstractmethod
    def get_by_stock_and_date(
        self,
        stock_id: int,
        target_date: date
    ) -> Optional[PriceData]:
        """특정 날짜의 주가 데이터 조회"""
        pass

    @abstractmethod
    def get_by_stock_range(
        self,
        stock_id: int,
        start_date: date,
        end_date: date
    ) -> List[PriceData]:
        """기간별 주가 데이터 조회"""
        pass

    @abstractmethod
    def get_latest(self, stock_id: int) -> Optional[PriceData]:
        """최신 주가 데이터 조회"""
        pass

    @abstractmethod
    def get_latest_date(self, stock_id: int) -> Optional[date]:
        """최신 데이터 날짜 조회"""
        pass

    @abstractmethod
    def save(self, price_data: PriceData) -> PriceData:
        """주가 데이터 저장"""
        pass

    @abstractmethod
    def save_bulk(self, price_data_list: List[PriceData]) -> int:
        """대량 주가 데이터 저장"""
        pass

    @abstractmethod
    def exists(self, stock_id: int, target_date: date) -> bool:
        """특정 날짜 데이터 존재 여부"""
        pass

    @abstractmethod
    def delete_by_stock(self, stock_id: int) -> int:
        """종목의 모든 주가 데이터 삭제"""
        pass
