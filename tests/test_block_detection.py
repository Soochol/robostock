"""
블록 탐지 기능 테스트
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.block_detector import block_detector
from data.database import get_session
from data.models import Stock, PriceData, VolumeBlock
from sqlalchemy import text, func

def test_block_detection():
    """블록 탐지 테스트"""
    print("=" * 80)
    print("BLOCK DETECTION TEST")
    print("=" * 80)

    # 데이터가 있는 종목 찾기
    with get_session() as session:
        stocks_with_data = session.execute(text('''
            SELECT s.id, s.code, s.name, COUNT(p.id) as cnt
            FROM stocks s
            JOIN price_data p ON s.id = p.stock_id
            GROUP BY s.id
            HAVING cnt > 100
            LIMIT 5
        ''')).fetchall()

        if not stocks_with_data:
            print("[ERROR] No stocks with price data found!")
            return

        print(f"\n[INFO] Found {len(stocks_with_data)} stocks with price data")
        print("\nTesting block detection on these stocks:")
        print("-" * 80)

        for stock_id, code, name, count in stocks_with_data:
            print(f"  - {name} ({code}): {count} price records")

    print("\n" + "=" * 80)
    print("STARTING DETECTION")
    print("=" * 80)

    # 날짜 범위 설정
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2025, 12, 31)

    total_blocks_1 = 0
    total_blocks_2 = 0
    success_count = 0
    error_count = 0

    # 각 종목별 탐지
    for stock_id, code, name, count in stocks_with_data:
        try:
            print(f"\n[INFO] Detecting {name} ({code})...")

            # 블록 탐지 실행
            result = block_detector.detect_all_blocks(
                stock_code=code,
                start_date=start_date,
                end_date=end_date
            )

            blocks_1_count = len(result['blocks_1'])
            blocks_2_count = len(result['blocks_2'])

            total_blocks_1 += blocks_1_count
            total_blocks_2 += blocks_2_count
            success_count += 1

            if blocks_1_count > 0 or blocks_2_count > 0:
                print(f"[SUCCESS] Found: Block 1={blocks_1_count}, Block 2={blocks_2_count}")
            else:
                print(f"[INFO] No blocks found")

        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            error_count += 1
            import traceback
            traceback.print_exc()
            continue

    # 결과 요약
    print("\n" + "=" * 80)
    print("DETECTION RESULTS")
    print("=" * 80)
    print(f"\nStocks processed: {success_count} success, {error_count} errors")
    print(f"Total Block 1 detected: {total_blocks_1}")
    print(f"Total Block 2 detected: {total_blocks_2}")

    # DB에 저장된 블록 확인
    with get_session() as session:
        saved_blocks = session.query(VolumeBlock).count()
        print(f"\nBlocks saved in DB: {saved_blocks}")

        if saved_blocks > 0:
            print("\nSample blocks:")
            blocks = session.query(VolumeBlock, Stock).join(Stock).limit(5).all()
            for block, stock in blocks:
                print(f"  - {stock.name} ({stock.code}): {block.block_type} on {block.date}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        test_block_detection()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
