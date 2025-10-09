"""
Test script to verify time logging in data collection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from datetime import datetime
from services.data_collector import data_collector
from core.enums import MarketType

def test_time_logging():
    """
    Test data collection with time logging
    Collect data for just a few stocks to verify logging works
    """
    print("="*60)
    print("Testing Time Logging Feature")
    print("="*60)

    # Test with KOSPI, limiting to first 5 stocks for quick test
    # Using start_date close to today to minimize data fetching
    start_date = "20251001"  # Just last week
    end_date = datetime.now().strftime("%Y%m%d")

    print(f"\nTest parameters:")
    print(f"  Market: KOSPI (will collect only 5 stocks for testing)")
    print(f"  Start Date: {start_date}")
    print(f"  End Date: {end_date}")
    print(f"\nExpected log format:")
    print(f"  [START] Collection started at YYYY-MM-DD HH:MM:SS")
    print(f"  [SKIP/UPDATE/OK] StockName (CODE): ... - X.XXs")
    print(f"  [FINISH] Collection completed at YYYY-MM-DD HH:MM:SS")
    print(f"     Total time: Xm Ys (X.XXs)")
    print(f"     Success: N")
    print(f"     Failed: N")
    print(f"     Average: X.XXs per stock")
    print("\n" + "="*60)

    # Get stock list first
    stocks = data_collector.get_stock_list(MarketType.KOSPI)

    if not stocks:
        print("[ERROR] Could not fetch stock list")
        return

    # Limit to 5 stocks for testing
    test_stocks = stocks[:5]
    print(f"\n[INFO] Testing with {len(test_stocks)} stocks:")
    for stock in test_stocks:
        print(f"  - {stock['name']} ({stock['code']})")

    # Save stocks to DB first
    data_collector.save_stocks_to_db(test_stocks)

    print("\n" + "="*60)
    print("Starting Collection (Watch for time logs)")
    print("="*60 + "\n")

    # Collect data (no progress callback for cleaner console output)
    data_collector.collect_all_stocks(
        market=None,  # Will use stocks from test_stocks
        start_date=start_date,
        end_date=end_date,
        progress_callback=None
    )

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

if __name__ == "__main__":
    test_time_logging()
