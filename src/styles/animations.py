"""
Animation System - Modern UI Animations
애니메이션 시스템 (부드러운 전환 효과)

2024-2025 Design Trends:
- Easing functions (Material Design 3)
- Hover/Press state transitions
- Smooth page transitions
- Micro-interactions
"""

from PySide6.QtCore import (
    QEasingCurve, QPropertyAnimation, QParallelAnimationGroup,
    QSequentialAnimationGroup, QObject, Property
)
from PySide6.QtWidgets import QGraphicsOpacityEffect


# ===== Easing Curves (Material Design 3) =====
EASINGS = {
    # Standard (일반적인 전환)
    'standard': QEasingCurve.Type.OutCubic,
    'standard_decelerate': QEasingCurve.Type.OutQuad,
    'standard_accelerate': QEasingCurve.Type.InQuad,

    # Emphasized (강조된 전환 - 중요한 UI 변경)
    'emphasized': QEasingCurve.Type.OutQuart,
    'emphasized_decelerate': QEasingCurve.Type.OutExpo,
    'emphasized_accelerate': QEasingCurve.Type.InExpo,

    # Legacy (기존 스타일 - 호환성)
    'ease_in_out': QEasingCurve.Type.InOutCubic,
    'ease_out': QEasingCurve.Type.OutCubic,
    'ease_in': QEasingCurve.Type.InCubic,

    # Special effects
    'bounce': QEasingCurve.Type.OutBounce,
    'elastic': QEasingCurve.Type.OutElastic,
}

# ===== Duration (밀리초) =====
DURATIONS = {
    # MD3 기준
    'instant': 0,
    'extra_short': 50,    # 아이콘 회전 등
    'short': 100,         # 호버 효과
    'medium': 200,        # 카드 이동
    'long': 300,          # 패널 전환
    'extra_long': 500,    # 페이지 전환
    'extended': 800,      # 복잡한 애니메이션
}


# ===== Animation Helpers =====
def create_fade_animation(
    widget,
    start_opacity: float = 0.0,
    end_opacity: float = 1.0,
    duration: int = DURATIONS['medium'],
    easing: str = 'standard'
):
    """
    페이드 애니메이션 생성

    Args:
        widget: 대상 위젯
        start_opacity: 시작 불투명도 (0.0 ~ 1.0)
        end_opacity: 끝 불투명도 (0.0 ~ 1.0)
        duration: 지속 시간 (ms)
        easing: 이징 커브 이름

    Returns:
        QPropertyAnimation
    """
    # Opacity effect 설정
    if not widget.graphicsEffect():
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    effect = widget.graphicsEffect()

    # Animation 생성
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(start_opacity)
    animation.setEndValue(end_opacity)
    animation.setEasingCurve(EASINGS.get(easing, EASINGS['standard']))

    return animation


def create_slide_animation(
    widget,
    start_pos,
    end_pos,
    duration: int = DURATIONS['medium'],
    easing: str = 'emphasized'
):
    """
    슬라이드 애니메이션 생성

    Args:
        widget: 대상 위젯
        start_pos: 시작 위치 (QPoint)
        end_pos: 끝 위치 (QPoint)
        duration: 지속 시간 (ms)
        easing: 이징 커브 이름

    Returns:
        QPropertyAnimation
    """
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(EASINGS.get(easing, EASINGS['emphasized']))

    return animation


def create_scale_animation(
    widget,
    start_scale: float = 0.8,
    end_scale: float = 1.0,
    duration: int = DURATIONS['short'],
    easing: str = 'emphasized'
):
    """
    스케일 애니메이션 생성 (크기 변화)

    Note: QWidget은 scale property가 없으므로 geometry를 사용

    Args:
        widget: 대상 위젯
        start_scale: 시작 스케일
        end_scale: 끝 스케일
        duration: 지속 시간 (ms)
        easing: 이징 커브 이름

    Returns:
        QPropertyAnimation
    """
    # Geometry 기반 스케일링
    original_geometry = widget.geometry()
    center = original_geometry.center()

    start_width = int(original_geometry.width() * start_scale)
    start_height = int(original_geometry.height() * start_scale)

    start_geometry = original_geometry.adjusted(
        (original_geometry.width() - start_width) // 2,
        (original_geometry.height() - start_height) // 2,
        -(original_geometry.width() - start_width) // 2,
        -(original_geometry.height() - start_height) // 2
    )

    animation = QPropertyAnimation(widget, b"geometry")
    animation.setDuration(duration)
    animation.setStartValue(start_geometry)
    animation.setEndValue(original_geometry)
    animation.setEasingCurve(EASINGS.get(easing, EASINGS['emphasized']))

    return animation


def create_hover_animation(
    widget,
    property_name: bytes,
    normal_value,
    hover_value,
    duration: int = DURATIONS['short']
):
    """
    호버 애니메이션 생성 (일반 ↔ 호버 상태)

    Args:
        widget: 대상 위젯
        property_name: 속성 이름 (예: b"pos", b"opacity")
        normal_value: 일반 상태 값
        hover_value: 호버 상태 값
        duration: 지속 시간 (ms)

    Returns:
        Tuple[QPropertyAnimation, QPropertyAnimation] (enter, leave)
    """
    # Enter animation
    enter_anim = QPropertyAnimation(widget, property_name)
    enter_anim.setDuration(duration)
    enter_anim.setStartValue(normal_value)
    enter_anim.setEndValue(hover_value)
    enter_anim.setEasingCurve(EASINGS['standard'])

    # Leave animation
    leave_anim = QPropertyAnimation(widget, property_name)
    leave_anim.setDuration(duration)
    leave_anim.setStartValue(hover_value)
    leave_anim.setEndValue(normal_value)
    leave_anim.setEasingCurve(EASINGS['standard'])

    return enter_anim, leave_anim


def create_press_animation(
    widget,
    duration: int = DURATIONS['extra_short']
):
    """
    프레스 애니메이션 (클릭 피드백)

    버튼 클릭 시 살짝 줄어들었다 원래대로 돌아오는 효과

    Args:
        widget: 대상 위젯
        duration: 지속 시간 (ms)

    Returns:
        QSequentialAnimationGroup
    """
    # Scale down
    press_down = create_scale_animation(
        widget, 1.0, 0.95, duration, 'standard_accelerate'
    )

    # Scale up
    press_up = create_scale_animation(
        widget, 0.95, 1.0, duration, 'standard_decelerate'
    )

    # Sequential
    group = QSequentialAnimationGroup()
    group.addAnimation(press_down)
    group.addAnimation(press_up)

    return group


def create_fade_slide_in(
    widget,
    direction: str = 'up',
    distance: int = 20,
    duration: int = DURATIONS['medium']
):
    """
    페이드 + 슬라이드 인 (등장 효과)

    Args:
        widget: 대상 위젯
        direction: 'up', 'down', 'left', 'right'
        distance: 이동 거리 (px)
        duration: 지속 시간 (ms)

    Returns:
        QParallelAnimationGroup
    """
    # Fade animation
    fade = create_fade_animation(widget, 0.0, 1.0, duration)

    # Slide animation
    current_pos = widget.pos()

    if direction == 'up':
        start_pos = current_pos.translated(0, distance)
    elif direction == 'down':
        start_pos = current_pos.translated(0, -distance)
    elif direction == 'left':
        start_pos = current_pos.translated(distance, 0)
    elif direction == 'right':
        start_pos = current_pos.translated(-distance, 0)
    else:
        start_pos = current_pos

    slide = create_slide_animation(widget, start_pos, current_pos, duration)

    # Parallel
    group = QParallelAnimationGroup()
    group.addAnimation(fade)
    group.addAnimation(slide)

    return group


# ===== Preset Animations =====
class AnimationPresets:
    """미리 정의된 애니메이션 프리셋"""

    @staticmethod
    def card_appear(widget):
        """카드 등장 (페이드 + 위로 슬라이드)"""
        return create_fade_slide_in(widget, 'up', 20, DURATIONS['medium'])

    @staticmethod
    def modal_open(widget):
        """모달 열기 (페이드 + 스케일)"""
        fade = create_fade_animation(widget, 0.0, 1.0, DURATIONS['long'])
        scale = create_scale_animation(
            widget, 0.9, 1.0, DURATIONS['long'], 'emphasized'
        )

        group = QParallelAnimationGroup()
        group.addAnimation(fade)
        group.addAnimation(scale)
        return group

    @staticmethod
    def modal_close(widget):
        """모달 닫기"""
        fade = create_fade_animation(widget, 1.0, 0.0, DURATIONS['medium'])
        scale = create_scale_animation(
            widget, 1.0, 0.95, DURATIONS['medium'], 'standard'
        )

        group = QParallelAnimationGroup()
        group.addAnimation(fade)
        group.addAnimation(scale)
        return group

    @staticmethod
    def notification_slide_in(widget):
        """알림 슬라이드 인 (오른쪽에서)"""
        return create_fade_slide_in(widget, 'right', 30, DURATIONS['long'])

    @staticmethod
    def button_press(widget):
        """버튼 프레스"""
        return create_press_animation(widget, DURATIONS['extra_short'])

    @staticmethod
    def card_disappear(widget):
        """카드 사라짐 (페이드 아웃 + 아래로 슬라이드)"""
        fade = create_fade_animation(widget, 1.0, 0.0, DURATIONS['medium'])

        current_pos = widget.pos()
        end_pos = current_pos.translated(0, 20)
        slide = create_slide_animation(widget, current_pos, end_pos, DURATIONS['medium'])

        group = QParallelAnimationGroup()
        group.addAnimation(fade)
        group.addAnimation(slide)
        return group

    @staticmethod
    def shake(widget, intensity: int = 10):
        """흔들기 효과 (에러 피드백)"""
        current_pos = widget.pos()
        shake_sequence = QSequentialAnimationGroup()

        for i in range(3):
            right = create_slide_animation(
                widget,
                current_pos.translated(-intensity if i > 0 else 0, 0),
                current_pos.translated(intensity, 0),
                DURATIONS['extra_short']
            )
            shake_sequence.addAnimation(right)

            left = create_slide_animation(
                widget,
                current_pos.translated(intensity, 0),
                current_pos.translated(-intensity, 0),
                DURATIONS['extra_short']
            )
            shake_sequence.addAnimation(left)

        reset = create_slide_animation(
            widget,
            current_pos.translated(-intensity, 0),
            current_pos,
            DURATIONS['extra_short']
        )
        shake_sequence.addAnimation(reset)
        return shake_sequence

    @staticmethod
    def bounce(widget):
        """튕기기 효과 (성공 피드백)"""
        scale_up = create_scale_animation(widget, 1.0, 1.1, DURATIONS['short'])
        scale_down = create_scale_animation(widget, 1.1, 0.95, DURATIONS['short'])
        scale_normal = create_scale_animation(widget, 0.95, 1.0, DURATIONS['short'])

        sequence = QSequentialAnimationGroup()
        sequence.addAnimation(scale_up)
        sequence.addAnimation(scale_down)
        sequence.addAnimation(scale_normal)
        return sequence

    @staticmethod
    def pulse(widget, count: int = 3):
        """맥박 효과 (주목 유도)"""
        sequence = QSequentialAnimationGroup()

        for _ in range(count):
            scale_up = create_scale_animation(widget, 1.0, 1.05, DURATIONS['short'])
            scale_down = create_scale_animation(widget, 1.05, 1.0, DURATIONS['short'])
            sequence.addAnimation(scale_up)
            sequence.addAnimation(scale_down)

        return sequence
