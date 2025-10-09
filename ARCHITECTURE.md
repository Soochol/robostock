# RoboStock 아키텍처 문서

> **Clean Architecture** 기반 설계
> 작성일: 2025-10-08

---

## 📁 **프로젝트 구조**

```
robostock/
├── src/
│   ├── core/                    # 🎯 Core - 시스템 핵심
│   │   ├── config.py           # 전역 설정
│   │   ├── enums.py            # Enum 정의
│   │   ├── signals.py          # Qt 시그널
│   │   └── exceptions.py       # 커스텀 예외 (20+개)
│   │
│   ├── domain/                  # 💎 Domain - 비즈니스 로직 (순수)
│   │   ├── entities/           # 순수 비즈니스 엔티티
│   │   │   ├── stock.py
│   │   │   ├── price_data.py
│   │   │   └── volume_block.py
│   │   │
│   │   ├── repositories/       # Repository 인터페이스 (ABC)
│   │   │   ├── stock_repository.py
│   │   │   ├── price_data_repository.py
│   │   │   └── block_repository.py
│   │   │
│   │   └── services/           # 도메인 서비스 (순수 로직)
│   │       └── block_detection_service.py
│   │
│   ├── application/            # 🎬 Application - 유스케이스
│   │   ├── use_cases/          # Use Case 구현
│   │   │   └── detect_blocks_use_case.py
│   │   │
│   │   └── dto/                # Data Transfer Objects
│   │
│   ├── infrastructure/         # 🔧 Infrastructure - 기술 구현
│   │   ├── database/           # 데이터베이스
│   │   │   ├── connection.py  # DB 연결 (싱글톤)
│   │   │   └── models.py      # SQLAlchemy ORM
│   │   │
│   │   └── repositories/       # Repository 구현체
│   │       ├── sqlalchemy_stock_repository.py
│   │       ├── sqlalchemy_price_data_repository.py
│   │       └── sqlalchemy_block_repository.py
│   │
│   ├── presentation/           # (기존 ui/) - UI 레이어
│   │   ├── windows/
│   │   ├── panels/
│   │   ├── widgets/
│   │   └── workers/
│   │
│   ├── services/               # (레거시) Application Services
│   │   ├── data_collector.py
│   │   ├── block_detector.py  # ⚠️ 마이그레이션 대상
│   │   └── trading_collector.py
│   │
│   ├── data/                   # (하위 호환성) re-export
│   ├── styles/                 # 스타일 & 테마
│   └── resources/              # 아이콘, 폰트
│
├── tests/                      # ✅ 테스트 (분리됨)
│   ├── unit/
│   ├── integration/
│   ├── conftest.py            # pytest 설정
│   └── test_*.py              # 테스트 파일들
│
└── data/                       # 데이터 파일
    └── robostock.db
```

---

## 🏛️ **아키텍처 계층**

### **의존성 방향 (Dependency Rule)**

```
┌─────────────────────────────────────┐
│  Presentation (UI)                  │
│  - PySide6 UI                       │
└─────────────┬───────────────────────┘
              │ depends on
              ↓
┌─────────────────────────────────────┐
│  Application (Use Cases)            │
│  - DetectBlocksUseCase              │
│  - CollectDataUseCase               │
└─────────────┬───────────────────────┘
              │ depends on
              ↓
┌─────────────────────────────────────┐
│  Domain (Business Logic)            │ ← 중심 (의존성 없음!)
│  - Entities (Stock, PriceData)      │
│  - Repositories (Interfaces)        │
│  - Services (BlockDetectionService) │
└─────────────△───────────────────────┘
              │ implements
              │
┌─────────────────────────────────────┐
│  Infrastructure (Tech)              │
│  - SQLAlchemy Repository Impl       │
│  - Database Connection              │
│  - External APIs (pykrx)            │
└─────────────────────────────────────┘
```

**핵심 원칙:**
- ✅ Domain은 아무것도 의존하지 않음 (순수 Python)
- ✅ Infrastructure가 Domain 인터페이스를 **구현**
- ✅ Application이 Domain과 Infrastructure를 **조율**
- ✅ Presentation은 Application을 통해서만 접근

---

## 🔄 **데이터 흐름 (Flow)**

### **예시: 블록 탐지**

```
1. UI (BlockDetectorPanel)
   ↓ 버튼 클릭
2. Worker (BlockDetectionWorker)
   ↓ 호출
3. Use Case (DetectBlocksUseCase)
   ↓
   ├─→ StockRepository.get_by_code()
   ├─→ PriceDataRepository.get_by_stock_range()
   │   ↓
   │   Infrastructure (SQLAlchemy) → Database
   │   ↓
   │   Entity (List[PriceData])
   │
   ├─→ BlockDetectionService.detect_block_1()
   │   ↓
   │   순수 비즈니스 로직 (DataFrame 분석)
   │   ↓
   │   Entity (List[VolumeBlock])
   │
   └─→ BlockRepository.save_bulk()
       ↓
       Infrastructure → Database
```

---

## 🎯 **주요 컴포넌트**

### **1. Domain Entities**

순수 비즈니스 객체 (ORM 독립적)

```python
@dataclass
class Stock:
    code: str
    name: str
    market: MarketType

    def is_kospi(self) -> bool:
        return self.market == MarketType.KOSPI
```

**특징:**
- ORM 모델과 분리
- 비즈니스 로직 메서드 포함
- 유효성 검증 (`__post_init__`)

---

### **2. Repository Pattern**

#### **인터페이스 (domain/repositories/)**

```python
class StockRepository(ABC):
    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Stock]:
        pass

    @abstractmethod
    def save(self, stock: Stock) -> Stock:
        pass
```

#### **구현체 (infrastructure/repositories/)**

```python
class SQLAlchemyStockRepository(StockRepository):
    def get_by_code(self, code: str) -> Optional[Stock]:
        with get_session() as session:
            orm = session.query(StockORM).filter_by(code=code).first()
            return self._to_entity(orm)

    def _to_entity(self, orm: StockORM) -> Stock:
        """ORM → Entity 변환"""
        return Stock(
            id=orm.id,
            code=orm.code,
            name=orm.name,
            market=orm.market
        )
```

**장점:**
- ✅ 테스트 용이 (Mock Repository 주입)
- ✅ DB 교체 가능 (SQLite → PostgreSQL)
- ✅ Domain과 Infrastructure 분리

---

### **3. Domain Services**

순수 비즈니스 로직 (DB 독립)

```python
class BlockDetectionService:
    def detect_block_1_from_data(
        self,
        stock_id: int,
        price_data_list: List[PriceData]
    ) -> List[VolumeBlock]:
        """주가 데이터로부터 블록 탐지 (DB 접근 없음)"""
        # 순수 알고리즘
        # DataFrame 분석
        # 조건 검사
        return blocks
```

---

### **4. Use Cases**

애플리케이션 로직 (조율자)

```python
class DetectBlocksUseCase:
    def __init__(
        self,
        stock_repo: StockRepository,
        price_data_repo: PriceDataRepository,
        block_repo: BlockRepository
    ):
        self._stock_repo = stock_repo
        self._price_data_repo = price_data_repo
        self._block_repo = block_repo
        self._service = BlockDetectionService()

    def execute(self, stock_code: str, start_date, end_date):
        # 1. Repository로 데이터 조회
        stock = self._stock_repo.get_by_code(stock_code)
        price_data = self._price_data_repo.get_by_stock_range(...)

        # 2. Domain Service로 블록 탐지
        blocks = self._service.detect_block_1_from_data(...)

        # 3. Repository로 저장
        self._block_repo.save_bulk(blocks)

        return result
```

---

## 🧪 **테스트 전략**

### **1. Unit Tests (domain/)**

```python
def test_block_detection_service():
    # Given
    service = BlockDetectionService()
    price_data = [
        PriceData(stock_id=1, date=date(2024,1,1), ...),
        # ...
    ]

    # When
    blocks = service.detect_block_1_from_data(1, price_data)

    # Then
    assert len(blocks) > 0
    assert blocks[0].block_type == BlockType.BLOCK_1
```

**Mock 불필요** - 순수 로직만 테스트

---

### **2. Integration Tests (repositories/)**

```python
def test_stock_repository(db_session):
    # Given
    repo = SQLAlchemyStockRepository()
    stock = Stock(code="005930", name="삼성전자", market=MarketType.KOSPI)

    # When
    saved = repo.save(stock)
    retrieved = repo.get_by_code("005930")

    # Then
    assert retrieved.name == "삼성전자"
```

---

## 📊 **마이그레이션 가이드**

### **Before (레거시)**

```python
# services/block_detector.py
class BlockDetector:
    def detect_all_blocks(self, stock_code, start_date, end_date):
        with get_session() as session:  # 직접 DB 접근
            stock = session.query(Stock).filter_by(code=stock_code).first()
            # ...
```

### **After (Clean Architecture)**

```python
# application/use_cases/detect_blocks_use_case.py
class DetectBlocksUseCase:
    def __init__(self, stock_repo, price_repo, block_repo):
        self._stock_repo = stock_repo  # 인터페이스 주입

    def execute(self, stock_code, start_date, end_date):
        stock = self._stock_repo.get_by_code(stock_code)
        # ...
```

---

## 🚀 **향후 확장**

### **1. 캐싱 레이어 추가**

```python
# infrastructure/cache/redis_cache.py
class CachedStockRepository(StockRepository):
    def __init__(self, base_repo, redis_client):
        self._base = base_repo
        self._cache = redis_client

    def get_by_code(self, code):
        # 캐시 확인 → DB 조회
```

### **2. 외부 API 추상화**

```python
# domain/repositories/market_data_provider.py
class MarketDataProvider(ABC):
    @abstractmethod
    def fetch_ohlcv(self, code, start, end):
        pass

# infrastructure/external/pykrx_provider.py
class PykrxMarketDataProvider(MarketDataProvider):
    def fetch_ohlcv(self, code, start, end):
        return pykrx_stock.get_market_ohlcv(...)
```

---

## 📚 **참고 자료**

- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)
- Repository Pattern (Martin Fowler)
- [PEP 8](https://peps.python.org/pep-0008/) - Python Style Guide

---

## ✅ **체크리스트**

- [x] Domain 계층 분리
- [x] Repository 패턴 적용
- [x] Entity와 ORM 분리
- [x] Use Case 구현
- [x] 예외 처리 체계화
- [x] 테스트 구조 개선
- [ ] 전체 서비스 마이그레이션
- [ ] 통합 테스트 작성
- [ ] API 문서화 (Swagger)
- [ ] 성능 최적화

---

**작성자**: Claude Code
**버전**: 1.0.0
**최종 수정일**: 2025-10-08
