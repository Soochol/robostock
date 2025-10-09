"""
Block Detection Worker
QThread 기반 백그라운드 블록 탐지 워커
"""

from PySide6.QtCore import QThread, Signal
from datetime import datetime
from services.block_detector import block_detector
from data.database import get_session
from data.models import Stock


class BlockDetectionWorker(QThread):
    """
    블록 탐지 백그라운드 워커

    Signals:
        progress: (current, total, message)
        stock_completed: (stock_name, blocks_1_count, blocks_2_count)
        finished: (success, total_blocks_1, total_blocks_2)
        error: (error_message)
    """

    progress = Signal(int, int, str)
    stock_completed = Signal(str, int, int)  # stock_name, blocks_1, blocks_2
    finished = Signal(bool, int, int)  # success, total_blocks_1, total_blocks_2
    error = Signal(str)

    def __init__(self, start_date, end_date, market_filter=None, settings=None):
        super().__init__()
        self.setTerminationEnabled(True)  # 강제 종료 가능하도록 설정
        self.start_date = start_date
        self.end_date = end_date
        self.market_filter = market_filter
        self.settings = settings  # 탐지 설정 (None이면 기본값 사용)
        self._is_running = True
        self.total_blocks_1 = 0
        self.total_blocks_2 = 0

    def run(self):
        """백그라운드 블록 탐지 실행"""
        print("[DEBUG] BlockDetectionWorker.run() started")
        try:
            # 날짜 변환
            start_dt = datetime.combine(self.start_date.toPython(), datetime.min.time())
            end_dt = datetime.combine(self.end_date.toPython(), datetime.max.time())
            print(f"[DEBUG] Date range: {start_dt} to {end_dt}")

            # DB에서 종목 리스트 조회
            with get_session() as session:
                query = session.query(Stock)

                # 시장 필터 적용
                if self.market_filter and self.market_filter != "전체":
                    query = query.filter(Stock.market == self.market_filter)

                stocks_orm = query.all()

                # 세션이 닫히기 전에 데이터를 dict로 변환
                stocks = [
                    {'code': s.code, 'name': s.name, 'id': s.id}
                    for s in stocks_orm
                ]
                total_stocks = len(stocks)
                print(f"[DEBUG] Found {total_stocks} stocks to process")

            if total_stocks == 0:
                print("[DEBUG] No stocks found - emitting error")
                self.error.emit("탐지할 종목이 없습니다. 먼저 데이터를 수집해주세요.")
                self.finished.emit(False, 0, 0)
                return

            print(f"[DEBUG] Emitting initial progress signal")
            self.progress.emit(0, total_stocks, f"총 {total_stocks}개 종목 탐지 시작...")

            # 각 종목별 블록 탐지
            print(f"[DEBUG] Starting detection loop for {total_stocks} stocks")
            for idx, stock in enumerate(stocks):
                if not self._is_running:
                    print("[DEBUG] Worker stopped by user")
                    self.progress.emit(idx, total_stocks, "사용자에 의해 중지됨")
                    break

                if idx % 100 == 0:
                    print(f"[DEBUG] Processing stock {idx+1}/{total_stocks}")

                self.progress.emit(
                    idx + 1,
                    total_stocks,
                    f"[{idx+1}/{total_stocks}] {stock['name']} ({stock['code']}) 탐지 중..."
                )

                try:
                    # 블록 탐지 실행 (settings 전달)
                    result = block_detector.detect_all_blocks(
                        stock['code'],
                        start_dt,
                        end_dt,
                        self.settings
                    )

                    blocks_1_count = len(result['blocks_1'])
                    blocks_2_count = len(result['blocks_2'])

                    # 카운트 누적
                    self.total_blocks_1 += blocks_1_count
                    self.total_blocks_2 += blocks_2_count

                    # 종목 완료 시그널
                    if blocks_1_count > 0 or blocks_2_count > 0:
                        print(f"[DEBUG] Blocks found for {stock['name']}: "
                              f"B1={blocks_1_count}, B2={blocks_2_count}")
                        self.stock_completed.emit(
                            stock['name'],
                            blocks_1_count,
                            blocks_2_count
                        )

                except Exception as e:
                    print(f"[ERROR] {stock['name']} ({stock['code']}) "
                          f"탐지 실패: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            # 완료
            print(f"[DEBUG] Detection loop finished. "
                  f"B1={self.total_blocks_1}, B2={self.total_blocks_2}")
            if self._is_running:
                print("[DEBUG] Emitting finished signal (success)")
                self.finished.emit(
                    True, self.total_blocks_1, self.total_blocks_2
                )
            else:
                print("[DEBUG] Emitting finished signal (stopped)")
                self.finished.emit(
                    False, self.total_blocks_1, self.total_blocks_2
                )

        except Exception as e:
            print(f"[DEBUG] Worker exception: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
            self.finished.emit(False, 0, 0)

    def stop(self):
        """탐지 중지"""
        self._is_running = False
