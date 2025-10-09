"""
Investor Trading Data Collection Test
투자자별 거래 데이터 수집 테스트
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from services.data_collector import DataCollector
from data.database import db_manager


def test_trading_collection():
    """삼성전자 투자자별 거래 데이터 수집 테스트"""
    print("=" * 60)
    print("투자자별 거래 데이터 수집 테스트")
    print("=" * 60)

    # 데이터 수집기 생성
    collector = DataCollector()
    collector.collect_trading_data_enabled = True

    # 삼성전자 테스트
    stock_code = "005930"
    stock_name = "삼성전자"

    # 최근 1개월 데이터
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    print(f"\n[INFO] 종목: {stock_name} ({stock_code})")
    print(f"[INFO] 기간: {start_str} ~ {end_str}")

    # 1. 주가 데이터 수집
    print("\n1. 주가 데이터 수집...")
    price_df = collector.collect_price_data(stock_code, start_str, end_str)

    if price_df is None or price_df.empty:
        print("[ERROR] 주가 데이터 수집 실패")
        return

    print(f"   수집: {len(price_df)}건")
    saved_price = collector.save_price_data_to_db(stock_code, price_df)
    print(f"   저장: {saved_price}건")

    # 2. 수급 데이터 수집
    print("\n2. 수급 데이터 수집...")
    trading_df = collector.collect_trading_data(stock_code, start_str, end_str)

    if trading_df is None or trading_df.empty:
        print("[ERROR] 수급 데이터 수집 실패")
        return

    print(f"   수집: {len(trading_df)}건")
    print(f"   컬럼: {list(trading_df.columns)}")

    # 3. 수급 데이터 저장
    print("\n3. 수급 데이터 저장...")
    saved_trading = collector.save_trading_data_to_db(
        stock_code, trading_df, price_df
    )
    print(f"   저장: {saved_trading}건")

    # 4. DB 확인
    print("\n4. DB 확인...")
    from data.models import Stock, InvestorTrading

    with db_manager.get_session() as session:
        stock = session.query(Stock).filter_by(code=stock_code).first()
        if stock:
            count = session.query(InvestorTrading).filter_by(
                stock_id=stock.id
            ).count()
            print(f"   총 {count}건의 투자자별 거래 데이터 저장됨")

            # 최근 5건 조회
            recent = session.query(InvestorTrading).filter_by(
                stock_id=stock.id
            ).order_by(InvestorTrading.date.desc()).limit(5).all()

            print("\n   최근 5건:")
            for td in recent:
                print(f"   - {td.date}: "
                      f"기관 {td.institutional_net_buy:+.0f}원 "
                      f"외국인 {td.foreign_net_buy:+.0f}원 "
                      f"(쌍끌이강도: {td.foreign_institutional_buying_strength:.2f}%)")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    test_trading_collection()
