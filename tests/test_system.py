"""
System Test Script
전체 시스템 테스트 스크립트
"""

import sys
from datetime import datetime, timedelta

# 데이터베이스 초기화
from data import init_database, get_session, Stock, PriceData, VolumeBlock
from services.data_collector import data_collector
from services.block_detector import block_detector
from core.enums import MarketType


def test_database():
    """데이터베이스 연결 테스트"""
    print("\n" + "="*60)
    print("1️⃣  데이터베이스 테스트")
    print("="*60)

    # 테이블 생성
    print("\n📦 데이터베이스 테이블 생성 중...")
    init_database()

    # 연결 테스트
    with get_session() as session:
        stock_count = session.query(Stock).count()
        print(f"✅ 데이터베이스 연결 성공! 현재 종목 수: {stock_count}개")


def test_data_collection_sample():
    """샘플 데이터 수집 테스트 (삼성전자 1종목만)"""
    print("\n" + "="*60)
    print("2️⃣  데이터 수집 테스트 (삼성전자)")
    print("="*60)

    # 삼성전자 정보 저장
    sample_stocks = [{
        'code': '005930',
        'name': '삼성전자',
        'market': MarketType.KOSPI
    }]

    print("\n📥 삼성전자 정보 저장 중...")
    data_collector.save_stocks_to_db(sample_stocks)

    # 최근 1년 주가 데이터 수집
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"\n📊 주가 데이터 수집 중... ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")

    df = data_collector.collect_price_data(
        '005930',
        start_date.strftime('%Y%m%d'),
        end_date.strftime('%Y%m%d')
    )

    if df is not None and not df.empty:
        saved = data_collector.save_price_data_to_db('005930', df)
        print(f"✅ {saved}건의 주가 데이터 저장 완료")
    else:
        print("❌ 데이터 수집 실패")

    # 저장된 데이터 확인
    with get_session() as session:
        stock = session.query(Stock).filter_by(code='005930').first()
        if stock:
            price_count = session.query(PriceData).filter_by(stock_id=stock.id).count()
            print(f"✅ DB 확인: 삼성전자 주가 데이터 {price_count}건 저장됨")


def test_block_detection():
    """블록 탐지 테스트 (삼성전자)"""
    print("\n" + "="*60)
    print("3️⃣  블록 탐지 테스트 (삼성전자)")
    print("="*60)

    # 최근 1년 기간 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"\n🔍 블록 탐지 시작... ({start_date.date()} ~ {end_date.date()})")

    result = block_detector.detect_all_blocks(
        '005930',
        start_date,
        end_date
    )

    print(f"\n✅ 탐지 완료:")
    print(f"   - 1번 블록: {len(result['blocks_1'])}개")
    print(f"   - 2번 블록: {len(result['blocks_2'])}개")

    # 블록 정보 출력
    if result['blocks_1']:
        print("\n📌 1번 블록 상세:")
        for i, block in enumerate(result['blocks_1'][:3], 1):  # 최대 3개만
            print(f"   {i}. 날짜: {block['date']}, "
                  f"거래대금: {block['trading_value']/100000000:.0f}억원, "
                  f"신고가: {block['new_high_grade'].value}등급")

    if result['blocks_2']:
        print("\n📌 2번 블록 상세:")
        for i, block in enumerate(result['blocks_2'][:3], 1):  # 최대 3개만
            print(f"   {i}. 날짜: {block['date']}, "
                  f"거래량 비율: {block['volume_ratio']*100:.1f}%, "
                  f"패턴: {block['pattern_type'].value}")


def test_database_queries():
    """데이터베이스 쿼리 테스트"""
    print("\n" + "="*60)
    print("4️⃣  데이터베이스 쿼리 테스트")
    print("="*60)

    with get_session() as session:
        # 전체 통계
        stock_count = session.query(Stock).count()
        price_count = session.query(PriceData).count()
        block_count = session.query(VolumeBlock).count()

        print(f"\n📊 전체 통계:")
        print(f"   - 종목: {stock_count}개")
        print(f"   - 주가 데이터: {price_count:,}건")
        print(f"   - 거래량 블록: {block_count}개")

        # 최근 블록 조회
        recent_blocks = session.query(VolumeBlock).order_by(
            VolumeBlock.date.desc()
        ).limit(5).all()

        if recent_blocks:
            print(f"\n📌 최근 블록 5개:")
            for block in recent_blocks:
                stock = session.query(Stock).filter_by(id=block.stock_id).first()
                print(f"   - {block.date} | {stock.name} | {block.block_type.value} | "
                      f"{block.trading_value/100000000:.0f}억원")


def main():
    """메인 테스트 실행"""
    print("\n" + "🎯 RoboStock 시스템 테스트 시작 🎯".center(60, "="))

    try:
        # 1. 데이터베이스 테스트
        test_database()

        # 2. 샘플 데이터 수집 (삼성전자)
        test_data_collection_sample()

        # 3. 블록 탐지 테스트
        test_block_detection()

        # 4. 데이터베이스 쿼리 테스트
        test_database_queries()

        print("\n" + "="*60)
        print("✅ 모든 테스트 완료!".center(60))
        print("="*60)
        print("\n💡 이제 GUI 앱을 실행하세요: python src/main.py")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
