"""
Volume Block Repository Interface
거래량 블록 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from domain.entities.volume_block import VolumeBlock
from core.enums import BlockType


class BlockRepository(ABC):
    """거래량 블록 Repository 인터페이스"""

    @abstractmethod
    def get_by_id(self, block_id: int) -> Optional[VolumeBlock]:
        """ID로 블록 조회"""
        pass

    @abstractmethod
    def get_by_stock(
        self,
        stock_id: int,
        block_type: Optional[BlockType] = None
    ) -> List[VolumeBlock]:
        """종목별 블록 조회 (타입 필터링 가능)"""
        pass

    @abstractmethod
    def get_by_stock_and_date(
        self,
        stock_id: int,
        target_date: date,
        block_type: Optional[BlockType] = None
    ) -> Optional[VolumeBlock]:
        """특정 날짜의 블록 조회"""
        pass

    @abstractmethod
    def get_by_date_range(
        self,
        stock_id: int,
        start_date: date,
        end_date: date,
        block_type: Optional[BlockType] = None
    ) -> List[VolumeBlock]:
        """기간별 블록 조회"""
        pass

    @abstractmethod
    def save(self, block: VolumeBlock) -> VolumeBlock:
        """블록 저장"""
        pass

    @abstractmethod
    def save_bulk(self, blocks: List[VolumeBlock]) -> int:
        """대량 블록 저장"""
        pass

    @abstractmethod
    def exists(
        self,
        stock_id: int,
        target_date: date,
        block_type: BlockType
    ) -> bool:
        """블록 존재 여부 확인"""
        pass

    @abstractmethod
    def delete(self, block_id: int) -> bool:
        """블록 삭제"""
        pass

    @abstractmethod
    def delete_by_stock(self, stock_id: int) -> int:
        """종목의 모든 블록 삭제"""
        pass

    @abstractmethod
    def count_by_type(
        self,
        stock_id: int,
        block_type: BlockType
    ) -> int:
        """타입별 블록 수 카운트"""
        pass
