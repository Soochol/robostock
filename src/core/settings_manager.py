"""
Settings Manager
블록 탐지 설정 저장/불러오기 관리
"""

import json
from pathlib import Path
from typing import Optional
from core.config import DATA_COLLECTION, BLOCK_CRITERIA


class SettingsManager:
    """블록 탐지 설정 저장/불러오기 관리"""

    def __init__(self, config_path: Path):
        """
        Args:
            config_path: 설정 파일 경로 (JSON)
        """
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> dict:
        """
        설정 불러오기

        Returns:
            설정 dict (없으면 기본값 반환)
        """
        if not self.config_path.exists():
            print(f"[INFO] Settings file not found. Using default settings.")
            return self._get_default_settings()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print(f"[INFO] Settings loaded from {self.config_path}")
            return settings
        except Exception as e:
            print(f"[ERROR] Failed to load settings: {e}")
            print(f"[INFO] Using default settings.")
            return self._get_default_settings()

    def save_settings(self, settings: dict):
        """
        설정 저장

        Args:
            settings: 저장할 설정 dict
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Settings saved to {self.config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save settings: {e}")

    def reset_settings(self) -> dict:
        """
        설정 초기화 (기본값으로 리셋)

        Returns:
            기본 설정 dict
        """
        default_settings = self._get_default_settings()

        # 기본값으로 저장
        self.save_settings(default_settings)
        print(f"[INFO] Settings reset to default values.")

        return default_settings

    def _get_default_settings(self) -> dict:
        """
        기본 설정값

        Returns:
            기본 설정 dict
        """
        return {
            'block1': {
                'max_volume_period': 20,
                'max_volume_ratio': 150,
                'min_trading_value': 100_000_000_000,  # 1000억
                'min_market_cap': 1_000_000_000,  # 10억
                'price_high_enabled': True,
                'price_high_period_months': 3,  # 3개월 신고가
            },
            'block2': {
                'gap_min': 1,
                'gap_max': 10,
                'volume_ratio': 80,
                'min_trading_value': 30_000_000_000,  # 300억
                'pattern_enabled': True,
                'pattern_d1_threshold_pct': 80,
                'pattern_d2_threshold_pct': 80,
                'price_breakthrough_enabled': True,
                'price_breakthrough_pct': 30,  # 1번 블록 고점 대비 30% 이상
            },
            'period': {
                'start_year': DATA_COLLECTION['start_year'],
                'start_month': 1,
                'start_day': 1,
                'end_year': DATA_COLLECTION['end_year'],
                'end_month': 10,
                'end_day': 8,
            }
        }
