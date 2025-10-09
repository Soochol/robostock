"""
Probability Distribution Chart
Level 확률 분포 차트
"""

import pandas as pd
import numpy as np
import re
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from styles.theme import theme_manager


def rgba_to_mpl(rgba_str):
    """
    Convert CSS rgba string to matplotlib-compatible format
    'rgba(255, 255, 255, 0.1)' -> (1.0, 1.0, 1.0, 0.1)
    """
    if not isinstance(rgba_str, str) or not rgba_str.startswith('rgba'):
        return rgba_str

    match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', rgba_str)
    if match:
        r, g, b, a = match.groups()
        return (int(r)/255, int(g)/255, int(b)/255, float(a))
    return rgba_str


class ProbabilityChart(FigureCanvasQTAgg):
    """
    Level 확률 분포 차트

    특징:
    - 수직 바 차트로 각 Level의 예측 확률 표시
    - Level 0-4 색상 구분
    - 최고 확률 Level 강조
    """

    def __init__(self, parent=None, width=4, height=3):
        # Figure 생성
        self.fig = Figure(figsize=(width, height), facecolor='none')
        super().__init__(self.fig)
        self.setParent(parent)

        # 축 생성
        self.ax = self.fig.add_subplot(111)

        # 스타일 설정
        self._setup_style()

    def _setup_style(self):
        """차트 스타일 설정"""
        colors = theme_manager.colors

        # 배경색
        self.ax.set_facecolor(colors['bg_layer_1'])
        self.fig.patch.set_facecolor('none')

        # 축 색상
        self.ax.tick_params(colors=colors['text_secondary'], which='both')
        self.ax.spines['bottom'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['top'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['left'].set_color(rgba_to_mpl(colors['border']))
        self.ax.spines['right'].set_color(rgba_to_mpl(colors['border']))

        # 그리드
        self.ax.grid(True, color=colors['grid'], alpha=0.3, linestyle='--', linewidth=0.5, axis='y')

        # 여백
        self.fig.tight_layout()

    def plot_probabilities(self, probabilities: dict = None):
        """
        Level 확률 분포 그리기

        Args:
            probabilities: Level별 확률 딕셔너리
                          {0: 0.05, 1: 0.15, 2: 0.25, 3: 0.45, 4: 0.10}
        """
        if probabilities is None:
            # 샘플 데이터
            probabilities = {
                0: 0.05,  # Level 0 (실패)
                1: 0.15,  # Level 1 (저수익)
                2: 0.25,  # Level 2 (중수익)
                3: 0.45,  # Level 3 (고수익) - 가장 높음
                4: 0.10   # Level 4 (초고수익)
            }

        # 차트 초기화
        self.ax.clear()
        self._setup_style()

        # 데이터 준비
        levels = list(probabilities.keys())
        probs = [probabilities[level] * 100 for level in levels]  # 퍼센트로 변환

        # Level별 색상
        colors = theme_manager.colors
        level_colors = [
            colors['level_0'],  # Level 0: 빨강
            colors['level_1'],  # Level 1: 핑크
            colors['level_2'],  # Level 2: 녹색
            colors['level_3'],  # Level 3: 파랑
            colors['level_4'],  # Level 4: 보라
        ]

        # 최고 확률 Level 찾기
        max_level = max(probabilities, key=probabilities.get)

        # 바 차트 그리기
        bars = self.ax.bar(
            levels,
            probs,
            color=level_colors,
            alpha=0.8,
            edgecolor='white',
            linewidth=1.5
        )

        # 최고 확률 Level 강조
        bars[max_level].set_alpha(1.0)
        bars[max_level].set_linewidth(2.5)

        # 값 라벨 추가
        for i, (level, prob) in enumerate(zip(levels, probs)):
            self.ax.text(
                level,
                prob + 2,
                f'{prob:.1f}%',
                ha='center',
                va='bottom',
                fontsize=9,
                color=colors['text_primary'],
                fontweight='bold' if level == max_level else 'normal'
            )

        # 축 레이블
        self.ax.set_xlabel('Level', fontsize=10, color=colors['text_secondary'])
        self.ax.set_ylabel('확률 (%)', fontsize=10, color=colors['text_secondary'])

        # x축 레이블
        level_labels = ['L0\n(실패)', 'L1\n(저수익)', 'L2\n(중수익)', 'L3\n(고수익)', 'L4\n(초고수익)']
        self.ax.set_xticks(levels)
        self.ax.set_xticklabels(level_labels, fontsize=8, color=colors['text_secondary'])

        # y축 범위
        self.ax.set_ylim(0, 100)

        # 제목
        self.ax.set_title('수익 Level 확률 분포', fontsize=11, color=colors['text_primary'], pad=10)

        # 캔버스 업데이트
        self.draw()

    def clear_chart(self):
        """차트 초기화"""
        self.ax.clear()
        self._setup_style()
        self.draw()
