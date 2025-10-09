"""
Collection Logger
데이터 수집 로그 포맷팅 유틸리티
"""

from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """로그 레벨"""
    SUCCESS = "OK"
    SKIP = "SKIP"
    ERROR = "ERR"
    INFO = "INFO"
    WARNING = "WARN"


class CollectionLogger:
    """
    데이터 수집 로그 포맷터

    깔끔하고 가독성 높은 로그 출력
    """

    def __init__(self, total_count: int = 0, use_colors: bool = True):
        """
        Args:
            total_count: 전체 작업 수
            use_colors: 색상 사용 여부
        """
        self.total_count = total_count
        self.use_colors = use_colors
        self.start_time = datetime.now()
        self.completed = 0
        self.success = 0
        self.skip = 0
        self.error = 0

        # ANSI 색상 코드
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'gray': '\033[90m',
            'bold': '\033[1m',
            'reset': '\033[0m',
        } if use_colors else {
            'green': '', 'yellow': '', 'red': '', 'blue': '',
            'cyan': '', 'gray': '', 'bold': '', 'reset': ''
        }

    def _colorize(self, text: str, color: str) -> str:
        """텍스트에 색상 적용"""
        return f"{self.colors[color]}{text}{self.colors['reset']}"

    def _format_number(self, num: int) -> str:
        """숫자 포맷팅 (K, M 단위)"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)

    def _format_progress_bar(self, percentage: float, width: int = 10) -> str:
        """프로그레스 바 생성"""
        filled = int(width * percentage / 100)
        bar = '#' * filled + '-' * (width - filled)
        return bar

    def _calculate_eta(self) -> str:
        """ETA (남은 시간) 계산"""
        if self.completed == 0:
            return "calculating..."

        elapsed = (datetime.now() - self.start_time).total_seconds()
        avg_time = elapsed / self.completed
        remaining = self.total_count - self.completed
        eta_seconds = avg_time * remaining

        if eta_seconds < 60:
            return f"{int(eta_seconds)}s"
        elif eta_seconds < 3600:
            minutes = int(eta_seconds // 60)
            seconds = int(eta_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(eta_seconds // 3600)
            minutes = int((eta_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def log_success(
        self,
        stock_name: str,
        stock_code: str,
        price_count: int,
        trading_count: int,
        elapsed: float
    ):
        """성공 로그"""
        self.completed += 1
        self.success += 1

        # 포맷팅
        index = f"{self.completed:4d}/{self.total_count}"
        symbol = self._colorize(LogLevel.SUCCESS.value, 'green')
        name = f"{stock_name:15s}"
        code = self._colorize(f"({stock_code})", 'gray')

        price_str = self._colorize(f"{self._format_number(price_count):>6s}P", 'cyan')
        trade_str = self._colorize(f"{self._format_number(trading_count):>6s}T", 'blue')
        time_str = self._colorize(f"{elapsed:5.1f}s", 'gray')

        # 속도 계산
        total_records = price_count + trading_count
        speed = int(total_records / elapsed) if elapsed > 0 else 0
        speed_str = self._colorize(f"{speed:4d}rec/s", 'green')

        print(f"{index} {symbol} {name} {code} {price_str} + {trade_str}  {time_str} {speed_str}")

    def log_skip(
        self,
        stock_name: str,
        stock_code: str,
        reason: str,
        elapsed: float
    ):
        """스킵 로그"""
        self.completed += 1
        self.skip += 1

        index = f"{self.completed:4d}/{self.total_count}"
        symbol = self._colorize(LogLevel.SKIP.value, 'yellow')
        name = f"{stock_name:15s}"
        code = self._colorize(f"({stock_code})", 'gray')
        reason_str = self._colorize(f"{reason:30s}", 'yellow')
        time_str = self._colorize(f"{elapsed:5.1f}s", 'gray')

        print(f"{index} {symbol} {name} {code} {reason_str}  {time_str}")

    def log_error(
        self,
        stock_name: str,
        stock_code: str,
        error_msg: str,
        elapsed: float
    ):
        """에러 로그"""
        self.completed += 1
        self.error += 1

        index = f"{self.completed:4d}/{self.total_count}"
        symbol = self._colorize(LogLevel.ERROR.value, 'red')
        name = f"{stock_name:15s}"
        code = self._colorize(f"({stock_code})", 'gray')
        error_str = self._colorize(f"{error_msg:30s}", 'red')
        time_str = self._colorize(f"{elapsed:5.1f}s", 'gray')

        print(f"{index} {symbol} {name} {code} {error_str}  {time_str}")

    def log_summary_inline(self):
        """인라인 요약 (주기적으로 출력)"""
        if self.completed % 50 == 0 and self.completed > 0:
            percentage = (self.completed / self.total_count * 100) if self.total_count > 0 else 0

            success_str = self._colorize(f"OK: {self.success}", 'green')
            skip_str = self._colorize(f"SKIP: {self.skip}", 'yellow')
            error_str = self._colorize(f"ERR: {self.error}", 'red')

            elapsed = (datetime.now() - self.start_time).total_seconds()
            avg_time = elapsed / self.completed if self.completed > 0 else 0
            eta = self._calculate_eta()

            bar = self._format_progress_bar(percentage, width=20)

            print(f"\n{'-' * 80}")
            print(f"[{bar}] {percentage:5.1f}% | {success_str} | {skip_str} | {error_str} | "
                  f"Speed: {avg_time:.1f}s/stock | ETA: {eta}")
            print(f"{'-' * 80}\n")

    def log_final_summary(self):
        """최종 요약"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        avg_time = elapsed / self.total_count if self.total_count > 0 else 0

        print(f"\n{'=' * 80}")
        print(f"{self._colorize('COLLECTION SUMMARY', 'bold')}")
        print(f"{'=' * 80}")

        # 통계
        print(f"Total Stocks:  {self.total_count:,}")
        print(f"  {self._colorize('Success:', 'green'):20s} {self.success:,} ({self.success/self.total_count*100:.1f}%)")
        print(f"  {self._colorize('Skipped:', 'yellow'):20s} {self.skip:,} ({self.skip/self.total_count*100:.1f}%)")
        print(f"  {self._colorize('Failed:', 'red'):20s} {self.error:,} ({self.error/self.total_count*100:.1f}%)")

        # 시간
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        print(f"\nTotal Time:    {minutes}m {seconds}s ({elapsed:.1f}s)")
        print(f"Average:       {avg_time:.2f}s per stock")

        # 속도
        if elapsed > 0:
            throughput = self.total_count / elapsed * 60
            print(f"Throughput:    {throughput:.1f} stocks/min")

        print(f"{'=' * 80}\n")


class CompactLogger(CollectionLogger):
    """더욱 압축된 로그 포맷"""

    def log_success(self, stock_name: str, stock_code: str, price_count: int, trading_count: int, elapsed: float):
        self.completed += 1
        self.success += 1

        idx = f"{self.completed}/{self.total_count}"
        symbol = self._colorize("✓", 'green')
        name = f"{stock_name[:12]:12s}"
        data = f"{self._format_number(price_count):>5s}+{self._format_number(trading_count):>5s}"
        time = f"{elapsed:4.1f}s"

        print(f"{idx:>10s} {symbol} {name} {data}  {time}")


class DetailedLogger(CollectionLogger):
    """상세한 로그 포맷 (테이블 형식)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._print_header()

    def _print_header(self):
        """테이블 헤더 출력"""
        print(f"\n{'─' * 100}")
        print(f"{'IDX':>8s} │ {'STATUS':^6s} │ {'STOCK NAME':20s} │ {'CODE':^8s} │ "
              f"{'PRICE':>8s} │ {'TRADE':>8s} │ {'TIME':>8s} │ {'SPEED':>10s}")
        print(f"{'─' * 100}")

    def log_success(self, stock_name: str, stock_code: str, price_count: int, trading_count: int, elapsed: float):
        self.completed += 1
        self.success += 1

        if self.completed % 50 == 1 and self.completed > 1:
            self._print_header()

        idx = f"{self.completed}/{self.total_count}"
        status = self._colorize("OK", 'green')
        name = f"{stock_name[:20]:20s}"
        code = f"{stock_code:^8s}"
        price = f"{price_count:,}"
        trade = f"{trading_count:,}"
        time = f"{elapsed:.2f}s"

        total = price_count + trading_count
        speed = int(total / elapsed) if elapsed > 0 else 0
        speed_str = f"{speed:,} r/s"

        print(f"{idx:>8s} │ {status:^6s} │ {name} │ {code} │ "
              f"{price:>8s} │ {trade:>8s} │ {time:>8s} │ {speed_str:>10s}")
