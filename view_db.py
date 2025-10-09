"""
DB 데이터 조회 스크립트
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.database import get_session
from data.models import Stock, PriceData, VolumeBlock
from sqlalchemy import func

def view_stocks(limit=20):
    """종목 리스트 보기"""
    print("\n" + "=" * 80)
    print("STOCK LIST")
    print("=" * 80)

    with get_session() as session:
        stocks = session.query(Stock).limit(limit).all()

        print(f"{'Code':<10} {'Name':<20} {'Market':<15} {'Updated':<20}")
        print("-" * 80)

        for stock in stocks:
            print(f"{stock.code:<10} {stock.name:<20} {str(stock.market):<15} {str(stock.updated_at):<20}")

def view_price_data(stock_code=None, limit=20):
    """가격 데이터 보기"""
    print("\n" + "=" * 80)
    print(f"PRICE DATA {f'for {stock_code}' if stock_code else ''}")
    print("=" * 80)

    with get_session() as session:
        query = session.query(PriceData, Stock).join(Stock)

        if stock_code:
            query = query.filter(Stock.code == stock_code)

        data = query.order_by(PriceData.date.desc()).limit(limit).all()

        print(f"{'Date':<12} {'Stock':<15} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<15}")
        print("-" * 80)

        for price, stock in data:
            print(f"{str(price.date):<12} {stock.name:<15} {price.open:<10.0f} {price.high:<10.0f} {price.low:<10.0f} {price.close:<10.0f} {price.volume:<15,}")

def view_blocks(limit=20):
    """블록 데이터 보기"""
    print("\n" + "=" * 80)
    print("VOLUME BLOCKS")
    print("=" * 80)

    with get_session() as session:
        blocks = session.query(VolumeBlock, Stock).join(Stock).limit(limit).all()

        if not blocks:
            print("No blocks detected yet.")
            return

        print(f"{'Date':<12} {'Stock':<15} {'Type':<10} {'Volume':<15} {'Price':<10}")
        print("-" * 80)

        for block, stock in blocks:
            print(f"{str(block.date):<12} {stock.name:<15} {str(block.block_type):<10} {block.volume:<15,} {block.close_price:<10.0f}")

def search_stock(keyword):
    """종목 검색"""
    print("\n" + "=" * 80)
    print(f"SEARCH: {keyword}")
    print("=" * 80)

    with get_session() as session:
        stocks = session.query(Stock).filter(
            (Stock.name.like(f'%{keyword}%')) | (Stock.code.like(f'%{keyword}%'))
        ).all()

        if not stocks:
            print(f"No stocks found for '{keyword}'")
            return

        print(f"{'Code':<10} {'Name':<20} {'Market':<15}")
        print("-" * 80)

        for stock in stocks:
            print(f"{stock.code:<10} {stock.name:<20} {str(stock.market):<15}")

def show_stats():
    """통계 보기"""
    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)

    with get_session() as session:
        # 종목 수
        total_stocks = session.query(Stock).count()
        kospi = session.query(Stock).filter(Stock.market == 'KOSPI').count()
        kosdaq = session.query(Stock).filter(Stock.market == 'KOSDAQ').count()

        # 가격 데이터 수
        total_prices = session.query(PriceData).count()

        # 가격 데이터 있는 종목 수
        stocks_with_data = session.query(func.count(func.distinct(PriceData.stock_id))).scalar()

        # 날짜 범위
        if total_prices > 0:
            min_date = session.query(func.min(PriceData.date)).scalar()
            max_date = session.query(func.max(PriceData.date)).scalar()
        else:
            min_date = max_date = "N/A"

        # 블록 수
        total_blocks = session.query(VolumeBlock).count()
        block_1 = session.query(VolumeBlock).filter(VolumeBlock.block_type == 'BLOCK_1').count()
        block_2 = session.query(VolumeBlock).filter(VolumeBlock.block_type == 'BLOCK_2').count()

        print(f"\nStocks:")
        print(f"  Total: {total_stocks:,}")
        print(f"  KOSPI: {kospi:,}")
        print(f"  KOSDAQ: {kosdaq:,}")

        print(f"\nPrice Data:")
        print(f"  Total records: {total_prices:,}")
        print(f"  Stocks with data: {stocks_with_data:,} / {total_stocks:,}")
        print(f"  Date range: {min_date} ~ {max_date}")

        print(f"\nVolume Blocks:")
        print(f"  Total: {total_blocks:,}")
        print(f"  Block 1: {block_1:,}")
        print(f"  Block 2: {block_2:,}")

def main():
    """메인 메뉴"""
    while True:
        print("\n" + "=" * 80)
        print("RoboStock DB Viewer")
        print("=" * 80)
        print("\n1. Show statistics")
        print("2. View stocks")
        print("3. View price data")
        print("4. View blocks")
        print("5. Search stock")
        print("6. View specific stock price data")
        print("0. Exit")

        choice = input("\nSelect: ").strip()

        if choice == '0':
            break
        elif choice == '1':
            show_stats()
        elif choice == '2':
            limit = input("How many? (default 20): ").strip() or "20"
            view_stocks(int(limit))
        elif choice == '3':
            limit = input("How many? (default 20): ").strip() or "20"
            view_price_data(limit=int(limit))
        elif choice == '4':
            limit = input("How many? (default 20): ").strip() or "20"
            view_blocks(int(limit))
        elif choice == '5':
            keyword = input("Search keyword: ").strip()
            if keyword:
                search_stock(keyword)
        elif choice == '6':
            code = input("Stock code (e.g. 005930): ").strip()
            limit = input("How many records? (default 20): ").strip() or "20"
            if code:
                view_price_data(code, int(limit))
        else:
            print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
