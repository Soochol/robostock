"""
블록 탐지 결과 DB 저장 확인 스크립트
"""

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from infrastructure.database import get_session
from infrastructure.database.models import VolumeBlock, Stock, BlockType
from sqlalchemy import func, desc

def check_blocks():
    """DB에 저장된 블록 확인"""
    with get_session() as session:
        # 1번 블록 통계
        block1_count = session.query(VolumeBlock).filter_by(
            block_type=BlockType.BLOCK_1
        ).count()

        # 2번 블록 통계
        block2_count = session.query(VolumeBlock).filter_by(
            block_type=BlockType.BLOCK_2
        ).count()

        print("=" * 60)
        print("블록 탐지 결과 DB 저장 확인")
        print("=" * 60)
        print(f"\n📊 전체 통계:")
        print(f"  - 1번 블록: {block1_count}개")
        print(f"  - 2번 블록: {block2_count}개")
        print(f"  - 총합: {block1_count + block2_count}개")

        # 종목별 블록 수 (상위 10개)
        print(f"\n📈 종목별 1번 블록 Top 10:")
        block1_by_stock = session.query(
            Stock.name,
            Stock.code,
            func.count(VolumeBlock.id).label('count')
        ).join(
            VolumeBlock, Stock.id == VolumeBlock.stock_id
        ).filter(
            VolumeBlock.block_type == BlockType.BLOCK_1
        ).group_by(
            Stock.id
        ).order_by(
            desc('count')
        ).limit(10).all()

        for idx, (name, code, count) in enumerate(block1_by_stock, 1):
            print(f"  {idx:2d}. {name} ({code}): {count}개")

        print(f"\n📈 종목별 2번 블록 Top 10:")
        block2_by_stock = session.query(
            Stock.name,
            Stock.code,
            func.count(VolumeBlock.id).label('count')
        ).join(
            VolumeBlock, Stock.id == VolumeBlock.stock_id
        ).filter(
            VolumeBlock.block_type == BlockType.BLOCK_2
        ).group_by(
            Stock.id
        ).order_by(
            desc('count')
        ).limit(10).all()

        for idx, (name, code, count) in enumerate(block2_by_stock, 1):
            print(f"  {idx:2d}. {name} ({code}): {count}개")

        # 최근 저장된 블록 5개
        print(f"\n🕐 최근 저장된 1번 블록 (5개):")
        recent_block1 = session.query(
            VolumeBlock, Stock
        ).join(
            Stock, VolumeBlock.stock_id == Stock.id
        ).filter(
            VolumeBlock.block_type == BlockType.BLOCK_1
        ).order_by(
            desc(VolumeBlock.date)
        ).limit(5).all()

        for block, stock in recent_block1:
            print(f"  - {stock.name} ({stock.code}) | {block.date.date()} | "
                  f"거래량: {block.volume:,}")

        print(f"\n🕐 최근 저장된 2번 블록 (5개):")
        recent_block2 = session.query(
            VolumeBlock, Stock
        ).join(
            Stock, VolumeBlock.stock_id == Stock.id
        ).filter(
            VolumeBlock.block_type == BlockType.BLOCK_2
        ).order_by(
            desc(VolumeBlock.date)
        ).limit(5).all()

        for block, stock in recent_block2:
            print(f"  - {stock.name} ({stock.code}) | {block.date.date()} | "
                  f"거래량: {block.volume:,} | 패턴: {block.pattern_type}")

        print("\n" + "=" * 60)

        if block1_count == 0 and block2_count == 0:
            print("⚠️  경고: DB에 저장된 블록이 없습니다!")
            print("   블록 탐지를 실행했는지 확인해주세요.")
        else:
            print("✅ DB에 블록이 정상적으로 저장되어 있습니다!")

        print("=" * 60)

if __name__ == "__main__":
    check_blocks()
