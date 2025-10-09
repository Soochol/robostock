"""
Color System - Modern Glassmorphism 2.0
프리미엄 모던 트레이딩 플랫폼 컬러 팔레트 (2024-2025 Design Trends)

주요 개선사항:
- Accent 컬러 추가 (#FF6B35 - 브랜드 아이덴티티)
- Primary 색상 조정 (#4F8FFF - 더 생동감 있는 블루)
- 텍스트 대비 강화 (WCAG AA 준수)
- 블록 색상 채도 조정 (-10%)
- Depth System (bg_base, bg_elevated 추가)
- Material Design 3 영감
"""

# ===== 다크 모드 (기본) =====
DARK_COLORS = {
    # ===== 배경 (Layered Depth System) =====
    'bg_base': '#0A0D14',          # 최심층 (더 깊은 다크)
    'bg_layer_1': '#0F1419',       # 최하층 (body)
    'bg_layer_2': '#1A1F2E',       # 중간층 (패널)
    'bg_layer_3': '#242938',       # 상층 (카드) - 약간 조정
    'bg_elevated': '#2A3040',      # 떠오른 요소 (모달, 툴팁)

    # ===== Surface (Glassmorphism 2.0) =====
    'surface_glass': 'rgba(42, 48, 64, 0.6)',           # 기본 유리
    'surface_glass_hover': 'rgba(42, 48, 64, 0.8)',     # 호버 시
    'surface_frosted': 'rgba(37, 42, 58, 0.85)',        # 더 불투명한 유리
    'bg_glass': 'rgba(42, 48, 64, 0.6)',                # 호환성 유지
    'bg_glass_hover': 'rgba(42, 48, 64, 0.8)',

    # ===== 텍스트 (WCAG AA 준수) =====
    'text_primary': '#FFFFFF',
    'text_secondary': '#A0AEC0',
    'text_tertiary': '#8B96AB',    # 개선: #718096 → #8B96AB (대비비 4.6:1)
    'text_disabled': '#4A5568',

    # ===== Primary (Dynamic Blue - Material Design 3 영감) =====
    'primary': '#4F8FFF',          # 개선: #3B82F6 → #4F8FFF (더 생동감)
    'primary_hover': '#3B7EF0',    # 개선: 새로운 호버 색상
    'primary_pressed': '#2563EB',  # 유지
    'primary_container': '#1E3A5F',  # NEW: MD3 Container 개념
    'primary_subtle': 'rgba(79, 143, 255, 0.12)',  # 개선: opacity 증가
    'on_primary': '#FFFFFF',       # NEW: primary 위의 텍스트

    # ===== Accent (시그니처 컬러 - 브랜드 아이덴티티) =====
    'accent': '#FF6B35',           # NEW: 따뜻한 오렌지
    'accent_hover': '#FF5520',     # NEW: 호버
    'accent_pressed': '#E64A1A',   # NEW: 눌림
    'accent_subtle': 'rgba(255, 107, 53, 0.15)',  # NEW: 미묘한 배경
    'accent_container': '#4A2617',  # NEW: accent container
    'on_accent': '#FFFFFF',        # NEW: accent 위의 텍스트

    # ===== 성공 (그린 시리즈) =====
    'success': '#10B981',
    'success_hover': '#059669',
    'success_pressed': '#047857',  # NEW
    'success_subtle': 'rgba(16, 185, 129, 0.12)',

    # ===== 경고 (옐로우 시리즈) =====
    'warning': '#F59E0B',
    'warning_hover': '#D97706',
    'warning_pressed': '#B45309',  # NEW
    'warning_subtle': 'rgba(245, 158, 11, 0.12)',

    # ===== 에러 (레드 시리즈) =====
    'error': '#EF4444',
    'error_hover': '#DC2626',
    'error_pressed': '#B91C1C',    # NEW
    'error_subtle': 'rgba(239, 68, 68, 0.12)',

    # ===== 정보 (사이언 시리즈) =====
    'info': '#06B6D4',
    'info_hover': '#0891B2',
    'info_pressed': '#0E7490',     # NEW
    'info_subtle': 'rgba(6, 182, 212, 0.12)',

    # ===== 거래량 블록 색상 (채도 조정 -10%) =====
    'block_1': '#FF2D92',          # 개선: #FF0080 → #FF2D92 (핑크, 채도 감소)
    'block_1_glow': 'rgba(255, 45, 146, 0.4)',  # 개선: opacity 감소
    'block_2': '#00E57D',          # 개선: #00FF88 → #00E57D (그린, 약간 따뜻하게)
    'block_2_glow': 'rgba(0, 229, 125, 0.4)',
    'block_3': '#00C4FF',          # 개선: #00D4FF → #00C4FF (사이언, 약간 차분)
    'block_3_glow': 'rgba(0, 196, 255, 0.4)',
    'block_4': '#FFB700',          # 개선: #FFD700 → #FFB700 (골드, 약간 차분)
    'block_4_glow': 'rgba(255, 183, 0, 0.4)',

    # ===== Level 색상 =====
    'level_4': '#FFD700',          # 금색 (초고수익)
    'level_3': '#667eea',          # 파란색 (고수익)
    'level_2': '#38ef7d',          # 녹색 (중수익)
    'level_1': '#fa709a',          # 핑크 (저수익)
    'level_0': '#eb3349',          # 빨강 (실패)

    # ===== 캔들 색상 =====
    'candle_up': '#26A69A',        # 상승 (틸)
    'candle_down': '#EF5350',      # 하락 (레드)

    # ===== UI 요소 =====
    'border': 'rgba(255, 255, 255, 0.12)',      # 개선: 0.1 → 0.12
    'border_hover': 'rgba(255, 255, 255, 0.2)',
    'border_focus': 'rgba(79, 143, 255, 0.5)',  # primary 색상 반영
    'border_subtle': 'rgba(255, 255, 255, 0.06)',  # NEW: 매우 미묘한 경계

    'divider': 'rgba(255, 255, 255, 0.08)',

    'overlay': 'rgba(0, 0, 0, 0.5)',
    'backdrop': 'rgba(0, 0, 0, 0.7)',

    # ===== 상태 배경 =====
    'hover_bg': 'rgba(255, 255, 255, 0.05)',    # NEW: 호버 배경
    'active_bg': 'rgba(255, 255, 255, 0.08)',   # NEW: 활성 배경
    'selected_bg': 'rgba(79, 143, 255, 0.15)',  # NEW: 선택 배경

    # ===== 차트 =====
    'grid': '#3E3E42',
    'axis': '#A0AEC0',
    'ma_60': '#FFA726',            # 60일 이평선 (주황)
    'support_line': 'rgba(255, 255, 255, 0.3)',  # 지지선
}

# ===== 라이트 모드 =====
LIGHT_COLORS = {
    # ===== 배경 =====
    'bg_base': '#F0F4F8',          # 개선: 약간 더 밝게
    'bg_layer_1': '#F7FAFC',
    'bg_layer_2': '#FFFFFF',
    'bg_layer_3': '#EDF2F7',
    'bg_elevated': '#FFFFFF',

    # ===== Surface =====
    'surface_glass': 'rgba(255, 255, 255, 0.7)',
    'surface_glass_hover': 'rgba(255, 255, 255, 0.9)',
    'surface_frosted': 'rgba(255, 255, 255, 0.95)',
    'bg_glass': 'rgba(255, 255, 255, 0.7)',
    'bg_glass_hover': 'rgba(255, 255, 255, 0.9)',

    # ===== 텍스트 (WCAG AA 준수 - Light Mode) =====
    'text_primary': '#1A202C',     # 대비비 15:1
    'text_secondary': '#4A5568',   # 대비비 8:1
    'text_tertiary': '#5A6472',    # ✅ 개선: 대비비 7:1 (더 어둡게)
    'text_disabled': '#A0AEC0',    # ✅ 개선: 더 밝게 (비활성 표시)

    # ===== Primary =====
    'primary': '#4F8FFF',
    'primary_hover': '#3B7EF0',
    'primary_pressed': '#2563EB',
    'primary_container': '#E0EBFF',
    'primary_subtle': 'rgba(79, 143, 255, 0.12)',
    'on_primary': '#FFFFFF',

    # ===== Accent =====
    'accent': '#FF6B35',
    'accent_hover': '#FF5520',
    'accent_pressed': '#E64A1A',
    'accent_subtle': 'rgba(255, 107, 53, 0.12)',
    'accent_container': '#FFE8DE',
    'on_accent': '#FFFFFF',

    # ===== 성공 =====
    'success': '#10B981',
    'success_hover': '#059669',
    'success_pressed': '#047857',
    'success_subtle': 'rgba(16, 185, 129, 0.12)',

    # ===== 경고 =====
    'warning': '#F59E0B',
    'warning_hover': '#D97706',
    'warning_pressed': '#B45309',
    'warning_subtle': 'rgba(245, 158, 11, 0.12)',

    # ===== 에러 =====
    'error': '#EF4444',
    'error_hover': '#DC2626',
    'error_pressed': '#B91C1C',
    'error_subtle': 'rgba(239, 68, 68, 0.12)',

    # ===== 정보 =====
    'info': '#06B6D4',
    'info_hover': '#0891B2',
    'info_pressed': '#0E7490',
    'info_subtle': 'rgba(6, 182, 212, 0.12)',

    # ===== 블록 색상 (라이트 모드에서는 덜 선명하게) =====
    'block_1': '#FF0080',
    'block_1_glow': 'rgba(255, 0, 128, 0.25)',
    'block_2': '#00CC70',
    'block_2_glow': 'rgba(0, 204, 112, 0.25)',
    'block_3': '#00A8CC',
    'block_3_glow': 'rgba(0, 168, 204, 0.25)',
    'block_4': '#FFAA00',
    'block_4_glow': 'rgba(255, 170, 0, 0.25)',

    # ===== Level 색상 =====
    'level_4': '#F59E0B',
    'level_3': '#4F8FFF',          # primary 반영
    'level_2': '#10B981',
    'level_1': '#EC4899',
    'level_0': '#EF4444',

    # ===== 캔들 색상 =====
    'candle_up': '#10B981',
    'candle_down': '#EF4444',

    # ===== UI 요소 =====
    'border': 'rgba(0, 0, 0, 0.12)',
    'border_hover': 'rgba(0, 0, 0, 0.2)',
    'border_focus': 'rgba(79, 143, 255, 0.5)',
    'border_subtle': 'rgba(0, 0, 0, 0.06)',

    'divider': 'rgba(0, 0, 0, 0.08)',

    'overlay': 'rgba(0, 0, 0, 0.3)',
    'backdrop': 'rgba(0, 0, 0, 0.5)',

    # ===== 상태 배경 =====
    'hover_bg': 'rgba(0, 0, 0, 0.04)',
    'active_bg': 'rgba(0, 0, 0, 0.08)',
    'selected_bg': 'rgba(79, 143, 255, 0.12)',

    # ===== 차트 =====
    'grid': '#E5E7EB',
    'axis': '#6B7280',
    'ma_60': '#F97316',
    'support_line': 'rgba(0, 0, 0, 0.2)',
}

# ===== 그라데이션 시스템 (확장) =====
GRADIENTS = {
    # === Smooth Gradients (135도 각도로 통일 - 2024 트렌드) ===
    'primary': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #4F8FFF, stop:0.5 #3B7EF0, stop:1 #2563EB)'
    ),
    'accent': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #FF6B35, stop:1 #FF5520)'
    ),
    'primary_hover': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #3B7EF0, stop:0.5 #2563EB, stop:1 #1E40AF)'
    ),
    'accent_hover': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #FF5520, stop:1 #E64A1A)'
    ),
    'success': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #10B981, stop:1 #059669)'
    ),
    'error': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #EF4444, stop:1 #DC2626)'
    ),

    # === Level Gradients (3색 그라데이션으로 확장) ===
    'level_4': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #FFD700, stop:0.5 #FFA500, stop:1 #FF6B35)'
    ),
    'level_3': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #667eea, stop:0.5 #764ba2, stop:1 #5B3A8C)'
    ),
    'level_2': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #38ef7d, stop:1 #11998e)'
    ),
    'level_1': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #fa709a, stop:1 #fee140)'
    ),
    'level_0': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 #eb3349, stop:1 #f45c43)'
    ),

    # === Ambient Gradients (배경용 - Radial) ===
    # Note: Qt는 radial gradient를 QRadialGradient로 별도 처리 필요
    'ambient_blue': (
        'radial-gradient(ellipse at top left, '
        'rgba(79, 143, 255, 0.08) 0%, transparent 50%)'
    ),
    'ambient_orange': (
        'radial-gradient(ellipse at bottom right, '
        'rgba(255, 107, 53, 0.06) 0%, transparent 50%)'
    ),

    # === Glass Background Gradients ===
    'glass_surface': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:1, '
        'stop:0 rgba(42, 48, 64, 0.6), stop:1 rgba(37, 42, 58, 0.7))'
    ),

    # === 헤더 그라데이션 (투명) ===
    'header': (
        'qlineargradient(x1:0, y1:0, x2:0, y2:1, '
        'stop:0 rgba(26, 31, 46, 0.95), stop:1 rgba(26, 31, 46, 0.7))'
    ),

    # === Progress Bar 그라데이션 (3색 애니메이션용) ===
    'progress_animated': (
        'qlineargradient(x1:0, y1:0, x2:1, y2:0, '
        'stop:0 #4F8FFF, stop:0.5 #FF6B35, stop:1 #10B981)'
    ),
}


# ===== 유틸리티 함수 =====
def get_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """
    HEX 색상을 RGBA로 변환

    Args:
        hex_color: "#RRGGBB" 형식
        alpha: 투명도 (0.0 ~ 1.0)

    Returns:
        "rgba(r, g, b, a)" 형식
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def get_level_color(level: int, mode: str = 'dark') -> str:
    """Level에 따른 색상 반환"""
    colors = DARK_COLORS if mode == 'dark' else LIGHT_COLORS
    level_map = {
        4: colors['level_4'],
        3: colors['level_3'],
        2: colors['level_2'],
        1: colors['level_1'],
        0: colors['level_0'],
    }
    return level_map.get(level, colors['text_secondary'])


def get_block_color(block_type: int, mode: str = 'dark') -> str:
    """블록 타입에 따른 색상 반환"""
    colors = DARK_COLORS if mode == 'dark' else LIGHT_COLORS
    block_map = {
        1: colors['block_1'],
        2: colors['block_2'],
        3: colors['block_3'],
        4: colors['block_4'],
    }
    return block_map.get(block_type, colors['text_secondary'])


def get_block_glow(block_type: int, mode: str = 'dark') -> str:
    """블록 타입에 따른 glow 색상 반환 (NEW)"""
    colors = DARK_COLORS if mode == 'dark' else LIGHT_COLORS
    glow_map = {
        1: colors['block_1_glow'],
        2: colors['block_2_glow'],
        3: colors['block_3_glow'],
        4: colors['block_4_glow'],
    }
    return glow_map.get(block_type, 'transparent')


# ===== 색상 변환 헬퍼 (NEW) =====
def hex_to_rgb(hex_color: str) -> tuple:
    """HEX를 RGB 튜플로 변환"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """RGB를 HEX로 변환"""
    return f"#{r:02x}{g:02x}{b:02x}"
