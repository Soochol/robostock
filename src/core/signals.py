"""
Global Signals Hub
전역 이벤트 시그널 관리 (Pub/Sub 패턴)
컴포넌트 간 느슨한 결합 (Loose Coupling)
"""

from PySide6.QtCore import QObject, Signal

class GlobalSignals(QObject):
    """
    앱 전역에서 사용하는 시그널

    사용 예시:
        from core.signals import global_signals

        # 시그널 발행
        global_signals.stock_selected.emit("005930")

        # 시그널 구독
        global_signals.stock_selected.connect(self.on_stock_changed)
    """

    # ===== 종목 관련 =====
    stock_selected = Signal(str)  # ticker
    stock_added_to_favorites = Signal(str)  # ticker
    stock_removed_from_favorites = Signal(str)  # ticker

    # ===== 블록 관련 =====
    block_selected = Signal(int)  # block_id
    block_detection_started = Signal()
    block_detection_progress = Signal(int, str)  # (progress%, message)
    block_detection_finished = Signal(bool, int)  # (success, total_blocks)

    # ===== 케이스 관련 =====
    case_selected = Signal(int)  # case_id
    case_filter_changed = Signal(dict)  # filter_params
    case_added_to_comparison = Signal(int)  # case_id
    case_removed_from_comparison = Signal(int)  # case_id

    # ===== 데이터 수집 관련 =====
    collection_started = Signal(str)  # collection_type
    collection_progress = Signal(int, str)  # (progress%, message)
    collection_finished = Signal(bool, str)  # (success, message)
    collection_error = Signal(str)  # error_message

    # ===== 차트 관련 =====
    chart_date_range_changed = Signal(str, str)  # (start_date, end_date)
    chart_period_changed = Signal(str)  # period ("1D", "1W", "1M", etc.)
    chart_zoom_changed = Signal(float)  # zoom_level
    chart_block_center_requested = Signal(int)  # block_id

    # ===== 팩터 분석 관련 =====
    factor_analysis_started = Signal()
    factor_analysis_finished = Signal(dict)  # analysis_result
    factor_importance_updated = Signal(list)  # [(factor_name, importance), ...]

    # ===== 예측 관련 =====
    prediction_started = Signal(int)  # case_id
    prediction_finished = Signal(int, dict)  # (case_id, prediction_result)
    prediction_error = Signal(int, str)  # (case_id, error_message)

    # ===== UI 관련 =====
    theme_changed = Signal(str)  # "dark" or "light"
    layout_mode_changed = Signal(str)  # "standard", "focus", "analysis"
    sidebar_toggled = Signal(bool)  # is_visible
    analysis_panel_toggled = Signal(bool)  # is_visible

    # ===== 패널 관련 =====
    panel_changed = Signal(str)  # panel_type
    panel_refresh_requested = Signal(str)  # panel_type

    # ===== 알림 관련 =====
    notification_requested = Signal(str, str, str)  # (message, type, duration)
    toast_show = Signal(str, str)  # (message, type)

    # ===== 검색 관련 =====
    search_query_changed = Signal(str)  # query
    search_result_selected = Signal(str, str)  # (result_type, result_id)

    # ===== 백테스팅 관련 =====
    backtest_started = Signal(dict)  # config
    backtest_progress = Signal(int, str)  # (progress%, message)
    backtest_finished = Signal(dict)  # result
    backtest_error = Signal(str)  # error_message

    # ===== 파일 관련 =====
    export_requested = Signal(str, str)  # (export_type, file_path)
    export_finished = Signal(bool, str)  # (success, message)
    import_requested = Signal(str)  # file_path
    import_finished = Signal(bool, str)  # (success, message)

    # ===== 데이터베이스 관련 =====
    db_connection_changed = Signal(bool)  # is_connected
    db_data_updated = Signal(str)  # table_name
    db_error = Signal(str)  # error_message

    # ===== 설정 관련 =====
    settings_changed = Signal(str, object)  # (key, value)
    settings_reset_requested = Signal()

# 싱글톤 인스턴스
global_signals = GlobalSignals()
