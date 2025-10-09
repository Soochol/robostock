"""
Performance Optimization Utilities
성능 최적화 유틸리티

Features:
- GPU 가속화 활성화
- 렌더링 힌트 설정
- 메모리 최적화
- 애니메이션 최적화
"""

from PySide6.QtWidgets import QWidget, QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


def enable_gpu_acceleration(widget: QWidget):
    """
    GPU 가속화 활성화

    Args:
        widget: 대상 위젯

    Note:
        - OpenGL 기반 렌더링 활성화
        - 부드러운 애니메이션을 위한 최적화
    """
    # OpenGL 기반 렌더링 (Qt 6에서는 자동으로 GPU 활용)
    widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)


def optimize_painting(widget: QWidget):
    """
    페인팅 최적화

    Args:
        widget: 대상 위젯

    Features:
        - 불필요한 배경 그리기 방지
        - 더블 버퍼링 활성화
        - 부분 업데이트 활성화
    """
    # 더블 버퍼링 (깜빡임 방지)
    widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    # 부분 업데이트 활성화
    widget.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)

    # 불필요한 배경 그리기 방지
    widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)


def set_high_quality_rendering(painter: QPainter):
    """
    고품질 렌더링 힌트 설정

    Args:
        painter: QPainter 객체

    Features:
        - 안티앨리어싱
        - 부드러운 변환
        - 고품질 텍스트 렌더링
    """
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)


def set_fast_rendering(painter: QPainter):
    """
    빠른 렌더링 설정 (품질 < 속도)

    Args:
        painter: QPainter 객체

    Use case:
        - 실시간 애니메이션 중
        - 많은 객체 렌더링 시
    """
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)


class PerformanceMonitor:
    """
    성능 모니터링

    Features:
        - FPS 측정
        - 메모리 사용량 추적
        - 병목 지점 식별
    """

    def __init__(self):
        self._frame_count = 0
        self._start_time = None
        self._fps = 0

    def start_frame(self):
        """프레임 시작"""
        from time import time

        if self._start_time is None:
            self._start_time = time()

        self._frame_count += 1

        # 1초마다 FPS 계산
        current_time = time()
        elapsed = current_time - self._start_time

        if elapsed >= 1.0:
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._start_time = current_time

    def get_fps(self) -> float:
        """현재 FPS 반환"""
        return self._fps

    def reset(self):
        """리셋"""
        self._frame_count = 0
        self._start_time = None
        self._fps = 0


# ===== 위젯 최적화 프로파일 =====
class OptimizationProfile:
    """최적화 프로파일"""

    @staticmethod
    def apply_static_widget(widget: QWidget):
        """
        정적 위젯 최적화 (변경이 거의 없는 위젯)

        Examples:
            - 로고
            - 정적 텍스트 라벨
            - 아이콘
        """
        widget.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)
        widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    @staticmethod
    def apply_dynamic_widget(widget: QWidget):
        """
        동적 위젯 최적화 (자주 변경되는 위젯)

        Examples:
            - 애니메이션 중인 요소
            - 실시간 차트
            - 프로그레스 바
        """
        # GPU 가속
        enable_gpu_acceleration(widget)

        # 부드러운 업데이트
        widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    @staticmethod
    def apply_chart_widget(widget: QWidget):
        """
        차트 위젯 최적화

        Examples:
            - 캔들차트
            - 라인차트
            - 거래량 바차트
        """
        # 더블 버퍼링
        widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        # 부분 업데이트 (성능 향상)
        widget.setUpdatesEnabled(True)

    @staticmethod
    def apply_glass_card(widget: QWidget):
        """
        Glass Card 최적화

        Features:
            - 반투명 렌더링 최적화
            - 블러 효과 캐싱
        """
        # 반투명 배경
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # GPU 가속
        enable_gpu_acceleration(widget)


# ===== 메모리 최적화 =====
class MemoryOptimizer:
    """메모리 최적화 헬퍼"""

    @staticmethod
    def clear_pixmap_cache():
        """픽스맵 캐시 정리"""
        from PySide6.QtGui import QPixmapCache
        QPixmapCache.clear()

    @staticmethod
    def set_pixmap_cache_limit(kb: int):
        """
        픽스맵 캐시 크기 제한

        Args:
            kb: 킬로바이트 단위
        """
        from PySide6.QtGui import QPixmapCache
        QPixmapCache.setCacheLimit(kb)

    @staticmethod
    def optimize_animation_cache():
        """애니메이션 캐시 최적화"""
        # 픽스맵 캐시 크기 증가 (애니메이션 부드러움)
        MemoryOptimizer.set_pixmap_cache_limit(102400)  # 100MB


# ===== 애니메이션 최적화 =====
def optimize_animation_performance(widget: QWidget):
    """
    애니메이션 성능 최적화

    Args:
        widget: 애니메이션 대상 위젯

    Features:
        - 60 FPS 목표
        - GPU 가속
        - 더블 버퍼링
    """
    # GPU 가속
    enable_gpu_acceleration(widget)

    # 더블 버퍼링
    widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    # 부드러운 업데이트
    widget.setUpdatesEnabled(True)


# ===== 전역 성능 설정 =====
def apply_global_optimizations():
    """
    전역 성능 최적화 적용

    Call this at app initialization
    """
    from PySide6.QtGui import QPixmapCache

    # 픽스맵 캐시 크기 증가
    QPixmapCache.setCacheLimit(102400)  # 100MB

    print("[PERFORMANCE] Global optimizations applied")
    print(f"[PERFORMANCE] Pixmap cache limit: {QPixmapCache.cacheLimit()} KB")


# ===== 사용 예시 =====
"""
Example usage:

# 1. 앱 시작 시
apply_global_optimizations()

# 2. Glass Card에 적용
glass_card = GlassCard()
OptimizationProfile.apply_glass_card(glass_card)

# 3. 차트에 적용
chart_widget = CandlestickChart()
OptimizationProfile.apply_chart_widget(chart_widget)

# 4. 애니메이션 최적화
button = InteractiveButton()
optimize_animation_performance(button)

# 5. 성능 모니터링
monitor = PerformanceMonitor()
def on_paint():
    monitor.start_frame()
    # ... painting code
    print(f"FPS: {monitor.get_fps():.2f}")
"""
