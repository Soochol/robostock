# 📊 로그 포맷 가이드

> 데이터 수집 로그 개선 (2025-10-08)

---

## 🎨 **새로운 로그 포맷**

### **Before (기존)**
```
[OK] CJ (001040): 2643 price + 2643 trading records - 16.10s
[OK] AJ네트웍스 (095570): 2485 price + 2472 trading records - 15.35s
[OK] CJ대한통운 (000120): 2643 price + 2643 trading records - 16.18s
```

**문제점:**
- ❌ 가독성 부족
- ❌ 정렬 안됨
- ❌ 진행률 표시 없음
- ❌ 실시간 통계 없음

---

### **After (개선)**

#### **Option 1: Compact 포맷 (기본)** ✨

```
   1/2900 ✓ CJ               (001040)  2.6K↓ +  2.6K↑  16.1s   164rec/s
   2/2900 ✓ AJ네트웍스       (095570)  2.5K↓ +  2.5K↑  15.4s   161rec/s
   3/2900 ✓ CJ대한통운       (000120)  2.6K↓ +  2.6K↑  16.2s   163rec/s
   4/2900 ⊘ CJ씨푸드         (011150)  Up-to-date (2025-01-05)   0.2s
   5/2900 ✗ CJ제일제당       (097950)  API timeout              30.0s

────────────────────────────────────────────────────────────────────────────────
[████████████████████] 50.0% | ✓ 1,420 | ⊘ 45 | ✗ 8 | ⚡ 14.2s/stock | ⏱ 3m 24s left
────────────────────────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════════════════════════
📊 COLLECTION SUMMARY
════════════════════════════════════════════════════════════════════════════════
Total Stocks:  2,900
  ✓ Success:       2,785 (96.0%)
  ⊘ Skipped:          98 ( 3.4%)
  ✗ Failed:           17 ( 0.6%)

Total Time:    68m 15s (4095.0s)
Average:       1.41s per stock
Throughput:    42.6 stocks/min
════════════════════════════════════════════════════════════════════════════════
```

**특징:**
- ✅ 색상 하이라이팅 (성공=녹색, 실패=빨강, 스킵=노랑)
- ✅ 숫자 포맷팅 (K, M 단위)
- ✅ 실시간 진행률 (50개마다)
- ✅ ETA (남은 시간 계산)
- ✅ 속도 표시 (records/sec)
- ✅ 최종 요약 통계

---

#### **Option 2: Detailed 포맷 (테이블)**

```
────────────────────────────────────────────────────────────────────────────────────────────────
     IDX │ STATUS │ STOCK NAME           │   CODE   │    PRICE │    TRADE │     TIME │      SPEED
────────────────────────────────────────────────────────────────────────────────────────────────
  1/2900 │   OK   │ CJ                   │  001040  │    2,643 │    2,643 │   16.10s │   328 r/s
  2/2900 │   OK   │ AJ네트웍스           │  095570  │    2,485 │    2,472 │   15.35s │   323 r/s
  3/2900 │   OK   │ CJ대한통운           │  000120  │    2,643 │    2,643 │   16.18s │   326 r/s
  4/2900 │  SKIP  │ CJ씨푸드             │  011150  │ Up-to-date (2025-01-05) │    0.20s │     0 r/s
  5/2900 │  ERROR │ CJ제일제당           │  097950  │ API timeout             │   30.00s │     0 r/s
```

**특징:**
- ✅ 완벽한 테이블 정렬
- ✅ 컬럼 헤더 (50개마다 반복)
- ✅ 명확한 구분
- ✅ 대용량 데이터 수집에 적합

---

## ⚙️ **설정 방법**

### **1. Config 파일 수정**

[src/core/config.py](src/core/config.py#L280):

```python
COLLECTION_LOG_CONFIG = {
    'style': 'compact',      # 'compact', 'detailed', 'simple'
    'use_colors': True,      # 색상 사용 여부
    'show_progress_bar': True,  # 프로그레스 바 표시
    'summary_interval': 50,  # 요약 출력 간격 (몇 개마다)
    'show_speed': True,      # 속도 표시 (records/sec)
    'show_eta': True,        # 남은 시간 표시
}
```

### **2. 스타일 변경**

#### **Compact (컴팩트)** - 기본값
```python
'style': 'compact'
```
- 가독성과 정보량의 균형
- 색상 하이라이팅
- 프로그레스 바

#### **Detailed (상세)** - 테이블
```python
'style': 'detailed'
```
- 완벽한 테이블 정렬
- 컬럼 헤더
- 대용량 데이터 적합

#### **Simple (심플)** - 최소
```python
'style': 'simple'
```
- 기존 로그 스타일 (fallback)
- 색상 없음
- 최소 정보만

### **3. 색상 끄기 (CI/CD 환경)**

```python
'use_colors': False  # 터미널이 색상을 지원하지 않을 때
```

---

## 🔍 **로그 레벨 및 상태**

### **상태 심볼**

| 심볼 | 의미 | 색상 |
|------|------|------|
| ✓ | Success (성공) | 🟢 녹색 |
| ⊘ | Skip (스킵) | 🟡 노랑 |
| ✗ | Error (실패) | 🔴 빨강 |
| ℹ | Info (정보) | 🔵 파랑 |
| ⚠ | Warning (경고) | 🟠 주황 |

### **스킵 사유**

```
⊘ Up-to-date (2025-01-05)     # 최신 데이터 (업데이트 불필요)
⊘ No new data in API           # API에 신규 데이터 없음
⊘ Cached                        # 캐시됨
```

### **에러 유형**

```
✗ API timeout                   # API 타임아웃
✗ Connection failed             # 연결 실패
✗ Invalid data                  # 잘못된 데이터
✗ Rate limit exceeded           # API 호출 제한 초과
```

---

## 📈 **실시간 통계**

### **프로그레스 바 (50개마다 출력)**

```
────────────────────────────────────────────────────────────────────────────────
[████████████████████] 50.0% | ✓ 1,420 | ⊘ 45 | ✗ 8 | ⚡ 14.2s/stock | ⏱ 3m 24s left
────────────────────────────────────────────────────────────────────────────────
```

**포함 정보:**
- 📊 진행률 바 (시각적)
- 📈 퍼센트 (%)
- ✓ 성공 수
- ⊘ 스킵 수
- ✗ 실패 수
- ⚡ 평균 속도 (초/종목)
- ⏱ ETA (남은 시간)

### **최종 요약**

```
════════════════════════════════════════════════════════════════════════════════
📊 COLLECTION SUMMARY
════════════════════════════════════════════════════════════════════════════════
Total Stocks:  2,900
  ✓ Success:       2,785 (96.0%)
  ⊘ Skipped:          98 ( 3.4%)
  ✗ Failed:           17 ( 0.6%)

Total Time:    68m 15s (4095.0s)
Average:       1.41s per stock
Throughput:    42.6 stocks/min
════════════════════════════════════════════════════════════════════════════════
```

---

## 🎯 **사용 예시**

### **Python 코드에서 직접 사용**

```python
from shared.utils.collection_logger import CollectionLogger, DetailedLogger

# Compact 로거
logger = CollectionLogger(total_count=1000, use_colors=True)

# 성공
logger.log_success(
    stock_name="삼성전자",
    stock_code="005930",
    price_count=2643,
    trading_count=2643,
    elapsed=16.1
)

# 스킵
logger.log_skip(
    stock_name="SK하이닉스",
    stock_code="000660",
    reason="Up-to-date (2025-01-05)",
    elapsed=0.2
)

# 에러
logger.log_error(
    stock_name="LG화학",
    stock_code="051910",
    error_msg="API timeout",
    elapsed=30.0
)

# 최종 요약
logger.log_final_summary()
```

### **DataCollector에서 자동 사용**

```python
from services.data_collector import data_collector

# 병렬 수집 (자동으로 새 로거 사용)
data_collector.collect_all_stocks_parallel(
    market=MarketType.KOSPI,
    max_workers=10
)
```

---

## 🔧 **커스터마이징**

### **자체 로거 구현**

```python
from shared.utils.collection_logger import CollectionLogger

class MyCustomLogger(CollectionLogger):
    def log_success(self, stock_name, stock_code, price_count, trading_count, elapsed):
        # 커스텀 포맷
        print(f"✨ {stock_name} completed in {elapsed}s!")

        # 부모 메서드 호출
        super().log_success(stock_name, stock_code, price_count, trading_count, elapsed)
```

### **조건부 로깅**

```python
# 실패만 로그
if not result['success']:
    logger.log_error(...)

# 느린 종목만 로그 (10초 이상)
if elapsed > 10:
    logger.log_success(...)
```

---

## 💡 **성능 팁**

1. **색상 비활성화** (로그 파일 출력 시)
   ```python
   'use_colors': False
   ```

2. **요약 간격 조정** (성능 향상)
   ```python
   'summary_interval': 100  # 50 → 100으로 증가
   ```

3. **ETA 비활성화** (계산 부하 감소)
   ```python
   'show_eta': False
   ```

---

## 📝 **변경 이력**

### v1.0.0 (2025-10-08)
- ✨ 새로운 로그 포맷 3가지 추가
- ✅ 색상 하이라이팅
- ✅ 실시간 진행률 및 ETA
- ✅ 최종 요약 통계
- ✅ 설정 가능한 스타일

---

**작성자**: Claude Code
**버전**: 1.0.0
**파일**: [collection_logger.py](src/shared/utils/collection_logger.py)
