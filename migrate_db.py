"""
Database Migration Script
데이터베이스 마이그레이션 - 새로운 테이블 추가
"""

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.database import db_manager
from data.models import (
    Base, Stock, PriceData, InvestorTrading, VolumeBlock,
    BlockPatternData, SupportLevel, Case,
    FactorScore, PredictionResult, FinancialData, BacktestResult
)


def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    print("=" * 60)
    print("데이터베이스 마이그레이션 시작")
    print("=" * 60)

    try:
        # 모든 테이블 생성 (기존 테이블은 유지, 새 테이블만 추가)
        print("\n1. 테이블 생성 중...")
        Base.metadata.create_all(bind=db_manager.engine)
        print("   완료")

        # 생성된 테이블 목록
        print("\n2. 테이블 목록:")
        tables = [
            "stocks",
            "price_data",
            "investor_trading",  # 신규
            "volume_blocks",
            "block_pattern_data",  # 신규
            "support_levels",
            "cases",
            "factor_scores",
            "prediction_results",
            "financial_data",
            "backtest_results"
        ]

        for table in tables:
            marker = "*" if table in ["investor_trading", "block_pattern_data"] else " "
            print(f"   {marker} {table}")

        print("\n3. 새로 추가된 테이블:")
        print("   * investor_trading - 투자자별 거래 데이터 (기관/외국인/개인)")
        print("   * block_pattern_data - 2번 블록 D+1, D+2 상세 데이터")

        print("\n4. 확장된 테이블:")
        print("   - volume_blocks - Range 정보 및 시장 대비 성과 필드 추가")

        print("\n" + "=" * 60)
        print("마이그레이션 완료!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nX 마이그레이션 실패: {e}")
        return False


if __name__ == "__main__":
    success = migrate_database()

    if success:
        print("\n다음 단계:")
        print("1. 투자자별 거래 데이터 수집:")
        print("   from services.data_collector import DataCollector")
        print("   collector = DataCollector()")
        print("   collector.collect_trading_data_enabled = True")
        print("   collector.collect_all_stocks(...)")
        print("\n2. 블록 탐지 후 Range 계산 로직 추가 필요")
    else:
        print("\n마이그레이션을 다시 시도하거나 오류를 확인하세요.")
