"""
Global Configuration
전역 설정 관리 - 단일 진실 공급원 (Single Source of Truth)
"""

from pathlib import Path
from .enums import ThemeMode, LayoutMode

# ===== 경로 설정 =====
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "robostock.db"
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
FONTS_DIR = RESOURCES_DIR / "fonts"

# 디렉토리 자동 생성
for directory in [DATA_DIR, LOG_DIR, RESOURCES_DIR, ICONS_DIR, FONTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ===== 앱 설정 =====
APP_CONFIG = {
    'name': 'RoboStock',
    'version': '1.0.0',
    'organization': 'RoboStock',
    'description': '거래량 블록 기반 장기투자 분석 플랫폼',
}

# ===== 데이터 수집 설정 =====
DATA_COLLECTION = {
    'start_year': 2015,
    'end_year': 2025,
    'markets': ['KOSPI', 'KOSDAQ'],
    'api_delay': 0.2,  # API 호출 간격 (초)
    'batch_size': 100,  # 배치 크기
}

# ===== 블록 탐지 기준 =====
BLOCK_CRITERIA = {
    'block_1': {
        # 최소 거래대금: 500억원 (트렌드 변화 시작의 유의미한 자금 유입)
        'min_trading_value': 50_000_000_000,
        # 최대 거래량 조회 기간: 730일 (2년, 신고가 여부 판단)
        'max_volume_period_days': 730,
    },
    'block_2': {
        # 거래량 비율: 1번 블록 대비 최소 80% (트렌드 확인)
        'volume_ratio_min': 0.8,
        # 1번 블록으로부터 최대 간격: 180일 (6개월, 패턴 유효성)
        'max_days_from_block1': 180,
        # 고거래대금 기준: 2000억원 (대형주 판단 기준)
        'high_trading_value': 200_000_000_000,
        # 패턴 매칭 일수: 3일 (D, D+1, D+2 패턴 분석)
        'pattern_match_days': 3,
    },
    'block_3': {
        # 거래량 비율: 2번 블록 최대 대비 최소 15% (추가 자금 유입 확인)
        'volume_ratio_min': 0.15,
        # 가격 범위: ±12% (횡보/조정 구간 판단)
        'price_range_pct': 0.12,
        # 2번 블록으로부터 최대 간격: 180일 (6개월, 패턴 유효성)
        'max_days_from_block2': 180,
    },
    # 이동평균 기간: 60일 (중기 추세 판단)
    'ma_period': 60,
}

# ===== UI 레이아웃 설정 =====
UI_CONFIG = {
    'window': {
        'default_size': (1920, 1080),
        'min_size': (1280, 720),
        'title': 'RoboStock - 거래량 블록 기반 장기투자 분석 플랫폼',
    },

    'layout_modes': {
        LayoutMode.STANDARD: {  # 기본 3-zone
            'sidebar_width': 180,
            'analysis_panel_width': 380,
            'sidebar_collapsed_width': 60,
        },
        LayoutMode.FOCUS: {  # 차트 집중 모드
            'sidebar_width': 60,
            'analysis_panel_width': 0,  # 숨김
            'sidebar_collapsed_width': 60,
        },
        LayoutMode.ANALYSIS: {  # 분석 집중 모드
            'sidebar_width': 180,
            'analysis_panel_width': 500,
            'sidebar_collapsed_width': 60,
        },
    },

    'header_height': 60,
    'statusbar_height': 30,

    'default_theme': ThemeMode.DARK,
    'default_layout': LayoutMode.STANDARD,
}

# ===== 간격 시스템 (8px Grid) =====
SPACING = {
    'xs': 4,    # 0.25rem
    'sm': 8,    # 0.5rem
    'md': 16,   # 1rem
    'lg': 24,   # 1.5rem
    'xl': 32,   # 2rem
    '2xl': 48,  # 3rem
    '3xl': 64,  # 4rem
}

# ===== 그림자 시스템 =====
SHADOWS = {
    'none': 'none',
    'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

    # Glassmorphism 효과
    'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',

    # 네온 글로우
    'glow_blue': '0 0 20px rgba(59, 130, 246, 0.5)',
    'glow_green': '0 0 20px rgba(16, 185, 129, 0.5)',
    'glow_red': '0 0 20px rgba(239, 68, 68, 0.5)',
    'glow_pink': '0 0 20px rgba(255, 0, 128, 0.5)',
}

# ===== 애니메이션 설정 =====
ANIMATIONS = {
    'duration': {
        'instant': 0,
        'fast': 150,
        'base': 250,
        'slow': 350,
        'slower': 500,
    },

    'easing': {
        'ease_in_out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'ease_out': 'cubic-bezier(0, 0, 0.2, 1)',
        'ease_in': 'cubic-bezier(0.4, 0, 1, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
}

# ===== 차트 설정 =====
CHART_CONFIG = {
    'default_period': '1Y',  # 1년
    'candle_up_color': '#26A69A',
    'candle_down_color': '#EF5350',
    'volume_color_up': '#26A69A',
    'volume_color_down': '#EF5350',
    'ma_60_color': '#FFA726',
    'grid_color': '#3E3E42',
    'background_color': 'transparent',
}

# ===== 테이블 설정 =====
TABLE_CONFIG = {
    'row_height': 40,
    'header_height': 48,
    'rows_per_page': 20,
    'alternating_row_colors': True,
}

# ===== 알림 설정 =====
NOTIFICATION_CONFIG = {
    'duration': 3000,  # 3초
    'position': 'bottom_right',  # 우하단
    'max_notifications': 3,  # 최대 동시 표시 개수
}

# ===== 검색 설정 =====
SEARCH_CONFIG = {
    'min_query_length': 2,
    'max_results': 10,
    'fuzzy_threshold': 0.6,  # 퍼지 매칭 임계값
    'recent_searches_count': 5,
}

# ===== 키보드 단축키 =====
SHORTCUTS = {
    # 네비게이션
    'data_collection': 'Ctrl+1',
    'block_detector': 'Ctrl+2',
    'case_manager': 'Ctrl+3',
    'factor_analysis': 'Ctrl+4',
    'pattern_learning': 'Ctrl+5',
    'backtesting': 'Ctrl+6',

    # 액션
    'search': 'Ctrl+F',
    'save': 'Ctrl+S',
    'export': 'Ctrl+E',
    'refresh': 'F5',

    # 차트
    'chart_home': 'H',
    'chart_zoom': 'Z',
    'chart_pan': 'P',
    'chart_block_center': 'B',
    'chart_pause': 'Space',

    # 레이아웃
    'toggle_layout': 'Ctrl+L',
    'toggle_sidebar': 'Ctrl+B',
    'toggle_analysis_panel': 'Ctrl+\\',

    # 테마
    'toggle_theme': 'Ctrl+Shift+T',
}

# ===== 아이콘 매핑 (SVG 키) =====
# 실제 아이콘은 resources.icons.IconManager에서 관리
ICONS = {
    # 메뉴 (Lucide Icons)
    'data_collection': 'download',
    'block_detector': 'search',
    'case_manager': 'folder',
    'factor_analysis': 'microscope',
    'pattern_learning': 'brain',
    'backtesting': 'zap',
    'settings': 'settings',
    'chart_viewer': 'bar-chart',

    # 블록 타입 (커스텀 네온 아이콘)
    'block_1': 'block_1',  # 네온 핑크
    'block_2': 'block_2',  # 네온 그린
    'block_3': 'block_3',  # 네온 사이언
    'block_4': 'block_4',  # 네온 골드

    # Level (메달/트로피 아이콘)
    'level_4': 'trophy',    # 🏆
    'level_3': 'medal',     # 🥇
    'level_2': 'medal',     # 🥈
    'level_1': 'medal',     # 🥉
    'level_0': 'x-circle',  # ❌

    # 팩터 (분석 관련 아이콘)
    'technical': 'activity',      # 기술적 분석
    'financial': 'trending-up',   # 재무 분석
    'supply': 'layers',           # 수급 분석
    'industry': 'bar-chart',      # 산업 분석

    # 공통 액션
    'search': 'search',
    'filter': 'filter',
    'favorite': 'check-circle',
    'notification': 'bell',
    'user': 'user',
    'download': 'download',
    'upload': 'upload',
    'delete': 'trash',
    'save': 'save',
    'map_pin': 'map-pin',
    'target': 'target',

    # 상태 표시
    'success': 'check-circle',
    'warning': 'alert-triangle',
    'error': 'alert-circle',
    'info': 'info',
}

# ===== 로깅 설정 =====
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file': LOG_DIR / 'robostock.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# ===== 콜렉션 로그 설정 =====
COLLECTION_LOG_CONFIG = {
    'style': 'compact',  # 'compact', 'detailed', 'simple'
    'use_colors': True,  # 색상 사용 여부
    'show_progress_bar': True,  # 프로그레스 바 표시
    'summary_interval': 50,  # 요약 출력 간격 (몇 개마다)
    'show_speed': True,  # 속도 표시 (records/sec)
    'show_eta': True,  # 남은 시간 표시
}
