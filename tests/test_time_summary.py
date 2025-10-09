"""
Quick test to verify the final summary with time logging
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from datetime import datetime
from services.data_collector import DataCollector
from core.enums import MarketType

# Create a custom collector instance for this test
collector = DataCollector()

# Manually stop after 10 stocks to see the summary
original_method = collector.collect_all_stocks

def limited_collect(market, start_date, end_date, progress_callback):
    """Wrapper to limit collection to 10 stocks"""
    # Get stock list
    stocks = collector.get_stock_list(market)[:10]  # Limit to 10
    collector.save_stocks_to_db(stocks)

    # Start timing
    start_time = datetime.now()
    print(f"\n[START] Collection started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    collected = 0
    failed = 0

    for idx, stock in enumerate(stocks):
        stock_start = datetime.now()

        # Simulate collection
        df = collector.collect_price_data(stock['code'], start_date, end_date)
        elapsed = (datetime.now() - stock_start).total_seconds()

        if df is not None and not df.empty:
            saved = collector.save_price_data_to_db(stock['code'], df)
            if saved > 0:
                collected += 1
                print(f"[OK] {stock['name']} ({stock['code']}): {saved} records saved - {elapsed:.2f}s")
            else:
                print(f"[INFO] {stock['name']} ({stock['code']}): No new data - {elapsed:.2f}s")
        else:
            failed += 1
            print(f"[ERROR] {stock['name']} ({stock['code']}): Collection failed - {elapsed:.2f}s")

    # Final summary
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    total_minutes = int(total_elapsed // 60)
    total_seconds = int(total_elapsed % 60)

    print(f"\n[FINISH] Collection completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Total time: {total_minutes}m {total_seconds}s ({total_elapsed:.2f}s)")
    print(f"   Success: {collected}")
    print(f"   Failed: {failed}")
    if len(stocks) > 0:
        avg_time = total_elapsed / len(stocks)
        print(f"   Average: {avg_time:.2f}s per stock")

# Run limited collection
limited_collect(
    market=MarketType.KOSPI,
    start_date="20251001",
    end_date=datetime.now().strftime("%Y%m%d"),
    progress_callback=None
)
