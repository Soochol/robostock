"""
Detect Blocks Use Case
블록 탐지 유스케이스 (Repository 패턴 활용)
"""

from typing import Dict, List
from datetime import datetime, date

from domain.repositories.stock_repository import StockRepository
from domain.repositories.price_data_repository import PriceDataRepository
from domain.repositories.block_repository import BlockRepository
from domain.services.block_detection_service import BlockDetectionService
from domain.entities.volume_block import VolumeBlock
from core.enums import BlockType
from core.exceptions import EntityNotFoundException, InsufficientDataException


class DetectBlocksUseCase:
    """
    블록 탐지 유스케이스

    책임:
    - Repository를 통해 데이터 조회
    - Domain Service를 통해 블록 탐지
    - 결과를 Repository를 통해 저장
    """

    def __init__(
        self,
        stock_repo: StockRepository,
        price_data_repo: PriceDataRepository,
        block_repo: BlockRepository
    ):
        self._stock_repo = stock_repo
        self._price_data_repo = price_data_repo
        self._block_repo = block_repo
        self._detection_service = BlockDetectionService()

    def execute(
        self,
        stock_code: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        블록 탐지 실행

        Args:
            stock_code: 종목 코드
            start_date: 시작일
            end_date: 종료일

        Returns:
            {
                'stock_id': int,
                'stock_name': str,
                'blocks_1_count': int,
                'blocks_2_count': int,
                'blocks_1': List[VolumeBlock],
                'blocks_2': List[VolumeBlock]
            }
        """
        # 1. 종목 조회
        stock = self._stock_repo.get_by_code(stock_code)
        if not stock:
            raise EntityNotFoundException("Stock", stock_code)

        # 2. 주가 데이터 조회
        price_data_list = self._price_data_repo.get_by_stock_range(
            stock.id,
            start_date,
            end_date
        )

        if not price_data_list:
            raise InsufficientDataException(1, 0)

        # 3. 1번 블록 탐지 (Domain Service 활용)
        blocks_1 = self._detection_service.detect_block_1_from_data(
            stock.id,
            price_data_list
        )

        # 4. 1번 블록 저장
        saved_blocks_1 = []
        for block in blocks_1:
            saved_block = self._block_repo.save(block)
            saved_blocks_1.append(saved_block)

        # 5. 각 1번 블록에 대해 2번 블록 탐지
        all_blocks_2 = []
        for block_1 in saved_blocks_1:
            # 1번 블록 이후 데이터 조회
            price_data_after = self._price_data_repo.get_by_stock_range(
                stock.id,
                block_1.date,
                end_date
            )

            # 2번 블록 탐지
            blocks_2 = self._detection_service.detect_block_2_from_data(
                stock.id,
                block_1,
                price_data_after
            )

            # 2번 블록 저장
            for block in blocks_2:
                saved_block = self._block_repo.save(block)
                all_blocks_2.append(saved_block)

        # 6. 결과 반환
        return {
            'stock_id': stock.id,
            'stock_name': stock.name,
            'stock_code': stock.code,
            'blocks_1_count': len(saved_blocks_1),
            'blocks_2_count': len(all_blocks_2),
            'blocks_1': saved_blocks_1,
            'blocks_2': all_blocks_2
        }

    def execute_bulk(
        self,
        stock_codes: List[str],
        start_date: date,
        end_date: date,
        progress_callback=None
    ) -> List[Dict]:
        """
        여러 종목에 대해 블록 탐지

        Args:
            stock_codes: 종목 코드 리스트
            start_date: 시작일
            end_date: 종료일
            progress_callback: 진행 상황 콜백

        Returns:
            각 종목별 탐지 결과 리스트
        """
        results = []

        for idx, stock_code in enumerate(stock_codes):
            try:
                result = self.execute(stock_code, start_date, end_date)
                results.append(result)

                if progress_callback:
                    progress_callback(
                        idx + 1,
                        len(stock_codes),
                        f"{result['stock_name']} 완료"
                    )

            except Exception as e:
                print(f"[ERROR] {stock_code} 블록 탐지 실패: {e}")
                if progress_callback:
                    progress_callback(
                        idx + 1,
                        len(stock_codes),
                        f"{stock_code} 실패"
                    )

        return results
