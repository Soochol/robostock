# 마이그레이션 가이드

> 기존 코드를 Clean Architecture로 전환하는 방법

---

## 📋 **현재 상태**

### ✅ **완료된 작업 (Phase 1-4)**

1. **Phase 1: Quick Wins**
   - ✅ 빈 폴더 6개 제거
   - ✅ 테스트 파일 `tests/` 폴더로 이동
   - ✅ `core/exceptions.py` 추가 (20개 커스텀 예외)

2. **Phase 2: Repository 패턴 도입**
   - ✅ `domain/repositories/` 인터페이스 3개
   - ✅ `domain/entities/` 순수 엔티티 3개
   - ✅ `infrastructure/repositories/` 구현체 3개
   - ✅ `data/` → `infrastructure/database/` 이동 (하위 호환성 유지)

3. **Phase 3: 도메인 서비스 분리**
   - ✅ `domain/services/block_detection_service.py`

4. **Phase 4: Application 계층**
   - ✅ `application/use_cases/detect_blocks_use_case.py`

---

## 🔄 **남은 마이그레이션 작업**

### **1. services/data_collector.py 리팩토링**

#### **현재 구조 (777줄)**
```python
# services/data_collector.py
class DataCollector:
    def collect_all_stocks(self, market, start_date, end_date):
        # 1. 종목 리스트 조회
        # 2. DB 저장
        # 3. 주가 데이터 수집
        # 4. 수급 데이터 수집
        with get_session() as session:  # 직접 DB 접근
            stock = session.query(Stock).filter_by(code=code).first()
            # ...
```

#### **목표 구조 (모듈 분리)**

```
application/
└── data_collection/
    ├── collectors/
    │   ├── stock_list_collector.py       # 종목 리스트 수집
    │   ├── price_data_collector.py       # 주가 데이터 수집
    │   └── trading_data_collector.py     # 수급 데이터 수집
    │
    ├── strategies/
    │   ├── sequential_strategy.py        # 순차 수집
    │   └── parallel_strategy.py          # 병렬 수집
    │
    └── use_cases/
        ├── collect_stock_list_use_case.py
        ├── collect_price_data_use_case.py
        └── collect_all_data_use_case.py
```

#### **마이그레이션 예시**

**Before:**
```python
# services/data_collector.py
class DataCollector:
    def save_price_data_to_db(self, stock_code, df):
        with get_session() as session:
            stock = session.query(Stock).filter_by(code=stock_code).first()
            for idx, row in df.iterrows():
                price_data = PriceData(
                    stock_id=stock.id,
                    date=idx.date(),
                    open=row['시가'],
                    # ...
                )
                session.add(price_data)
```

**After:**
```python
# application/use_cases/collect_price_data_use_case.py
class CollectPriceDataUseCase:
    def __init__(
        self,
        stock_repo: StockRepository,
        price_data_repo: PriceDataRepository,
        market_data_provider: MarketDataProvider
    ):
        self._stock_repo = stock_repo
        self._price_data_repo = price_data_repo
        self._provider = market_data_provider

    def execute(self, stock_code: str, start_date, end_date):
        # 1. 종목 조회
        stock = self._stock_repo.get_by_code(stock_code)

        # 2. 외부 API로 데이터 수집
        raw_data = self._provider.fetch_ohlcv(stock_code, start_date, end_date)

        # 3. Entity로 변환
        price_entities = [
            PriceData(
                stock_id=stock.id,
                date=row['date'],
                open=row['open'],
                # ...
            )
            for row in raw_data
        ]

        # 4. 저장
        saved_count = self._price_data_repo.save_bulk(price_entities)

        return saved_count
```

---

### **2. 외부 API 추상화 (pykrx)**

#### **인터페이스 정의**

```python
# domain/repositories/market_data_provider.py
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import date

class MarketDataProvider(ABC):
    """시장 데이터 제공자 인터페이스"""

    @abstractmethod
    def get_stock_list(self, market: str, target_date: date) -> List[Dict]:
        """종목 리스트 조회"""
        pass

    @abstractmethod
    def fetch_ohlcv(
        self,
        stock_code: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """OHLCV 데이터 조회"""
        pass

    @abstractmethod
    def fetch_trading_data(
        self,
        stock_code: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """투자자별 거래 데이터 조회"""
        pass
```

#### **구현체**

```python
# infrastructure/external/pykrx_provider.py
from domain.repositories.market_data_provider import MarketDataProvider
from pykrx import stock as pykrx_stock
from core.exceptions import PykrxAPIException

class PykrxMarketDataProvider(MarketDataProvider):
    """pykrx 기반 시장 데이터 제공자"""

    def get_stock_list(self, market: str, target_date: date) -> List[Dict]:
        try:
            date_str = target_date.strftime("%Y%m%d")
            codes = pykrx_stock.get_market_ticker_list(date_str, market=market)

            return [
                {
                    'code': code,
                    'name': pykrx_stock.get_market_ticker_name(code),
                    'market': market
                }
                for code in codes
            ]
        except Exception as e:
            raise PykrxAPIException('get_stock_list', str(e))

    def fetch_ohlcv(self, stock_code, start_date, end_date):
        try:
            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")

            df = pykrx_stock.get_market_ohlcv(start_str, end_str, stock_code)

            if df is None or df.empty:
                return []

            # DataFrame → Dict 리스트 변환
            result = []
            for idx, row in df.iterrows():
                result.append({
                    'date': idx.date(),
                    'open': float(row['시가']),
                    'high': float(row['고가']),
                    'low': float(row['저가']),
                    'close': float(row['종가']),
                    'volume': int(row['거래량'])
                })

            return result

        except Exception as e:
            raise PykrxAPIException('fetch_ohlcv', str(e))
```

---

### **3. UI 레이어 연결**

#### **현재 (직접 Service 호출)**

```python
# ui/panels/data_collection_panel.py
from services.data_collector import data_collector

class DataCollectionPanel(QWidget):
    def start_collection(self):
        # 직접 서비스 호출
        data_collector.collect_all_stocks(
            market=market,
            start_date=start_date,
            end_date=end_date
        )
```

#### **개선 (Use Case 주입)**

```python
# ui/panels/data_collection_panel.py
from application.use_cases.collect_all_data_use_case import CollectAllDataUseCase

class DataCollectionPanel(QWidget):
    def __init__(self, collect_use_case: CollectAllDataUseCase):
        super().__init__()
        self._collect_use_case = collect_use_case

    def start_collection(self):
        # Use Case 실행
        self._collect_use_case.execute(
            market=market,
            start_date=start_date,
            end_date=end_date,
            progress_callback=self.on_progress
        )
```

#### **의존성 주입 (main.py)**

```python
# main.py
from infrastructure.repositories.sqlalchemy_stock_repository import SQLAlchemyStockRepository
from infrastructure.repositories.sqlalchemy_price_data_repository import SQLAlchemyPriceDataRepository
from infrastructure.external.pykrx_provider import PykrxMarketDataProvider
from application.use_cases.collect_all_data_use_case import CollectAllDataUseCase

def main():
    # 데이터베이스 초기화
    init_database()

    # Repository 생성
    stock_repo = SQLAlchemyStockRepository()
    price_data_repo = SQLAlchemyPriceDataRepository()

    # External Provider
    market_data_provider = PykrxMarketDataProvider()

    # Use Case 생성 (의존성 주입)
    collect_use_case = CollectAllDataUseCase(
        stock_repo=stock_repo,
        price_data_repo=price_data_repo,
        provider=market_data_provider
    )

    # Qt App
    app = QApplication(sys.argv)

    # UI에 Use Case 주입
    window = MainWindow(collect_use_case=collect_use_case)
    window.show()

    sys.exit(app.exec())
```

---

## 🧪 **테스트 작성**

### **1. Domain 테스트 (순수 로직)**

```python
# tests/unit/domain/test_block_detection_service.py
import pytest
from domain.services.block_detection_service import BlockDetectionService
from domain.entities.price_data import PriceData
from datetime import date

def test_detect_block_1():
    # Given
    service = BlockDetectionService()
    price_data = [
        PriceData(
            stock_id=1,
            date=date(2024, 1, 1),
            open=10000,
            high=11000,
            low=9800,
            close=10500,
            volume=1000000,
            trading_value=100_000_000_000  # 1000억
        ),
        # ... more data
    ]

    # When
    blocks = service.detect_block_1_from_data(1, price_data)

    # Then
    assert len(blocks) > 0
    assert blocks[0].trading_value >= 50_000_000_000
```

### **2. Repository 테스트 (Integration)**

```python
# tests/integration/test_repositories.py
import pytest
from infrastructure.repositories.sqlalchemy_stock_repository import SQLAlchemyStockRepository
from domain.entities.stock import Stock
from core.enums import MarketType

@pytest.fixture
def stock_repo():
    return SQLAlchemyStockRepository()

def test_save_and_retrieve_stock(stock_repo):
    # Given
    stock = Stock(
        code="005930",
        name="삼성전자",
        market=MarketType.KOSPI
    )

    # When
    saved = stock_repo.save(stock)
    retrieved = stock_repo.get_by_code("005930")

    # Then
    assert retrieved is not None
    assert retrieved.name == "삼성전자"
    assert retrieved.market == MarketType.KOSPI
```

### **3. Use Case 테스트 (Mocking)**

```python
# tests/unit/application/test_detect_blocks_use_case.py
import pytest
from unittest.mock import Mock
from application.use_cases.detect_blocks_use_case import DetectBlocksUseCase

def test_execute():
    # Given
    mock_stock_repo = Mock()
    mock_price_repo = Mock()
    mock_block_repo = Mock()

    use_case = DetectBlocksUseCase(
        stock_repo=mock_stock_repo,
        price_data_repo=mock_price_repo,
        block_repo=mock_block_repo
    )

    # When
    result = use_case.execute("005930", date(2024,1,1), date(2024,12,31))

    # Then
    assert mock_stock_repo.get_by_code.called
    assert mock_price_repo.get_by_stock_range.called
```

---

## 📝 **체크리스트**

### **단계별 마이그레이션**

- [x] Phase 1: Quick Wins
- [x] Phase 2: Repository 패턴
- [x] Phase 3: Domain Services
- [x] Phase 4: Application Use Cases
- [ ] Phase 5: 외부 API 추상화
- [ ] Phase 6: 서비스 계층 리팩토링
- [ ] Phase 7: UI 의존성 주입
- [ ] Phase 8: 통합 테스트
- [ ] Phase 9: 성능 최적화
- [ ] Phase 10: 문서화 완료

---

## ⚠️ **주의사항**

1. **하위 호환성 유지**
   - `data/__init__.py`에서 re-export로 기존 코드 동작 보장
   - 점진적 마이그레이션 (Big Bang 금지)

2. **테스트 먼저 작성**
   - 리팩토링 전 기존 동작을 테스트로 고정
   - 리팩토링 후 동일한 테스트 통과 확인

3. **한 번에 하나씩**
   - 한 모듈씩 마이그레이션
   - 각 단계마다 커밋

---

## 🚀 **다음 단계**

1. **`MarketDataProvider` 인터페이스 구현**
   - pykrx 래퍼 작성
   - 예외 처리 통일

2. **`CollectDataUseCase` 작성**
   - 데이터 수집 로직 분리
   - 병렬 처리 전략 구현

3. **UI 의존성 주입 설정**
   - main.py에서 컨테이너 구성
   - 각 Panel에 Use Case 주입

4. **통합 테스트 작성**
   - E2E 시나리오 테스트
   - 성능 벤치마크

---

**작성자**: Claude Code
**최종 수정**: 2025-10-08
