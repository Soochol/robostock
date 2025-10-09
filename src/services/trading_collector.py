"""
Trading Data Collector
수급 데이터 수집 모듈 (기관/외국인/개인 매매 정보)
"""

from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
from pykrx import stock
from sqlalchemy.orm import Session
import logging

from infrastructure.database.models import Stock, InvestorTrading
from infrastructure.database import get_session

logger = logging.getLogger(__name__)


class TradingDataCollector:
    """수급 데이터 수집기"""

    def __init__(self):
        pass  # session은 get_session() 컨텍스트 매니저 사용

    def collect_trading_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        특정 종목의 수급 데이터 수집

        Args:
            stock_code: 종목코드
            start_date: 시작일
            end_date: 종료일

        Returns:
            수급 데이터 DataFrame
        """
        try:
            # pykrx로 투자자별 거래 데이터 수집
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')

            # 투자자별 순매수 금액 (원)
            df_trading = stock.get_market_trading_value_by_date(
                start_str, end_str, stock_code
            )

            if df_trading is None or df_trading.empty:
                logger.warning(f"수급 데이터 없음: {stock_code}")
                return None

            # 컬럼 정리
            df_trading = df_trading.reset_index()
            df_trading.columns = [
                'date', 'institutional_buy', 'foreign_buy',
                'individual_buy', 'institutional_sell',
                'foreign_sell', 'individual_sell'
            ]

            # 순매수 계산
            df_trading['institutional_net_buy'] = (
                df_trading['institutional_buy'] -
                df_trading['institutional_sell']
            )
            df_trading['foreign_net_buy'] = (
                df_trading['foreign_buy'] - df_trading['foreign_sell']
            )
            df_trading['individual_net_buy'] = (
                df_trading['individual_buy'] - df_trading['individual_sell']
            )

            # 프로그램 순매수 (별도 API, 옵션)
            try:
                df_program = stock.get_market_trading_value_by_date(
                    start_str, end_str, stock_code, detail=True
                )
                if df_program is not None and '프로그램' in df_program.columns:
                    df_trading['program_net_buy'] = df_program['프로그램']
            except Exception:
                df_trading['program_net_buy'] = 0

            return df_trading

        except Exception as e:
            logger.error(f"수급 데이터 수집 실패 ({stock_code}): {e}")
            return None

    def calculate_buying_strength(
        self,
        net_buy: float,
        trading_value: float
    ) -> float:
        """
        매수강세 지수 계산

        Args:
            net_buy: 순매수 금액 (원)
            trading_value: 거래대금 (원)

        Returns:
            매수강세 지수 (%)
        """
        if trading_value == 0:
            return 0.0

        return (net_buy / trading_value) * 100

    def save_trading_data(
        self,
        stock_code: str,
        trading_df: pd.DataFrame,
        price_df: pd.DataFrame
    ) -> int:
        """
        수급 데이터 DB 저장

        Args:
            stock_code: 종목코드
            trading_df: 수급 데이터
            price_df: 주가 데이터 (거래대금 참조)

        Returns:
            저장된 레코드 수
        """
        try:
            with get_session() as session:
                # 종목 조회
                stock = session.query(Stock).filter(
                    Stock.code == stock_code
                ).first()

                if not stock:
                    logger.warning(f"종목 없음: {stock_code}")
                    return 0

                # 가격 데이터와 병합 (거래대금)
                merged_df = pd.merge(
                    trading_df,
                    price_df[['date', 'trading_value']],
                    on='date',
                    how='left'
                )

                saved_count = 0

                for _, row in merged_df.iterrows():
                    trading_value = row.get('trading_value', 0) or 0

                    # 매수강세 지수 계산
                    inst_strength = self.calculate_buying_strength(
                        row['institutional_net_buy'], trading_value
                    )
                    foreign_strength = self.calculate_buying_strength(
                        row['foreign_net_buy'], trading_value
                    )
                    individual_strength = self.calculate_buying_strength(
                        row['individual_net_buy'], trading_value
                    )
                    foreign_inst_strength = inst_strength + foreign_strength

                    # 기존 데이터 확인
                    existing = session.query(InvestorTrading).filter(
                        InvestorTrading.stock_id == stock.id,
                        InvestorTrading.date == row['date']
                    ).first()

                    if existing:
                        # 업데이트
                        existing.institutional_net_buy = float(
                            row['institutional_net_buy']
                        )
                        existing.foreign_net_buy = float(row['foreign_net_buy'])
                        existing.individual_net_buy = float(
                            row['individual_net_buy']
                        )
                        existing.program_net_buy = float(
                            row.get('program_net_buy', 0)
                        )
                        existing.institutional_buy = float(
                            row['institutional_buy']
                        )
                        existing.institutional_sell = float(
                            row['institutional_sell']
                        )
                        existing.foreign_buy = float(row['foreign_buy'])
                        existing.foreign_sell = float(row['foreign_sell'])
                        existing.individual_buy = float(row['individual_buy'])
                        existing.individual_sell = float(row['individual_sell'])
                        existing.institutional_buying_strength = inst_strength
                        existing.foreign_buying_strength = foreign_strength
                        existing.individual_buying_strength = individual_strength
                        existing.foreign_institutional_buying_strength = (
                            foreign_inst_strength
                        )
                    else:
                        # 신규 생성
                        trading_data = InvestorTrading(
                            stock_id=stock.id,
                            date=row['date'],
                            institutional_net_buy=float(
                                row['institutional_net_buy']
                            ),
                            foreign_net_buy=float(row['foreign_net_buy']),
                            individual_net_buy=float(row['individual_net_buy']),
                            program_net_buy=float(row.get('program_net_buy', 0)),
                            institutional_buy=float(row['institutional_buy']),
                            institutional_sell=float(row['institutional_sell']),
                            foreign_buy=float(row['foreign_buy']),
                            foreign_sell=float(row['foreign_sell']),
                            individual_buy=float(row['individual_buy']),
                            individual_sell=float(row['individual_sell']),
                            institutional_buying_strength=inst_strength,
                            foreign_buying_strength=foreign_strength,
                            individual_buying_strength=individual_strength,
                            foreign_institutional_buying_strength=(
                                foreign_inst_strength
                            )
                        )
                        session.add(trading_data)

                    saved_count += 1

                return saved_count

        except Exception as e:
            logger.error(f"수급 데이터 저장 실패: {e}")
            return 0

    def collect_and_save(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        price_df: pd.DataFrame
    ) -> int:
        """
        수급 데이터 수집 및 저장 (통합)

        Args:
            stock_code: 종목코드
            start_date: 시작일
            end_date: 종료일
            price_df: 주가 데이터

        Returns:
            저장된 레코드 수
        """
        # 수집
        trading_df = self.collect_trading_data(
            stock_code, start_date, end_date
        )

        if trading_df is None or trading_df.empty:
            return 0

        # 저장
        return self.save_trading_data(stock_code, trading_df, price_df)
