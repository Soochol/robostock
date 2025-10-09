"""
Radar Chart Widget
레이더 차트 위젯 (팩터 스코어 시각화)
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


class RadarChart(FigureCanvasQTAgg):
    """
    레이더 차트 위젯 (팩터 스코어 시각화)

    특징:
    - 5개 팩터 차원 표시 (기술적, 재무, 수급, 산업, 패턴)
    - 점수 범위: 0-100
    - 네온 스타일 디자인
    """

    def __init__(self, parent=None, width=4, height=4):
        # Figure 생성
        self.fig = Figure(figsize=(width, height), facecolor='none')
        super().__init__(self.fig)
        self.setParent(parent)

        # Polar subplot
        self.ax = self.fig.add_subplot(111, projection='polar')

        # 팩터 카테고리
        self.categories = ['기술적', '재무', '수급', '산업', '패턴']
        self.num_vars = len(self.categories)

        # 스타일 설정
        self._setup_style()

    def _setup_style(self):
        """차트 스타일 설정"""
        colors = theme_manager.colors

        # 배경색
        self.ax.set_facecolor(colors['bg_layer_1'])
        self.fig.patch.set_facecolor('none')

        # 레이블 색상
        self.ax.tick_params(colors=colors['text_secondary'])

        # 그리드 색상
        self.ax.grid(True, color=rgba_to_mpl(colors['border']), alpha=0.3, linestyle='--')

        # y축 범위 (0-100)
        self.ax.set_ylim(0, 100)

        # 여백
        self.fig.tight_layout()

    def plot_scores(self, scores: dict = None):
        """
        팩터 스코어 그리기

        Args:
            scores: 팩터별 점수 딕셔너리
                    {'기술적': 75, '재무': 60, '수급': 85, '산업': 70, '패턴': 80}
        """
        if scores is None:
            # 샘플 데이터
            scores = {
                '기술적': 75,
                '재무': 60,
                '수급': 85,
                '산업': 70,
                '패턴': 80
            }

        # 차트 초기화
        self.ax.clear()
        self._setup_style()

        # 점수 배열 생성
        values = [scores.get(cat, 0) for cat in self.categories]

        # 각도 계산 (첫 번째 축을 위쪽으로)
        angles = np.linspace(0, 2 * np.pi, self.num_vars, endpoint=False).tolist()

        # 폐곡선 만들기 (첫 값을 마지막에 추가)
        values += values[:1]
        angles += angles[:1]

        # 레이더 차트 그리기
        colors = theme_manager.colors
        self.ax.plot(
            angles,
            values,
            'o-',
            linewidth=2,
            color=colors['primary'],
            markersize=8,
            markerfacecolor=colors['primary'],
            markeredgecolor='white',
            markeredgewidth=1.5
        )

        # 채우기
        self.ax.fill(
            angles,
            values,
            color=colors['primary'],
            alpha=0.25
        )

        # 카테고리 레이블
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(self.categories, size=10, color=colors['text_primary'])

        # y축 레이블 (점수)
        self.ax.set_yticks([20, 40, 60, 80, 100])
        self.ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color=colors['text_secondary'])

        # 제목
        self.ax.set_title('팩터 스코어', size=12, color=colors['text_primary'], pad=20)

        # 그리드 스타일
        self.ax.spines['polar'].set_color(rgba_to_mpl(colors['border']))

        # 캔버스 업데이트
        self.draw()

    def clear_chart(self):
        """차트 초기화"""
        self.ax.clear()
        self._setup_style()
        self.draw()
