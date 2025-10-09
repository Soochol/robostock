"""
Data Collector Service
pykrx를 이용한 주가 데이터 수집
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from pykrx import stock as pykrx_stock
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading
import time
import socket

# 전역 HTTP 타임아웃 설정 (10초)
socket.setdefaulttimeout(10.0)

from infrastructure.database import get_session
from infrastructure.database.models import Stock, PriceData, InvestorTrading
from core.enums import MarketType
from core.config import COLLECTION_LOG_CONFIG
from sqlalchemy import func
from shared.utils.collection_logger import CollectionLogger, CompactLogger, DetailedLogger


class DataCollector:
    """
    데이터 수집 서비스

    기능:
    - KOSPI/KOSDAQ 종목 리스트 수집
    - 일별 OHLCV 데이터 수집
    - 거래대금, 시가총액 수집
    """

    def __init__(self):
        self.collected_count = 0
        self.failed_count = 0
        self.is_running = False
        self.collect_trading_data_enabled = True  # 수급 데이터 수집 옵션 (빠른 API 사용)
        self._lock = threading.Lock()  # 카운터 동기화용
        self._executor = None  # ThreadPoolExecutor 참조 저장

    def get_stock_list(self, market: MarketType = None) -> List[Dict]:
        """
        종목 리스트 가져오기

        Args:
            market: 시장 구분 (None=전체, KOSPI, KOSDAQ)

        Returns:
            종목 리스트 [{code, name, market}, ...]
        """
        today = datetime.now().strftime("%Y%m%d")
        stocks = []

        try:
            if market is None or market == MarketType.KOSPI:
                # KOSPI 종목
                kospi_codes = pykrx_stock.get_market_ticker_list(today, market="KOSPI")
                for code in kospi_codes:
                    name = pykrx_stock.get_market_ticker_name(code)
                    stocks.append({
                        'code': code,
                        'name': name,
                        'market': MarketType.KOSPI
                    })

            if market is None or market == MarketType.KOSDAQ:
                # KOSDAQ 종목
                kosdaq_codes = pykrx_stock.get_market_ticker_list(today, market="KOSDAQ")
                for code in kosdaq_codes:
                    name = pykrx_stock.get_market_ticker_name(code)
                    stocks.append({
                        'code': code,
                        'name': name,
                        'market': MarketType.KOSDAQ
                    })

        except Exception as e:
            print(f"[ERROR] Stock list fetch failed: {e}")
            return []

        print(f"[OK] Stock list fetched: {len(stocks)} stocks")
        return stocks

    def save_stocks_to_db(self, stocks: List[Dict]) -> int:
        """
        종목 정보를 DB에 저장

        Args:
            stocks: 종목 리스트

        Returns:
            저장된 종목 수
        """
        saved_count = 0

        with get_session() as session:
            for stock_info in stocks:
                # 기존 종목 확인
                existing = session.query(Stock).filter_by(code=stock_info['code']).first()

                if existing:
                    # 업데이트
                    existing.name = stock_info['name']
                    existing.market = stock_info['market']
                    existing.updated_at = datetime.now()
                else:
                    # 신규 추가
                    new_stock = Stock(
                        code=stock_info['code'],
                        name=stock_info['name'],
                        market=stock_info['market']
                    )
                    session.add(new_stock)

                saved_count += 1

        print(f"[OK] DB saved: {saved_count} stocks")
        return saved_count

    def collect_price_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        max_retries: int = 2,
        retry_delay: float = 0.5
    ) -> Optional[pd.DataFrame]:
        """
        종목의 일별 주가 데이터 수집

        Args:
            stock_code: 종목 코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간 대기 시간(초)

        Returns:
            DataFrame (날짜, OHLCV, 거래대금, 시가총액)
        """
        for attempt in range(max_retries):
            try:
                # 실행 중 체크
                if not self.is_running:
                    print(f"[DEBUG] {stock_code}: Collection stopped, skipping")
                    return None

                # API 호출 간 딜레이 (API 서버 부하 방지)
                # 워커 수가 2개이므로 200ms 대기 (서버 부하 최소화)
                time.sleep(0.2)  # 모든 요청 전 200ms 대기

                if attempt > 0:
                    time.sleep(retry_delay)
                    print(f"[DEBUG] {stock_code}: Retry {attempt}/{max_retries}")

                # OHLCV 데이터
                print(f"[DEBUG] {stock_code}: Calling pykrx get_market_ohlcv...")
                df = pykrx_stock.get_market_ohlcv(start_date, end_date, stock_code)
                print(f"[DEBUG] {stock_code}: pykrx get_market_ohlcv returned")

                if df is None or df.empty:
                    return None

                # 거래대금 계산 (거래량 × 평균가격)
                try:
                    print(f"[DEBUG] {stock_code}: Calculating trading value...")
                    # 평균가격 = (시가 + 고가 + 저가 + 종가) / 4
                    avg_price = (df['시가'] + df['고가'] + df['저가'] + df['종가']) / 4
                    df['TradingValue'] = df['거래량'] * avg_price
                    print(f"[DEBUG] {stock_code}: Trading value calculated")
                except Exception as e:
                    print(f"[DEBUG] {stock_code}: Trading value calculation failed: {e}")
                    df['TradingValue'] = 0

                # 시가총액 추가
                try:
                    print(f"[DEBUG] {stock_code}: Getting market cap...")
                    cap = pykrx_stock.get_market_cap_by_date(
                        start_date, end_date, stock_code
                    )
                    if cap is not None and not cap.empty:
                        df['MarketCap'] = cap['시가총액']
                except Exception as e:
                    print(f"[DEBUG] {stock_code}: Market cap failed: {e}")
                    df['MarketCap'] = 0

                # 성공 시 반환
                return df

            except Exception as e:
                print(f"[ERROR] {stock_code} attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    # 마지막 시도 실패
                    return None
                # 재시도 계속

        return None

    def collect_trading_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        수급 데이터 수집 (기관/외국인/개인 매매)

        Args:
            stock_code: 종목 코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            DataFrame (날짜, 순매수 정보)
        """
        try:
            # 실행 중 체크
            if not self.is_running:
                print(f"[DEBUG] {stock_code}: Collection stopped, skipping trading data")
                return None

            print(f"[DEBUG] {stock_code}: Calling pykrx get_market_trading_volume_by_date...")
            # pykrx로 날짜별 투자자 거래 데이터 (날짜가 인덱스)
            df = pykrx_stock.get_market_trading_volume_by_date(
                start_date, end_date, stock_code
            )
            print(f"[DEBUG] {stock_code}: pykrx returned ({len(df) if df is not None else 0} records)")

            if df is None or df.empty:
                return None

            # 인덱스(날짜)를 컬럼으로 변환
            df = df.reset_index()

            # 컬럼명 표준화 (인코딩 문제 방지를 위해 인덱스로 접근)
            # 컬럼 순서: 날짜, 금융투자, 기타법인, 개인, 외국인법인, 기타
            if len(df.columns) >= 5:
                df.columns = ['date', '금융투자', '기타법인', '개인', '외국인법인', '기타']
            else:
                print(f"[WARNING] {stock_code}: Unexpected column count: {len(df.columns)}")
                return None

            # 날짜 타입 변환 (datetime으로 통일)
            df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            print(f"[ERROR] {stock_code} trading data collection failed: {e}")
            return None

    def save_trading_data_to_db(
        self,
        stock_code: str,
        trading_df: pd.DataFrame,
        price_df: pd.DataFrame
    ) -> int:
        """
        수급 데이터를 DB에 저장

        Args:
            stock_code: 종목 코드
            trading_df: 수급 데이터
            price_df: 주가 데이터 (거래대금 참조)

        Returns:
            저장된 레코드 수
        """
        if trading_df is None or trading_df.empty:
            return 0

        saved_count = 0

        try:
            with get_session() as session:
                stock = session.query(Stock).filter_by(code=stock_code).first()
                if not stock:
                    return 0

                # 가격 데이터와 병합
                price_df_reset = price_df.reset_index()
                price_df_reset.columns = ['date'] + list(price_df.columns)

                # 날짜 타입 통일 (datetime)
                price_df_reset['date'] = pd.to_datetime(price_df_reset['date'])
                trading_df['date'] = pd.to_datetime(trading_df['date'])

                merged = pd.merge(
                    trading_df,
                    price_df_reset[['date', 'TradingValue']],
                    on='date',
                    how='left'
                )

                for _, row in merged.iterrows():
                    date_obj = row['date'].date() if hasattr(
                        row['date'], 'date'
                    ) else row['date']

                    trading_value = row.get('TradingValue', 0) or 0

                    # 기존 데이터 확인
                    existing = session.query(InvestorTrading).filter_by(
                        stock_id=stock.id,
                        date=date_obj
                    ).first()

                    # 순매수 계산 (pykrx 컬럼명: 금융투자, 외국인법인, 개인)
                    inst_net = float(row.get('금융투자', 0) or 0)
                    foreign_net = float(row.get('외국인법인', 0) or 0)
                    indiv_net = float(row.get('개인', 0) or 0)

                    # 매수강세 지수 계산
                    inst_strength = (
                        (inst_net / trading_value * 100) if trading_value > 0 else 0
                    )
                    foreign_strength = (
                        (foreign_net / trading_value * 100) if trading_value > 0 else 0
                    )
                    indiv_strength = (
                        (indiv_net / trading_value * 100) if trading_value > 0 else 0
                    )

                    if existing:
                        # 업데이트
                        existing.institutional_net_buy = inst_net
                        existing.foreign_net_buy = foreign_net
                        existing.individual_net_buy = indiv_net
                        existing.institutional_buying_strength = inst_strength
                        existing.foreign_buying_strength = foreign_strength
                        existing.individual_buying_strength = indiv_strength
                        existing.foreign_institutional_buying_strength = (
                            inst_strength + foreign_strength
                        )
                    else:
                        # 신규 생성
                        trading_data = InvestorTrading(
                            stock_id=stock.id,
                            date=date_obj,
                            institutional_net_buy=inst_net,
                            foreign_net_buy=foreign_net,
                            individual_net_buy=indiv_net,
                            institutional_buying_strength=inst_strength,
                            foreign_buying_strength=foreign_strength,
                            individual_buying_strength=indiv_strength,
                            foreign_institutional_buying_strength=(
                                inst_strength + foreign_strength
                            )
                        )
                        session.add(trading_data)

                    saved_count += 1

            return saved_count

        except Exception as e:
            print(f"[ERROR] Trading data save failed: {e}")
            return 0

    def save_price_data_to_db(
        self,
        stock_code: str,
        df: pd.DataFrame
    ) -> int:
        """
        주가 데이터를 DB에 저장

        Args:
            stock_code: 종목 코드
            df: 주가 데이터 DataFrame

        Returns:
            저장된 레코드 수
        """
        if df is None or df.empty:
            return 0

        saved_count = 0

        try:
            with get_session() as session:
                # 종목 조회
                stock = session.query(Stock).filter_by(code=stock_code).first()
                if not stock:
                    print(f"[WARNING] Stock {stock_code} not found in DB")
                    return 0

                # DataFrame 순회하며 저장/업데이트
                for date_idx, row in df.iterrows():
                    date_obj = date_idx.date() if hasattr(date_idx, 'date') else date_idx

                    # 기존 레코드 확인
                    existing = session.query(PriceData).filter_by(
                        stock_id=stock.id,
                        date=date_obj
                    ).first()

                    if existing:
                        # 거래대금이 0이면 업데이트
                        if existing.trading_value == 0 or existing.trading_value is None:
                            existing.trading_value = float(row.get('TradingValue', 0))
                        if existing.market_cap == 0 or existing.market_cap is None:
                            existing.market_cap = float(row.get('MarketCap', 0))
                        saved_count += 1
                    else:
                        # 새 레코드 추가
                        price_data = PriceData(
                            stock_id=stock.id,
                            date=date_obj,
                            open=float(row['시가']),
                            high=float(row['고가']),
                            low=float(row['저가']),
                            close=float(row['종가']),
                            volume=int(row['거래량']),
                            trading_value=float(row.get('TradingValue', 0)),
                            market_cap=float(row.get('MarketCap', 0))
                        )
                        session.add(price_data)
                        saved_count += 1

        except Exception as e:
            print(f"[ERROR] Failed to save {stock_code} to DB: {e}")
            return 0

        return saved_count

    def collect_all_stocks(
        self,
        market: MarketType = None,
        start_date: str = "20150101",
        end_date: str = None,
        progress_callback=None
    ):
        """
        전체 종목 데이터 수집

        Args:
            market: 시장 구분
            start_date: 시작일
            end_date: 종료일 (기본: 오늘)
            progress_callback: 진행률 콜백 함수 (current, total, message)
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        self.is_running = True
        self.collected_count = 0
        self.failed_count = 0

        # 시작 시간 기록
        start_time = datetime.now()
        print(f"\n[START] Collection started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 종목 리스트 수집
        if progress_callback:
            progress_callback(0, 100, "종목 리스트 수집 중...")

        stocks = self.get_stock_list(market)
        if not stocks:
            print("[ERROR] Stock list is empty")
            return

        # 2. 종목 정보 DB 저장
        self.save_stocks_to_db(stocks)

        # 3. 각 종목별 주가 데이터 수집
        total_stocks = len(stocks)

        for idx, stock_info in enumerate(stocks):
            if not self.is_running:
                print("[INFO] Collection stopped")
                break

            stock_code = stock_info['code']
            stock_name = stock_info['name']

            if progress_callback:
                progress_callback(
                    idx + 1,
                    total_stocks,
                    f"[{idx+1}/{total_stocks}] {stock_name} ({stock_code}) 수집 중..."
                )

            # 종목별 시작 시간
            stock_start_time = datetime.now()

            # DB에 이미 데이터가 있는지 먼저 확인
            collection_start_date = start_date
            last_date_in_db = None  # 변수로 저장

            with get_session() as session:
                stock = session.query(Stock).filter_by(code=stock_code).first()
                if stock:
                    # 마지막 데이터 날짜 확인
                    last_date_in_db = session.query(func.max(PriceData.date)).filter_by(
                        stock_id=stock.id
                    ).scalar()

                    if last_date_in_db:
                        # 마지막 날짜가 오늘과 같거나 미래면 스킵
                        today = datetime.now().date()
                        if last_date_in_db >= today:
                            elapsed = (datetime.now() - stock_start_time).total_seconds()
                            print(f"[SKIP] {stock_name} ({stock_code}): Up-to-date ({last_date_in_db}) - {elapsed:.2f}s")
                            continue

                        # 마지막 날짜 다음날부터 수집 (증분 업데이트)
                        next_day = (last_date_in_db + timedelta(days=1)).strftime("%Y%m%d")
                        collection_start_date = next_day
                        print(f"[UPDATE] {stock_name} ({stock_code}): Updating from {next_day}")

            # 주가 데이터 수집
            df = self.collect_price_data(stock_code, collection_start_date, end_date)

            # 종목별 소요 시간 계산
            elapsed = (datetime.now() - stock_start_time).total_seconds()

            if df is not None and not df.empty:
                # 주가 데이터 DB 저장
                saved = self.save_price_data_to_db(stock_code, df)

                # 수급 데이터 수집 (옵션)
                trading_saved = 0
                if self.collect_trading_data_enabled:
                    trading_df = self.collect_trading_data(
                        stock_code, collection_start_date, end_date
                    )
                    if trading_df is not None and not trading_df.empty:
                        trading_saved = self.save_trading_data_to_db(
                            stock_code, trading_df, df
                        )

                if saved > 0:
                    self.collected_count += 1
                    msg = f"[OK] {stock_name} ({stock_code}): {saved} price"
                    if trading_saved > 0:
                        msg += f" + {trading_saved} trading"
                    msg += f" records - {elapsed:.2f}s"
                    print(msg)
                else:
                    print(f"[INFO] {stock_name} ({stock_code}): No new data - {elapsed:.2f}s")
            else:
                # 데이터가 없는 경우 처리
                # 증분 업데이트 중이고 last_date가 최근(7일 이내)이면 API에 신규 데이터가 없는 것
                if last_date_in_db is not None:
                    days_diff = (datetime.now().date() - last_date_in_db).days
                    if days_diff <= 7:  # 주말 포함 최대 7일
                        # 최근 데이터가 있고 API에 신규 데이터가 없음 (정상 - 휴일/주말)
                        print(f"[SKIP] {stock_name} ({stock_code}): No new data in API (last: {last_date_in_db}) - {elapsed:.2f}s")
                        continue

                # 그 외에는 실제 에러 (7일 이상 데이터 없음 or 처음 수집 실패)
                self.failed_count += 1
                print(f"[ERROR] {stock_name} ({stock_code}): Collection failed - {elapsed:.2f}s")

        # 완료 시간 계산
        end_time = datetime.now()
        total_elapsed = (end_time - start_time).total_seconds()
        total_minutes = int(total_elapsed // 60)
        total_seconds = int(total_elapsed % 60)

        # 완료
        if progress_callback:
            progress_callback(
                total_stocks,
                total_stocks,
                f"수집 완료: {self.collected_count}개 성공, {self.failed_count}개 실패"
            )

        print(f"\n[FINISH] Collection completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total time: {total_minutes}m {total_seconds}s ({total_elapsed:.2f}s)")
        print(f"   Success: {self.collected_count}")
        print(f"   Failed: {self.failed_count}")
        if total_stocks > 0:
            avg_time = total_elapsed / total_stocks
            print(f"   Average: {avg_time:.2f}s per stock")

    def stop_collection(self):
        """수집 중지"""
        print("[DEBUG] stop_collection called")
        self.is_running = False

        # ThreadPoolExecutor 즉시 종료 (wait=False)
        if self._executor:
            print("[DEBUG] Shutting down executor (immediate)...")
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except Exception as e:
                print(f"[DEBUG] Executor shutdown error: {e}")
            finally:
                self._executor = None
                print("[DEBUG] Executor shutdown complete")

    def _collect_single_stock(
        self,
        stock_info: Dict,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        단일 종목 수집 (병렬 처리용)

        Args:
            stock_info: 종목 정보
            start_date: 시작일
            end_date: 종료일

        Returns:
            Dict: {'code': str, 'name': str, 'saved': int, 'success': bool}
        """
        stock_code = stock_info['code']
        stock_name = stock_info['name']
        stock_start_time = datetime.now()

        print(f"[DEBUG] _collect_single_stock START: {stock_name} ({stock_code})")

        try:
            # DB에서 최소/최대 날짜 확인 (스마트 증분 업데이트)
            print(f"[DEBUG] {stock_name}: Checking date range in DB...")
            requested_start = datetime.strptime(start_date, "%Y%m%d").date()
            requested_end = datetime.strptime(end_date, "%Y%m%d").date()

            min_date_in_db = None
            max_date_in_db = None
            total_saved = 0
            total_trading_saved = 0

            with get_session() as session:
                stock = session.query(Stock).filter_by(code=stock_code).first()
                if stock:
                    min_date_in_db = session.query(
                        func.min(PriceData.date)
                    ).filter_by(stock_id=stock.id).scalar()

                    max_date_in_db = session.query(
                        func.max(PriceData.date)
                    ).filter_by(stock_id=stock.id).scalar()

            # 수집할 구간 결정
            collection_ranges = []

            # 과거 갭 체크 (요청 시작일 < DB 최소일)
            if min_date_in_db and requested_start < min_date_in_db:
                past_gap_start = requested_start.strftime("%Y%m%d")
                past_gap_end = (min_date_in_db - timedelta(days=1)).strftime("%Y%m%d")
                collection_ranges.append(('past', past_gap_start, past_gap_end))
                print(f"[DEBUG] {stock_name}: Past gap detected: {past_gap_start} ~ {past_gap_end}")

            # 미래 갭 체크 (DB 최대일 < 요청 종료일)
            if max_date_in_db:
                if max_date_in_db < requested_end:
                    future_gap_start = (max_date_in_db + timedelta(days=1)).strftime("%Y%m%d")
                    future_gap_end = requested_end.strftime("%Y%m%d")
                    collection_ranges.append(('future', future_gap_start, future_gap_end))
                    print(f"[DEBUG] {stock_name}: Future gap detected: {future_gap_start} ~ {future_gap_end}")
                elif max_date_in_db >= datetime.now().date():
                    # 최신 데이터 있음
                    elapsed = (datetime.now() - stock_start_time).total_seconds()
                    return {
                        'code': stock_code,
                        'name': stock_name,
                        'saved': 0,
                        'success': True,
                        'message': f'Up-to-date ({max_date_in_db})',
                        'elapsed': elapsed
                    }
            else:
                # DB에 데이터 없음 - 전체 구간 수집
                collection_ranges.append(('full', start_date, end_date))
                print(f"[DEBUG] {stock_name}: No data in DB, collecting full range")

            # 각 구간별로 데이터 수집
            for gap_type, gap_start, gap_end in collection_ranges:
                print(f"[DEBUG] {stock_name}: Collecting {gap_type} gap from {gap_start} to {gap_end}...")
                df = self.collect_price_data(stock_code, gap_start, gap_end)

                if df is not None and not df.empty:
                    print(f"[DEBUG] {stock_name}: Saving {len(df)} records for {gap_type} gap...")
                    saved = self.save_price_data_to_db(stock_code, df)
                    total_saved += saved

                    # 수급 데이터 수집
                    if self.collect_trading_data_enabled:
                        print(f"[DEBUG] {stock_name}: Collecting trading data for {gap_type} gap...")
                        trading_df = self.collect_trading_data(stock_code, gap_start, gap_end)
                        if trading_df is not None and not trading_df.empty:
                            trading_saved = self.save_trading_data_to_db(stock_code, trading_df, df)
                            total_trading_saved += trading_saved

            elapsed = (datetime.now() - stock_start_time).total_seconds()

            # 결과 반환
            if total_saved > 0:
                print(f"[DEBUG] {stock_name}: DONE - Saved {total_saved} price, {total_trading_saved} trading records")
                return {
                    'code': stock_code,
                    'name': stock_name,
                    'saved': total_saved,
                    'trading_saved': total_trading_saved,
                    'success': True,
                    'message': f'{total_saved} price + {total_trading_saved} trading records',
                    'elapsed': elapsed
                }
            else:
                # 데이터 없음 처리
                if max_date_in_db is not None:
                    days_diff = (datetime.now().date() - max_date_in_db).days
                    if days_diff <= 7:
                        return {
                            'code': stock_code,
                            'name': stock_name,
                            'saved': 0,
                            'success': True,
                            'message': f'No new data (last: {max_date_in_db})',
                            'elapsed': elapsed
                        }

                return {
                    'code': stock_code,
                    'name': stock_name,
                    'saved': 0,
                    'success': False,
                    'message': 'No data collected',
                    'elapsed': elapsed
                }

        except Exception as e:
            elapsed = (datetime.now() - stock_start_time).total_seconds()
            return {
                'code': stock_code,
                'name': stock_name,
                'saved': 0,
                'success': False,
                'message': f'Error: {e}',
                'elapsed': elapsed
            }

    def collect_all_stocks_parallel(
        self,
        market: MarketType = None,
        start_date: str = "20150101",
        end_date: str = None,
        progress_callback=None,
        max_workers: int = 10,
        limit: int = None,
        priority_mode: bool = False
    ):
        """
        병렬로 모든 종목 데이터 수집

        Args:
            market: 시장 구분
            start_date: 시작일
            end_date: 종료일
            progress_callback: 진행 상황 콜백
            max_workers: 동시 처리 스레드 수 (기본 10개)
            limit: 수집 종목 수 제한
            priority_mode: 우선순위 모드 (시총 기준 정렬)
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        self.is_running = True
        self.collected_count = 0
        self.failed_count = 0

        start_time = datetime.now()
        print(f"\n[START] Parallel collection started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Workers: {max_workers} threads")

        # 종목 리스트 수집
        if progress_callback:
            progress_callback(0, 100, "종목 리스트 수집 중...")

        stocks = self.get_stock_list(market)
        if not stocks:
            print("[ERROR] Stock list is empty")
            return

        # 우선순위 정렬 (시가총액 기준)
        if priority_mode:
            print("   Sorting by market cap (priority mode)...")
            # 시가총액은 실시간 조회가 어려우므로 코드 기준으로 주요 종목 우선
            # KOSPI 200, 대형주 우선
            priority_codes = ['005930', '000660', '051910', '035420', '006400',  # 삼성전자, SK하이닉스, LG화학, NAVER, 삼성SDI
                            '035720', '000270', '068270', '207940', '105560']  # 카카오, 기아, 셀트리온, 삼성바이오, KB금융

            # 우선순위 종목을 앞으로
            priority_stocks = [s for s in stocks if s['code'] in priority_codes]
            other_stocks = [s for s in stocks if s['code'] not in priority_codes]
            stocks = priority_stocks + other_stocks
            print(f"   Priority stocks: {len(priority_stocks)}")

        # 수집 제한 적용
        if limit and limit > 0:
            stocks = stocks[:limit]
            print(f"   Limited to top {limit} stocks")

        # DB 저장
        self.save_stocks_to_db(stocks)

        total_stocks = len(stocks)
        completed = 0

        print(f"   Total stocks to collect: {total_stocks}\n")

        # 로거 생성
        log_style = COLLECTION_LOG_CONFIG.get('style', 'compact')
        use_colors = COLLECTION_LOG_CONFIG.get('use_colors', True)

        if log_style == 'detailed':
            logger = DetailedLogger(total_count=total_stocks, use_colors=use_colors)
        elif log_style == 'compact':
            logger = CollectionLogger(total_count=total_stocks, use_colors=use_colors)
        else:
            logger = None

        # 병렬 수집
        print(f"[DEBUG] Starting ThreadPoolExecutor with {max_workers} workers...")
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            print(f"[DEBUG] Submitting {len(stocks)} tasks...")
            futures = {
                self._executor.submit(
                    self._collect_single_stock,
                    stock,
                    start_date,
                    end_date
                ): stock for stock in stocks
            }
            print(f"[DEBUG] All tasks submitted. Waiting for completion...")

            for future in as_completed(futures):
                print(f"[DEBUG] Future completed: {completed + 1}/{total_stocks}")

                if not self.is_running:
                    print("[INFO] Collection stopped")
                    break

                stock = futures[future]
                completed += 1

                try:
                    print(f"[DEBUG] Getting result for {stock['name']}...")
                    result = future.result(timeout=30)  # 30초 타임아웃 추가
                    print(f"[DEBUG] Result received: {result['name']} - {result['message']}")

                    # 카운터 업데이트 (스레드 안전)
                    with self._lock:
                        if result['success'] and result['saved'] > 0:
                            self.collected_count += 1
                        elif not result['success']:
                            self.failed_count += 1

                    # 로그 출력
                    if logger:
                        if result['success']:
                            if result['saved'] > 0:
                                logger.log_success(
                                    result['name'],
                                    result['code'],
                                    result['saved'],
                                    result.get('trading_saved', 0),
                                    result['elapsed']
                                )
                            else:
                                logger.log_skip(
                                    result['name'],
                                    result['code'],
                                    result['message'],
                                    result['elapsed']
                                )
                        else:
                            logger.log_error(
                                result['name'],
                                result['code'],
                                result['message'],
                                result['elapsed']
                            )

                        # 주기적 요약 출력
                        if COLLECTION_LOG_CONFIG.get('show_progress_bar', True):
                            logger.log_summary_inline()
                    else:
                        # 기본 로그 (fallback)
                        if result['success']:
                            if result['saved'] > 0:
                                print(f"[OK] {result['name']} ({result['code']}): {result['message']} - {result['elapsed']:.2f}s")
                            else:
                                print(f"[SKIP] {result['name']} ({result['code']}): {result['message']} - {result['elapsed']:.2f}s")
                        else:
                            print(f"[ERROR] {result['name']} ({result['code']}): {result['message']} - {result['elapsed']:.2f}s")

                    # 진행 상황 업데이트
                    if progress_callback:
                        progress_callback(
                            completed,
                            total_stocks,
                            f"[{completed}/{total_stocks}] {result['name']} 완료"
                        )

                except Exception as e:
                    with self._lock:
                        self.failed_count += 1
                    print(f"[ERROR] {stock['name']} ({stock['code']}): {e}")

        finally:
            # Executor 정리 (즉시 종료)
            print("[DEBUG] Cleaning up executor...")
            if self._executor:
                try:
                    self._executor.shutdown(wait=False, cancel_futures=True)
                except Exception as e:
                    print(f"[DEBUG] Cleanup error: {e}")
                finally:
                    self._executor = None
            print("[DEBUG] Executor cleaned up")

        # 완료 시간 계산
        end_time = datetime.now()
        total_elapsed = (end_time - start_time).total_seconds()
        total_minutes = int(total_elapsed // 60)
        total_seconds = int(total_elapsed % 60)

        # 완료 메시지
        if progress_callback:
            progress_callback(
                total_stocks,
                total_stocks,
                f"수집 완료: {self.collected_count}개 성공, {self.failed_count}개 실패"
            )

        # 최종 요약
        if logger:
            logger.log_final_summary()
        else:
            print(f"\n[FINISH] Collection completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Total time: {total_minutes}m {total_seconds}s ({total_elapsed:.2f}s)")
            print(f"   Success: {self.collected_count}")
            print(f"   Failed: {self.failed_count}")
            print(f"   Skipped: {total_stocks - self.collected_count - self.failed_count}")
            if total_stocks > 0:
                avg_time = total_elapsed / total_stocks
                print(f"   Average: {avg_time:.2f}s per stock")
                print(f"   Speed improvement: ~{max_workers}x faster")


# 전역 데이터 수집 인스턴스
data_collector = DataCollector()
