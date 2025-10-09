"""
Data Collection Worker
QThread 기반 백그라운드 데이터 수집 워커
"""

from PySide6.QtCore import QThread, Signal
from datetime import datetime
from services.data_collector import data_collector
from core.enums import MarketType


class DataCollectionWorker(QThread):
    """
    데이터 수집 백그라운드 워커

    Signals:
        progress: (current, total, message)
        finished: (success, total_count)
        error: (error_message)
    """

    progress = Signal(int, int, str)
    finished = Signal(bool, int)
    error = Signal(str)

    def __init__(
        self,
        market_type,
        start_date,
        end_date,
        collect_price,
        collect_financial,
        collection_range="전체 종목",
        max_workers=5
    ):
        super().__init__()
        self.setTerminationEnabled(True)  # 강제 종료 가능하도록 설정
        self.market_type = market_type
        self.start_date = start_date
        self.end_date = end_date
        self.collect_price = collect_price
        self.collect_financial = collect_financial
        self.collection_range = collection_range  # 수집 범위
        self.max_workers = max_workers  # 병렬 처리 워커 수
        self._is_running = True

    def run(self):
        """백그라운드 데이터 수집 실행"""
        try:
            # 시장 타입 변환
            if self.market_type == "전체 (KOSPI + KOSDAQ)":
                market = None
            elif self.market_type == "KOSPI":
                market = MarketType.KOSPI
            else:
                market = MarketType.KOSDAQ

            # 날짜 포맷 변환
            start_str = self.start_date.toString("yyyyMMdd")
            end_str = self.end_date.toString("yyyyMMdd")

            # 진행률 콜백 함수
            def progress_callback(current, total, message):
                if self._is_running:
                    self.progress.emit(current, total, message)

            # 수집 범위에 따라 limit과 priority_mode 설정
            limit = None
            priority_mode = False

            if self.collection_range == "주요 종목만 (시총 상위 200개)":
                limit = 200
                priority_mode = True
            elif self.collection_range == "시가총액 1조 이상":
                limit = 300  # 대략 300개 정도
                priority_mode = True
            elif self.collection_range == "KOSPI 200":
                limit = 200
                priority_mode = True
            elif self.collection_range == "증분 업데이트만 (신규 데이터)":
                # 전체 종목이지만 이미 데이터가 있는 종목은 SKIP됨
                limit = None
                priority_mode = False

            # 병렬 데이터 수집 실행
            data_collector.collect_all_stocks_parallel(
                market=market,
                start_date=start_str,
                end_date=end_str,
                progress_callback=progress_callback,
                max_workers=self.max_workers,
                limit=limit,
                priority_mode=priority_mode
            )

            # 완료
            if self._is_running:
                self.finished.emit(True, data_collector.collected_count)

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, 0)

    def stop(self):
        """수집 중지"""
        self._is_running = False
        data_collector.stop_collection()
