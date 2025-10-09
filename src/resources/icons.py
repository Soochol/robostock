"""SVG 아이콘 통합 관리 시스템

Lucide Icons 기반 + 커스텀 네온 스타일 아이콘
"""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, QSize, Qt
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class IconManager:
    """SVG 아이콘 통합 관리 클래스"""

    # 기본 색상 상수
    DEFAULT_COLOR = "#E2E8F0"
    MENU_COLOR = "#94A3B8"
    PRIMARY_COLOR = "#667eea"

    # 아이콘 캐시
    _icon_cache: Dict[str, QIcon] = {}

    # Lucide Icons - 메뉴 및 공통 아이콘
    LUCIDE_ICONS: Dict[str, str] = {
        # 메인 네비게이션
        'target': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>''',

        'download': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>''',

        'search': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>''',

        'bar-chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>''',

        'folder': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>''',

        'microscope': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2"/><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/></svg>''',

        'brain': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>''',

        'zap': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>''',

        'settings': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>''',

        'bell': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>''',

        'user': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',

        'filter': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>''',

        # 추가 공통 아이콘
        'upload': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>''',

        'trash': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>''',

        'check-circle': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>''',

        'alert-triangle': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>''',

        'alert-circle': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>''',

        'info': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>''',

        'x-circle': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>''',

        'trophy': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>''',

        'medal': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15"/><path d="M11 12 5.12 2.2"/><path d="m13 12 5.88-9.8"/><path d="M8 7h8"/><circle cx="12" cy="17" r="5"/><path d="M12 18v-2h-.5"/></svg>''',

        'trending-up': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>''',

        'activity': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>''',

        'layers': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>''',

        'save': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>''',

        'map-pin': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>''',
    }

    # 커스텀 네온 블록 아이콘 (색상 구분)
    CUSTOM_ICONS: Dict[str, str] = {
        'block_1': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" fill="#FF0080" opacity="0.2"/>
            <circle cx="12" cy="12" r="7" fill="none" stroke="#FF0080" stroke-width="2.5"/>
            <circle cx="12" cy="12" r="3" fill="#FF0080"/>
        </svg>''',

        'block_2': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" fill="#00FF88" opacity="0.2"/>
            <circle cx="12" cy="12" r="7" fill="none" stroke="#00FF88" stroke-width="2.5"/>
            <circle cx="12" cy="12" r="3" fill="#00FF88"/>
        </svg>''',

        'block_3': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" fill="#00D4FF" opacity="0.2"/>
            <circle cx="12" cy="12" r="7" fill="none" stroke="#00D4FF" stroke-width="2.5"/>
            <circle cx="12" cy="12" r="3" fill="#00D4FF"/>
        </svg>''',

        'block_4': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" fill="#FFD700" opacity="0.2"/>
            <circle cx="12" cy="12" r="7" fill="none" stroke="#FFD700" stroke-width="2.5"/>
            <circle cx="12" cy="12" r="3" fill="#FFD700"/>
        </svg>''',
    }

    @staticmethod
    def _apply_color_to_svg(svg: str, color: str) -> str:
        """SVG의 currentColor를 실제 색상으로 변경"""
        return svg.replace('currentColor', color)

    @staticmethod
    def get_svg(name: str, color: str = "#E2E8F0") -> str:
        """SVG 문자열 반환

        Args:
            name: 아이콘 이름
            color: 색상 (Lucide 아이콘에만 적용)

        Returns:
            SVG 문자열
        """
        # 커스텀 아이콘 우선
        if name in IconManager.CUSTOM_ICONS:
            return IconManager.CUSTOM_ICONS[name]

        # Lucide 아이콘
        if name in IconManager.LUCIDE_ICONS:
            svg = IconManager.LUCIDE_ICONS[name]
            return IconManager._apply_color_to_svg(svg, color)

        # 없으면 기본 원형
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="8" fill="none" stroke="{color}" stroke-width="2"/>
        </svg>'''

    @staticmethod
    def get_qicon(name: str, size: int = 24, color: str = None) -> QIcon:
        """QIcon 반환

        Args:
            name: 아이콘 이름
            size: 크기 (픽셀)
            color: 색상 (None이면 기본 색상)

        Returns:
            QIcon 객체
        """
        if color is None:
            color = IconManager.DEFAULT_COLOR

        # 캐시 키 생성
        cache_key = f"{name}_{size}_{color}"

        # 캐시 확인
        if cache_key in IconManager._icon_cache:
            return IconManager._icon_cache[cache_key]

        try:
            svg_str = IconManager.get_svg(name, color)

            # QSvgRenderer로 렌더링
            renderer = QSvgRenderer(QByteArray(svg_str.encode('utf-8')))

            if not renderer.isValid():
                logger.warning(f"Invalid SVG for icon: {name}")
                return QIcon()

            # QPixmap 생성
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(Qt.GlobalColor.transparent)

            # 렌더링
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            icon = QIcon(pixmap)

            # 캐시 저장
            IconManager._icon_cache[cache_key] = icon

            return icon

        except Exception as e:
            logger.error(f"Error creating icon '{name}': {e}")
            return QIcon()

    @staticmethod
    def get_colored_icon(name: str, size: int = 24,
                        stroke_color: str = None,
                        fill_color: Optional[str] = None) -> QIcon:
        """색상 커스터마이징된 QIcon 반환

        Args:
            name: 아이콘 이름
            size: 크기
            stroke_color: 선 색상 (None이면 기본 색상)
            fill_color: 채우기 색상 (None이면 투명)

        Returns:
            QIcon 객체
        """
        if stroke_color is None:
            stroke_color = IconManager.DEFAULT_COLOR

        try:
            svg_str = IconManager.get_svg(name, stroke_color)

            if fill_color:
                svg_str = svg_str.replace('fill="none"', f'fill="{fill_color}"')

            renderer = QSvgRenderer(QByteArray(svg_str.encode('utf-8')))

            if not renderer.isValid():
                logger.warning(f"Invalid SVG for colored icon: {name}")
                return QIcon()

            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            logger.error(f"Error creating colored icon '{name}': {e}")
            return QIcon()

    @staticmethod
    def clear_cache():
        """아이콘 캐시 초기화"""
        IconManager._icon_cache.clear()
        logger.info("Icon cache cleared")


# 편의 함수
def get_menu_icon(name: str, size: int = 20) -> QIcon:
    """메뉴용 아이콘 (회색)"""
    return IconManager.get_qicon(name, size, IconManager.MENU_COLOR)


def get_primary_icon(name: str, size: int = 20) -> QIcon:
    """프라이머리 아이콘 (그라데이션 블루)"""
    return IconManager.get_qicon(name, size, IconManager.PRIMARY_COLOR)


def get_block_icon(block_num: int, size: int = 16) -> QIcon:
    """블록 아이콘 (1~4번)"""
    return IconManager.get_qicon(f'block_{block_num}', size)


def get_level_icon(level: int, size: int = 18) -> QIcon:
    """레벨 아이콘 (0~4)"""
    icon_map = {
        4: 'trophy',
        3: 'medal',
        2: 'medal',
        1: 'medal',
        0: 'x-circle',
    }

    color_map = {
        4: "#FFD700",  # 골드
        3: "#FFD700",  # 골드
        2: "#C0C0C0",  # 실버
        1: "#CD7F32",  # 브론즈
        0: "#EF4444",  # 레드
    }

    name = icon_map.get(level, 'x-circle')
    color = color_map.get(level, "#94A3B8")

    return IconManager.get_qicon(name, size, color)


def get_status_icon(status: str, size: int = 16) -> QIcon:
    """상태 아이콘"""
    icon_map = {
        'success': 'check-circle',
        'warning': 'alert-triangle',
        'error': 'alert-circle',
        'info': 'info',
    }

    color_map = {
        'success': "#10B981",
        'warning': "#F59E0B",
        'error': "#EF4444",
        'info': "#3B82F6",
    }

    name = icon_map.get(status, 'info')
    color = color_map.get(status, "#94A3B8")

    return IconManager.get_qicon(name, size, color)
