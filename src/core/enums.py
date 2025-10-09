"""
Enums - 타입 안전성을 위한 Enum 정의
"""

from enum import Enum, auto

class BlockType(Enum):
    """거래량 블록 타입"""
    BLOCK_1 = 1  # 1번 거래량 블록 (트렌드 변화 시작)
    BLOCK_2 = 2  # 2번 거래량 블록 (트렌드 확인)
    BLOCK_3 = 3  # 3번 거래량 블록 (추가 자금 유입)
    BLOCK_4 = 4  # 4번 거래량 블록 (반복 자금 유입)

class MarketType(Enum):
    """시장 구분"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"

class ReturnLevel(Enum):
    """수익률 Level 분류"""
    LEVEL_0 = 0  # 실패 (50% 미만)
    LEVEL_1 = 1  # 저수익 (50~100%)
    LEVEL_2 = 2  # 중수익 (100~300%)
    LEVEL_3 = 3  # 고수익 (300~1000%)
    LEVEL_4 = 4  # 초고수익 (1000% 이상)

class FactorType(Enum):
    """팩터 분석 타입"""
    TECHNICAL = "technical"    # 기술적 분석
    FINANCIAL = "financial"    # 재무 분석
    SUPPLY = "supply"          # 수급 분석
    INDUSTRY = "industry"      # 산업 분석

class PanelType(Enum):
    """패널 타입 (사이드바 메뉴)"""
    DATA_COLLECTION = auto()  # 데이터 수집
    BLOCK_DETECTOR = auto()   # 블록 탐지
    CHART_VIEWER = auto()     # 차트 뷰어
    CASE_MANAGER = auto()     # 케이스 관리
    FACTOR_ANALYSIS = auto()  # 팩터 분석
    PATTERN_LEARNING = auto() # 패턴 학습
    BACKTESTING = auto()      # 백테스팅
    SETTINGS = auto()         # 설정

class NewHighGrade(Enum):
    """신고가 등급"""
    S = "S"  # 역사적 신고가
    A = "A"  # 10년래 신고가
    B = "B"  # 5년래 신고가
    C = "C"  # 2년래 신고가
    D = "D"  # 1년래 신고가
    E = "E"  # 6개월래 신고가
    F = "F"  # 해당없음

class PatternType(Enum):
    """2번 블록 패턴 타입"""
    D_ONLY = "D"
    D_D1 = "D+D+1"
    D_D2 = "D+D+2"
    D_D1_D2 = "D+D+1+D+2"

class ThemeMode(Enum):
    """테마 모드"""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"  # 시스템 설정 따라가기

class LayoutMode(Enum):
    """레이아웃 모드"""
    STANDARD = "standard"  # 기본 3-zone
    FOCUS = "focus"        # 차트 집중 모드
    ANALYSIS = "analysis"  # 분석 집중 모드

class NotificationType(Enum):
    """알림 타입"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
