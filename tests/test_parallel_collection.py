"""
Test parallel data collection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from datetime import datetime
from services.data_collector import data_collector
from core.enums import MarketType

print("="*60)
print("Testing Parallel Data Collection")
print("="*60)

# 테스트 1: 작은 샘플로 병렬 처리 테스트 (10개 종목만)
print("\n[TEST 1] Small sample (first 10 stocks)")
print("-"*60)

# 종목 리스트 가져오기
stocks = data_collector.get_stock_list(MarketType.KOSPI)[:10]
data_collector.save_stocks_to_db(stocks)

# 병렬 수집 (5 workers)
data_collector.collect_all_stocks_parallel(
    market=None,  # stocks already selected
    start_date="20240101",
    end_date=datetime.now().strftime("%Y%m%d"),
    progress_callback=None,
    max_workers=5
)

print("\n" + "="*60)
print("Test complete!")
print("="*60)
