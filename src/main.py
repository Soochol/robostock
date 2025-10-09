"""
RoboStock - 거래량 블록 기반 장기투자 분석 플랫폼
메인 진입점

실행 방법:
    프로젝트 루트에서: python -m src.main
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.config import APP_CONFIG
from styles.theme import theme_manager
from ui.windows.main_window import MainWindow
from infrastructure.database import init_database


def setup_app():
    """앱 초기 설정"""
    app = QApplication(sys.argv)

    # 앱 정보 설정
    app.setApplicationName(APP_CONFIG["name"])
    app.setOrganizationName(APP_CONFIG["organization"])
    app.setApplicationVersion(APP_CONFIG["version"])

    # 기본 폰트 설정
    font = QFont("Inter", 14)
    app.setFont(font)

    # 테마 적용
    app.setStyleSheet(theme_manager.get_stylesheet())

    # 고해상도 지원 (Qt 6에서는 기본적으로 활성화되어 있음)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Deprecated in Qt 6
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # Deprecated in Qt 6

    return app


def main():
    """메인 함수"""
    # 데이터베이스 초기화
    print("[INFO] Database initialization...")
    init_database()

    app = setup_app()

    # 메인 윈도우 생성
    window = MainWindow()
    window.show()

    # 이벤트 루프 시작
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
