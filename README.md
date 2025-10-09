# 🎯 RoboStock

**거래량 블록 기반 장기투자 분석 플랫폼**

프리미엄 모던 트레이딩 플랫폼 - PySide6 기반 데스크톱 애플리케이션

---

## ✨ 주요 기능

- 🔍 **거래량 블록 탐지**: 1번/2번/3번/4번 블록 자동 탐지
- 📊 **팩터 분석**: 기술적/재무/수급/산업 4개 팩터 종합 분석
- 🧠 **AI 예측**: 머신러닝 기반 Level 0~4 성공 확률 예측
- 📈 **프리미엄 차트**: Glassmorphism 디자인, 인터랙티브 차트
- ⚡ **백테스팅**: 10년 데이터 기반 전략 검증

---

## 🚀 빠른 시작

### 1. 환경 설정

**필수 요구사항:**
- Python 3.10 이상
- Windows 10/11 (현재 테스트 환경)

### 2. 의존성 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 실행

```bash
# src 디렉토리에서 실행
cd src
python main.py

# 또는 프로젝트 루트에서
python src/main.py
```

---

## 📐 프로젝트 구조

```
robostock/
├── src/
│   ├── main.py                   # 앱 진입점
│   │
│   ├── core/                     # 핵심 모듈
│   │   ├── config.py             # 전역 설정
│   │   ├── enums.py              # Enum 정의
│   │   └── signals.py            # 전역 시그널
│   │
│   ├── styles/                   # 디자인 시스템
│   │   ├── colors.py             # 컬러 팔레트 (Glassmorphism)
│   │   ├── typography.py         # 타이포그래피
│   │   └── theme.py              # 테마 매니저
│   │
│   ├── ui/                       # UI 컴포넌트
│   │   ├── windows/              # 최상위 윈도우
│   │   │   └── main_window.py    # 메인 윈도우 (3-Zone 레이아웃)
│   │   ├── panels/               # 기능별 패널
│   │   │   └── block_detector_panel.py  # 블록 탐지 패널
│   │   └── widgets/              # 재사용 가능 위젯
│   │       ├── common/
│   │       │   ├── gradient_progress_bar.py
│   │       │   └── glass_card.py
│   │       ├── charts/           # (예정)
│   │       ├── cards/            # (예정)
│   │       └── controls/         # (예정)
│   │
│   ├── models/                   # 데이터 모델 (예정)
│   └── services/                 # 비즈니스 로직 (예정)
│
├── data/                         # 데이터 저장소
│   ├── robostock.db              # SQLite DB
│   └── logs/                     # 로그 파일
│
├── resources/                    # 리소스 파일
│   ├── icons/                    # 아이콘
│   └── fonts/                    # 폰트
│
├── requirements.txt              # 의존성 패키지
└── README.md
```

---

## 🎨 디자인 시스템

### 컬러 팔레트 (다크 모드)

- **배경**: Glassmorphism 효과 (`rgba(37, 42, 58, 0.7)`)
- **프라이머리**: 블루 그라데이션 (`#667eea → #764ba2`)
- **블록 색상**:
  - 1번 블록: 네온 핑크 `#FF0080`
  - 2번 블록: 네온 그린 `#00FF88`
  - 3번 블록: 네온 사이언 `#00D4FF`
  - 4번 블록: 네온 골드 `#FFD700`

### 타이포그래피

- **Primary**: Inter (본문)
- **Display**: Poppins (숫자, 제목)
- **Mono**: JetBrains Mono (코드)

### 레이아웃 모드

1. **Standard**: 기본 3-Zone (컨트롤 180px + 비주얼 60% + 인사이트 380px)
2. **Focus**: 차트 집중 모드 (사이드바 축소)
3. **Analysis**: 분석 집중 모드 (인사이트 패널 확대)

---

## 🔧 개발 진행 상황

### ✅ 완료된 작업

- [x] **Phase 1**: 프로젝트 기반 구조 + 디자인 시스템
  - [x] 디렉토리 구조
  - [x] Glassmorphism 컬러 팔레트
  - [x] 타이포그래피 시스템
  - [x] 전역 설정 (config.py)
  - [x] Enum 정의 (enums.py)
  - [x] 시그널 허브 (signals.py)

- [x] **Phase 2**: 메인 윈도우 + 3-Zone 레이아웃
  - [x] 헤더 (로고, 검색, 알림)
  - [x] 컨트롤존 (사이드바)
  - [x] 비주얼존 (메인 캔버스)
  - [x] 인사이트존 (우측 패널)
  - [x] 상태바

- [x] **Phase 3**: 블록 탐지 UI
  - [x] 3-Step 카드 레이아웃 (기간 선택 → 조건 설정 → 실행)
  - [x] 그라데이션 프로그레스 바
  - [x] 탐지 결과 테이블
  - [x] Glassmorphism 카드 위젯

### 🔨 진행 예정

- [ ] **Phase 4**: 프리미엄 차트 시각화
  - [ ] 캔들스틱 차트 + 블록 마커
  - [ ] 거래량 바차트
  - [ ] 플로팅 타임라인 컨트롤
  - [ ] 스마트 인사이트 바

- [ ] **Phase 5**: 인사이트존 상세 구현
  - [ ] 성공 확률 카드
  - [ ] 블록 정보 미니 카드
  - [ ] 레이더 차트 (팩터 점수)
  - [ ] Level 확률 분포
  - [ ] 투자 제안 섹션

- [ ] **Phase 6**: 데이터 수집 모듈
- [ ] **Phase 7**: 팩터 분석 대시보드
- [ ] **Phase 8**: 백테스팅 패널

---

## 🎯 사용 방법

### 1. 블록 탐지

1. **좌측 사이드바**에서 "🔍 블록 탐지" 클릭
2. **Step 1**: 분석 기간 선택 (기본: 2015~2025)
3. **Step 2**: 탐지 조건 체크
   - 1번 블록: 2년래 최대 거래량, 500억 이상
   - 2번 블록: 80% 이상, 6개월 이내, 패턴 매칭
4. **Step 3**: "🔍 탐지 시작" 버튼 클릭
5. 실시간 진행률 확인
6. 결과 테이블에서 케이스 확인

### 2. 키보드 단축키

- `Ctrl+1~6`: 메뉴 이동
- `Ctrl+F`: 검색
- `Ctrl+L`: 레이아웃 모드 전환
- `Ctrl+Shift+T`: 테마 전환 (다크/라이트)

---

## 📝 라이선스

이 프로젝트는 개인 학습/연구 목적으로 개발되었습니다.

---

## 🙏 기술 스택

- **Framework**: PySide6 (Qt for Python)
- **Visualization**: Matplotlib, mplfinance
- **Data**: Pandas, NumPy
- **Data Source**: pykrx, dart-fss
- **ML**: scikit-learn, XGBoost, LightGBM
- **Database**: SQLAlchemy, SQLite

---

## 📞 문의

개발 계획서의 전략을 기반으로 구현된 프로젝트입니다.

**현재 버전**: v0.1.0 (Alpha)
**마지막 업데이트**: 2025-10-08
