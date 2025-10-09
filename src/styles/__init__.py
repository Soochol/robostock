"""
Styles Package
디자인 시스템: 색상, 타이포그래피, 테마
"""

from .colors import (
    DARK_COLORS,
    LIGHT_COLORS,
    GRADIENTS,
    get_rgba,
    get_level_color,
    get_block_color,
)

from .typography import (
    FONT_FAMILIES,
    FONT_SIZES,
    FONT_WEIGHTS,
    LINE_HEIGHTS,
    LETTER_SPACINGS,
    TYPOGRAPHY_PRESETS,
    get_font_style,
    font_to_qss,
)

__all__ = [
    # Colors
    'DARK_COLORS',
    'LIGHT_COLORS',
    'GRADIENTS',
    'get_rgba',
    'get_level_color',
    'get_block_color',
    # Typography
    'FONT_FAMILIES',
    'FONT_SIZES',
    'FONT_WEIGHTS',
    'LINE_HEIGHTS',
    'LETTER_SPACINGS',
    'TYPOGRAPHY_PRESETS',
    'get_font_style',
    'font_to_qss',
]
