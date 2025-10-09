"""
Test new SKIP logic for holidays/weekends
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from datetime import datetime
from services.data_collector import data_collector
from core.enums import MarketType

# Test with 10 stocks
start_date = "20251001"
end_date = datetime.now().strftime("%Y%m%d")

print("="*60)
print("Testing SKIP logic for holidays/weekends")
print("="*60)
print(f"Start: {start_date}")
print(f"End: {end_date}")
print(f"Expected: Most stocks should show [SKIP] instead of [ERROR]")
print("="*60 + "\n")

# Get 10 stocks that already have data
from data.database import get_session
from data.models import Stock, PriceData

with get_session() as session:
    # Get stocks with recent data
    stocks_with_data = session.query(Stock).join(PriceData).limit(10).all()
    test_stocks = [{'code': s.code, 'name': s.name, 'market': s.market} for s in stocks_with_data]

print(f"Testing with {len(test_stocks)} stocks:\n")
for stock in test_stocks:
    print(f"  - {stock['name']} ({stock['code']})")

# Save to DB first
data_collector.save_stocks_to_db(test_stocks)

# Collect (should show SKIP for most)
data_collector.collect_all_stocks(
    market=None,
    start_date=start_date,
    end_date=end_date,
    progress_callback=None
)

print("\n" + "="*60)
print("Test Complete - Check for [SKIP] messages above")
print("="*60)
