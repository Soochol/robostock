"""
DB 데이터 확인 스크립트
"""
import sys
import os

# src 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.database import get_session
from data.models import Stock, PriceData, VolumeBlock
from sqlalchemy import func

def check_database():
    """DB 데이터 확인"""
    print("=" * 60)
    print("RoboStock Database Status")
    print("=" * 60)

    with get_session() as session:
        # 1. 종목 수
        stock_count = session.query(Stock).count()
        print(f"\n[1] Stock Table:")
        print(f"    Total stocks: {stock_count}")

        if stock_count > 0:
            # 시장별 종목 수
            kospi_count = session.query(Stock).filter(Stock.market == 'KOSPI').count()
            kosdaq_count = session.query(Stock).filter(Stock.market == 'KOSDAQ').count()
            print(f"    - KOSPI: {kospi_count}")
            print(f"    - KOSDAQ: {kosdaq_count}")

            # 샘플 종목 5개
            sample_stocks = session.query(Stock).limit(5).all()
            print(f"\n    Sample stocks:")
            for stock in sample_stocks:
                print(f"      - {stock.name} ({stock.code}) [{stock.market}]")

        # 2. 가격 데이터
        price_count = session.query(PriceData).count()
        print(f"\n[2] PriceData Table:")
        print(f"    Total records: {price_count:,}")

        if price_count > 0:
            # 날짜 범위
            min_date = session.query(func.min(PriceData.date)).scalar()
            max_date = session.query(func.max(PriceData.date)).scalar()
            print(f"    Date range: {min_date} ~ {max_date}")

            # 종목별 데이터 수
            stock_with_data = session.query(
                Stock.name,
                Stock.code,
                func.count(PriceData.id).label('count')
            ).join(PriceData).group_by(Stock.id).limit(5).all()

            print(f"\n    Sample data by stock:")
            for name, code, count in stock_with_data:
                print(f"      - {name} ({code}): {count} records")

        # 3. 블록 데이터
        block_count = session.query(VolumeBlock).count()
        print(f"\n[3] VolumeBlock Table:")
        print(f"    Total blocks: {block_count}")

        if block_count > 0:
            # 블록 타입별
            block_1_count = session.query(VolumeBlock).filter(
                VolumeBlock.block_type == 'BLOCK_1'
            ).count()
            block_2_count = session.query(VolumeBlock).filter(
                VolumeBlock.block_type == 'BLOCK_2'
            ).count()
            print(f"    - Block 1: {block_1_count}")
            print(f"    - Block 2: {block_2_count}")

            # 샘플 블록
            sample_blocks = session.query(VolumeBlock).limit(5).all()
            print(f"\n    Sample blocks:")
            for block in sample_blocks:
                stock = session.query(Stock).filter(Stock.id == block.stock_id).first()
                if stock:
                    print(f"      - {stock.name} ({stock.code}): {block.block_type} on {block.date}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"[ERROR] Failed to check database: {e}")
        import traceback
        traceback.print_exc()
