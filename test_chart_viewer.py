"""
차트 뷰어 테스트 스크립트
블록탐지 결과를 차트에서 확인
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from src.ui.panels.chart_viewer_panel import ChartViewerPanel


def main():
    """차트 뷰어 패널 테스트"""
    app = QApplication(sys.argv)

    # 메인 윈도우
    window = QMainWindow()
    window.setWindowTitle("차트 뷰어 테스트")
    window.setGeometry(100, 100, 1400, 900)

    # 차트 뷰어 패널
    chart_viewer = ChartViewerPanel()
    window.setCentralWidget(chart_viewer)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
