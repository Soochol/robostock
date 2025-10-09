"""
pykrx API 응답 디버깅
"""

from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta

# 테스트할 종목들
test_stocks = [
    ('095570', 'AJ네트웍스'),
    ('005930', '삼성전자'),
    ('006840', 'AK홀딩스'),
]

# 최근 날짜 테스트
today = datetime.now()
yesterday = today - timedelta(days=1)
week_ago = today - timedelta(days=7)

print(f"Today: {today.strftime('%Y%m%d')}")
print(f"Yesterday: {yesterday.strftime('%Y%m%d')}")
print(f"Week ago: {week_ago.strftime('%Y%m%d')}")
print("="*60)

for code, name in test_stocks:
    print(f"\n[{name} ({code})]")

    # 테스트 1: 최근 1주일
    try:
        df = pykrx_stock.get_market_ohlcv(
            week_ago.strftime('%Y%m%d'),
            today.strftime('%Y%m%d'),
            code
        )
        if df is not None and not df.empty:
            print(f"  [OK] 1 week data: {len(df)} rows")
            print(f"    Last date: {df.index[-1]}")
        else:
            print(f"  [EMPTY] 1 week data: None/Empty")
    except Exception as e:
        print(f"  [ERROR] 1 week data: {e}")

    # 테스트 2: 10월 3일 이후
    try:
        df = pykrx_stock.get_market_ohlcv(
            '20251003',
            today.strftime('%Y%m%d'),
            code
        )
        if df is not None and not df.empty:
            print(f"  [OK] From 20251003: {len(df)} rows")
            print(f"    Last date: {df.index[-1]}")
        else:
            print(f"  [EMPTY] From 20251003: None/Empty")
    except Exception as e:
        print(f"  [ERROR] From 20251003: {e}")

    # 테스트 3: 어제~오늘
    try:
        df = pykrx_stock.get_market_ohlcv(
            yesterday.strftime('%Y%m%d'),
            today.strftime('%Y%m%d'),
            code
        )
        if df is not None and not df.empty:
            print(f"  [OK] Yesterday-Today: {len(df)} rows")
        else:
            print(f"  [EMPTY] Yesterday-Today: None/Empty")
    except Exception as e:
        print(f"  [ERROR] Yesterday-Today: {e}")

print("\n" + "="*60)
print("결론: pykrx는 장이 끝난 후에만 데이터 제공")
print("주말/공휴일에는 최근 거래일 데이터만 조회 가능")
