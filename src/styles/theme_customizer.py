"""
Theme Customizer
사용자 커스텀 테마 설정

Features:
- 색상 커스터마이징 (Primary, Accent)
- 테마 프리셋 (기본, 보라, 그린, 오렌지 등)
- 설정 저장/불러오기
- 실시간 미리보기
"""

import json
from pathlib import Path
from typing import Dict, Any

from PySide6.QtCore import QObject, Signal

from styles.colors import DARK_COLORS, LIGHT_COLORS, GRADIENTS
from core.enums import ThemeMode


class ThemeCustomizer(QObject):
    """
    테마 커스터마이저

    Features:
    - 색상 오버라이드
    - 프리셋 관리
    - 설정 저장
    """

    theme_customized = Signal(dict)  # 커스텀 색상 변경 시

    # 테마 프리셋
    PRESETS = {
        'default': {
            'name': 'Default Blue',
            'primary': '#4F8FFF',
            'accent': '#FF6B35',
            'description': '기본 블루 + 오렌지 (Option B)',
        },
        'purple': {
            'name': 'Purple Dream',
            'primary': '#A78BFA',
            'accent': '#EC4899',
            'description': '보라 + 핑크',
        },
        'green': {
            'name': 'Nature Green',
            'primary': '#10B981',
            'accent': '#F59E0B',
            'description': '그린 + 앰버',
        },
        'orange': {
            'name': 'Sunset Orange',
            'primary': '#F97316',
            'accent': '#EF4444',
            'description': '오렌지 + 레드',
        },
        'cyan': {
            'name': 'Ocean Cyan',
            'primary': '#06B6D4',
            'accent': '#8B5CF6',
            'description': '시안 + 바이올렛',
        },
        'rose': {
            'name': 'Rose Pink',
            'primary': '#F43F5E',
            'accent': '#FB923C',
            'description': '로즈 + 오렌지',
        },
    }

    def __init__(self):
        super().__init__()

        self._custom_colors = {}
        self._current_preset = 'default'
        self._config_file = Path('data/theme_config.json')

    def apply_preset(self, preset_name: str):
        """
        프리셋 적용

        Args:
            preset_name: 프리셋 이름
        """
        if preset_name not in self.PRESETS:
            return

        preset = self.PRESETS[preset_name]
        self._current_preset = preset_name

        # Primary와 Accent 색상 변경
        self.set_color('primary', preset['primary'])
        self.set_color('accent', preset['accent'])

        self.theme_customized.emit(self._custom_colors)

    def set_color(self, color_key: str, color_value: str):
        """
        개별 색상 설정

        Args:
            color_key: 색상 키 (예: 'primary', 'accent')
            color_value: HEX 색상값 (예: '#4F8FFF')
        """
        self._custom_colors[color_key] = color_value

        # 관련 색상도 자동 생성
        if color_key == 'primary':
            self._generate_primary_variants(color_value)
        elif color_key == 'accent':
            self._generate_accent_variants(color_value)

        self.theme_customized.emit(self._custom_colors)

    def _generate_primary_variants(self, base_color: str):
        """
        Primary 변형 색상 자동 생성 (hover, pressed 등)

        Args:
            base_color: 기본 색상 HEX
        """
        # 간단한 어둡게/밝게 처리 (실제로는 더 정교한 알고리즘 필요)
        r, g, b = self._hex_to_rgb(base_color)

        # Hover: 약간 어둡게 (-10%)
        hover_r = max(0, int(r * 0.9))
        hover_g = max(0, int(g * 0.9))
        hover_b = max(0, int(b * 0.9))
        self._custom_colors['primary_hover'] = self._rgb_to_hex(hover_r, hover_g, hover_b)

        # Pressed: 더 어둡게 (-20%)
        pressed_r = max(0, int(r * 0.8))
        pressed_g = max(0, int(g * 0.8))
        pressed_b = max(0, int(b * 0.8))
        self._custom_colors['primary_pressed'] = self._rgb_to_hex(pressed_r, pressed_g, pressed_b)

        # Subtle: 투명도 적용
        self._custom_colors['primary_subtle'] = f'rgba({r}, {g}, {b}, 0.12)'

        # Container: 어둡게
        container_r = max(0, int(r * 0.3))
        container_g = max(0, int(g * 0.3))
        container_b = max(0, int(b * 0.3))
        self._custom_colors['primary_container'] = self._rgb_to_hex(container_r, container_g, container_b)

    def _generate_accent_variants(self, base_color: str):
        """Accent 변형 색상 자동 생성"""
        r, g, b = self._hex_to_rgb(base_color)

        # Hover
        hover_r = max(0, int(r * 0.9))
        hover_g = max(0, int(g * 0.9))
        hover_b = max(0, int(b * 0.9))
        self._custom_colors['accent_hover'] = self._rgb_to_hex(hover_r, hover_g, hover_b)

        # Pressed
        pressed_r = max(0, int(r * 0.8))
        pressed_g = max(0, int(g * 0.8))
        pressed_b = max(0, int(b * 0.8))
        self._custom_colors['accent_pressed'] = self._rgb_to_hex(pressed_r, pressed_g, pressed_b)

        # Subtle
        self._custom_colors['accent_subtle'] = f'rgba({r}, {g}, {b}, 0.15)'

        # Container
        container_r = max(0, int(r * 0.3))
        container_g = max(0, int(g * 0.3))
        container_b = max(0, int(b * 0.3))
        self._custom_colors['accent_container'] = self._rgb_to_hex(container_r, container_g, container_b)

    def get_custom_colors(self, mode: ThemeMode = ThemeMode.DARK) -> Dict[str, str]:
        """
        커스텀 색상 가져오기

        Args:
            mode: 테마 모드

        Returns:
            커스텀 색상 딕셔너리 (기본 색상 + 오버라이드)
        """
        base_colors = DARK_COLORS if mode == ThemeMode.DARK else LIGHT_COLORS

        # 기본 색상에 커스텀 색상 오버라이드
        result = base_colors.copy()
        result.update(self._custom_colors)

        return result

    def save_config(self):
        """설정 파일로 저장"""
        config = {
            'preset': self._current_preset,
            'custom_colors': self._custom_colors,
        }

        self._config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def load_config(self):
        """설정 파일에서 불러오기"""
        if not self._config_file.exists():
            return

        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self._current_preset = config.get('preset', 'default')
            self._custom_colors = config.get('custom_colors', {})

            self.theme_customized.emit(self._custom_colors)

        except Exception as e:
            print(f"[ERROR] Failed to load theme config: {e}")

    def reset_to_default(self):
        """기본 테마로 리셋"""
        self._custom_colors = {}
        self._current_preset = 'default'
        self.theme_customized.emit(self._custom_colors)

    def get_current_preset(self) -> str:
        """현재 프리셋 이름"""
        return self._current_preset

    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """프리셋 정보 가져오기"""
        return self.PRESETS.get(preset_name, self.PRESETS['default'])

    # === 유틸리티 함수 ===

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """HEX를 RGB로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _rgb_to_hex(r: int, g: int, b: int) -> str:
        """RGB를 HEX로 변환"""
        return f'#{r:02x}{g:02x}{b:02x}'

    @staticmethod
    def lighten_color(hex_color: str, factor: float = 0.2) -> str:
        """
        색상 밝게 하기

        Args:
            hex_color: HEX 색상
            factor: 밝기 증가 (0.0 ~ 1.0)

        Returns:
            밝아진 HEX 색상
        """
        r, g, b = ThemeCustomizer._hex_to_rgb(hex_color)

        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return ThemeCustomizer._rgb_to_hex(r, g, b)

    @staticmethod
    def darken_color(hex_color: str, factor: float = 0.2) -> str:
        """
        색상 어둡게 하기

        Args:
            hex_color: HEX 색상
            factor: 어둡기 증가 (0.0 ~ 1.0)

        Returns:
            어두워진 HEX 색상
        """
        r, g, b = ThemeCustomizer._hex_to_rgb(hex_color)

        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return ThemeCustomizer._rgb_to_hex(r, g, b)


# 싱글톤 인스턴스
theme_customizer = ThemeCustomizer()
