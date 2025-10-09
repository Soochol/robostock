"""
Typography System
타이포그래피 설정 (가독성 최우선)
"""

# ===== 폰트 패밀리 =====
FONT_FAMILIES = {
    'primary': (
        '"Pretendard Variable", "Pretendard", "Inter", '
        '-apple-system, sans-serif'
    ),
    'display': '"Poppins", "Pretendard Variable", sans-serif',
    'mono': '"JetBrains Mono", "D2Coding", "Consolas", monospace',
}

# ===== 폰트 크기 (8px 기준 배수) =====
FONT_SIZES = {
    'display_1': 56,   # 큰 숫자 (성공 확률 등) - 54 → 56 (8px grid)
    'display_2': 40,   # 중간 숫자 - 42 → 40 (8px grid)
    'h1': 32,          # 페이지 제목
    'h2': 24,          # 섹션 제목
    'h3': 18,          # 카드 제목
    'body_large': 16,  # 강조 본문
    'body': 15,        # 기본 본문 - 14 → 15 (가독성 향상)
    'body_small': 13,  # 작은 본문
    'caption': 12,     # 캡션
    'small': 11,       # 작은 텍스트
}

# ===== 폰트 무게 =====
FONT_WEIGHTS = {
    'bold': 700,
    'semi_bold': 600,
    'medium': 500,
    'regular': 400,
    'light': 300,
}

# ===== 행간 (Line Height) =====
LINE_HEIGHTS = {
    'tight': 1.2,
    'normal': 1.5,
    'relaxed': 1.75,
    'loose': 2.0,
}

# ===== 자간 (Letter Spacing) =====
LETTER_SPACINGS = {
    'tighter': -0.05,
    'tight': -0.025,
    'normal': 0,
    'wide': 0.025,
    'wider': 0.05,
    'widest': 0.1,
}

# ===== 프리셋 스타일 =====
TYPOGRAPHY_PRESETS = {
    'display_1': {
        'font_family': FONT_FAMILIES['display'],
        'font_size': FONT_SIZES['display_1'],
        'font_weight': FONT_WEIGHTS['bold'],
        'line_height': LINE_HEIGHTS['tight'],
        'letter_spacing': LETTER_SPACINGS['tight'],
    },
    'h1': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['h1'],
        'font_weight': FONT_WEIGHTS['bold'],
        'line_height': LINE_HEIGHTS['tight'],
        'letter_spacing': LETTER_SPACINGS['tight'],
    },
    'h2': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['h2'],
        'font_weight': FONT_WEIGHTS['semi_bold'],
        'line_height': LINE_HEIGHTS['normal'],
        'letter_spacing': LETTER_SPACINGS['normal'],
    },
    'h3': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['h3'],
        'font_weight': FONT_WEIGHTS['semi_bold'],
        'line_height': LINE_HEIGHTS['normal'],
        'letter_spacing': LETTER_SPACINGS['normal'],
    },
    'body': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['body'],
        'font_weight': FONT_WEIGHTS['regular'],
        'line_height': LINE_HEIGHTS['normal'],
        'letter_spacing': LETTER_SPACINGS['normal'],
    },
    'body_bold': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['body'],
        'font_weight': FONT_WEIGHTS['semi_bold'],
        'line_height': LINE_HEIGHTS['normal'],
        'letter_spacing': LETTER_SPACINGS['normal'],
    },
    'caption': {
        'font_family': FONT_FAMILIES['primary'],
        'font_size': FONT_SIZES['caption'],
        'font_weight': FONT_WEIGHTS['regular'],
        'line_height': LINE_HEIGHTS['normal'],
        'letter_spacing': LETTER_SPACINGS['wide'],
    },
    'mono': {
        'font_family': FONT_FAMILIES['mono'],
        'font_size': FONT_SIZES['body_small'],
        'font_weight': FONT_WEIGHTS['regular'],
        'line_height': LINE_HEIGHTS['relaxed'],
        'letter_spacing': LETTER_SPACINGS['normal'],
    },
}


# ===== 유틸리티 함수 =====


def get_font_style(preset: str) -> dict:
    """
    프리셋 이름으로 폰트 스타일 가져오기

    Args:
        preset: 프리셋 이름 ('h1', 'body', 'caption' 등)

    Returns:
        폰트 스타일 딕셔너리
    """
    return TYPOGRAPHY_PRESETS.get(preset, TYPOGRAPHY_PRESETS['body'])


def font_to_qss(preset: str) -> str:
    """
    프리셋을 QSS 스타일로 변환

    Args:
        preset: 프리셋 이름

    Returns:
        QSS font 스타일 문자열

    Example:
        >>> font_to_qss('h1')
        'font-family: "Inter"; font-size: 32px; font-weight: 700;'
    """
    style = get_font_style(preset)
    return f"""
        font-family: {style['font_family']};
        font-size: {style['font_size']}px;
        font-weight: {style['font_weight']};
        line-height: {style['line_height']};
        letter-spacing: {style['letter_spacing']}em;
    """.strip()
