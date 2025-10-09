"""Check trading_value in database"""
import sys
sys.path.insert(0, 'src')

from data.database import get_session
from data.models import PriceData, Stock

with get_session() as session:
    # 삼성전자 데이터 조회
    result = session.query(
        Stock.name,
        PriceData.date,
        PriceData.volume,
        PriceData.trading_value,
        PriceData.market_cap,
        PriceData.close
    ).join(Stock).filter(
        Stock.code == '005930'
    ).order_by(
        PriceData.date.desc()
    ).limit(5).all()

    print("=" * 150)
    print(f"{'Stock':<15} {'Date':<15} {'Volume':>15} {'TradingValue':>20} {'TradingVal(B)':>18} {'MarketCap(T)':>15} {'Close':>12}")
    print("=" * 150)

    for r in result:
        name, date, volume, trading_value, market_cap, close = r
        trading_B = trading_value / 1e8 if trading_value else 0
        market_cap_T = market_cap / 1e12 if market_cap else 0
        print(f"{name:<15} {str(date):<15} {volume:>15,} {trading_value:>20,.0f} {trading_B:>18,.1f} {market_cap_T:>15,.1f} {close:>12,.0f}")

    print("\n" + "=" * 150)
    print("TradingValue criteria: >= 500B (50,000,000,000 won)")
    print("MarketCap = Market Capitalization (total value of all shares in trillion won)")
    print("=" * 150)
