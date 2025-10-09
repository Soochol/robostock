"""
Block 1 Settings Section
1번 블록 조건 설정 섹션
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QButtonGroup,
    QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal

from core.config import BLOCK_CRITERIA
from styles.theme import theme_manager
from .collapsible_section import CollapsibleSection
from .setting_item import SettingItem
from .parameter_slider import ParameterSlider


class Block1SettingsSection(CollapsibleSection):
    """
    1번 블록 조건 설정 섹션

    조건:
    - 최대 거래량 (기간 설정 가능)
    - 거래대금 (최소값 설정 가능)
    - 신고가 등급 필터 (선택)
    - 가격 범위 필터 (선택)
    - 시가총액 필터 (선택)
    """

    settingsChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(
            title="1번 블록 조건 (초기 대량 거래일 탐지)",
            icon="🎯",
            expanded=True,
            parent=parent
        )

        self.settings = self._default_settings()
        self._setup_content()

    def _default_settings(self) -> dict:
        """기본 설정값"""
        return {
            'max_volume_enabled': True,
            'max_volume_period_days': BLOCK_CRITERIA['block_1']['max_volume_period_days'],
            'max_volume_comparison': '>=',  # >=, >, ==

            'trading_value_enabled': True,
            'min_trading_value': BLOCK_CRITERIA['block_1']['min_trading_value'],
            'trading_value_unit': '원',  # 원, 억원
            'trading_value_calculation': 'close_volume',  # close_volume, avg_volume, mid_volume

            # N개월 신고가 조건 (NEW)
            'price_high_enabled': True,
            'price_high_period_months': 3,  # 3개월 신고가

            'price_range_enabled': False,
            'price_min': 0,
            'price_max': 999999,
            'price_unlimited_max': True,

            'market_cap_enabled': False,
            'market_cap_min': 100_000_000_000,  # 1000억
        }

    def _setup_content(self):
        """컨텐츠 구성"""
        # 1. 최대 거래량 조건
        self._add_max_volume_setting()

        # 2. 거래대금 조건
        self._add_trading_value_setting()

        # 3. N개월 신고가 조건 (NEW)
        self._add_price_high_setting()

        # 4. 가격 범위 필터
        self._add_price_range_setting()

        # 5. 시가총액 필터
        self._add_market_cap_setting()

    def _add_max_volume_setting(self):
        """최대 거래량 조건"""
        # 파라미터 컨테이너
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 비교 방식
        comparison_widget = self._create_comparison_widget()
        params_layout.addWidget(comparison_widget)

        # 설정 항목 생성
        setting = SettingItem(
            label="최대 거래량 조건",
            description="해당 날짜 기준 N일 이내 최대 거래량",
            control_widget=params_widget,
            checked=self.settings['max_volume_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('max_volume_enabled', checked)
        )

        self.add_widget(setting)

    def _add_trading_value_setting(self):
        """거래대금 조건"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 거래대금 입력
        from PySide6.QtWidgets import QLabel
        trading_value_layout = QHBoxLayout()
        trading_value_label = QLabel("최소 거래대금:")
        trading_value_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
            min-width: 100px;
        """)
        trading_value_layout.addWidget(trading_value_label)

        self.trading_value_spinbox = QSpinBox()
        self.trading_value_spinbox.setRange(1, 999_999)
        self.trading_value_spinbox.setValue(self.settings['min_trading_value'] // 100_000_000)
        self.trading_value_spinbox.setSuffix(" 억원")
        self.trading_value_spinbox.setSingleStep(100)
        self.trading_value_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.trading_value_spinbox.valueChanged.connect(
            lambda value: self._update_setting('min_trading_value', value * 100_000_000)
        )
        trading_value_layout.addWidget(self.trading_value_spinbox)
        params_layout.addLayout(trading_value_layout)

        # 계산 방식
        calc_widget = self._create_calculation_widget()
        params_layout.addWidget(calc_widget)

        setting = SettingItem(
            label="거래대금 조건",
            description="최소 거래대금 기준 (현재: {:,.0f}억원)".format(
                self.settings['min_trading_value'] / 100_000_000
            ),
            control_widget=params_widget,
            checked=self.settings['trading_value_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('trading_value_enabled', checked)
        )

        self.add_widget(setting)

    def _add_price_high_setting(self):
        """N개월 신고가 조건"""
        # N개월 슬라이더
        period_slider = ParameterSlider(
            label="신고가 기간 (개월)",
            min_value=1,
            max_value=24,
            default_value=self.settings.get('price_high_period_months', 3),
            suffix="개월"
        )
        period_slider.valueChanged.connect(
            lambda value: self._update_setting('price_high_period_months', value)
        )

        setting = SettingItem(
            label="N개월 신고가 조건",
            description="D일 고점이 N개월 내 신고가여야 함 (현재: {}개월)".format(
                self.settings.get('price_high_period_months', 3)
            ),
            control_widget=period_slider,
            checked=self.settings.get('price_high_enabled', True)
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('price_high_enabled', checked)
        )

        self.add_widget(setting)

    def _add_price_range_setting(self):
        """가격 범위 필터"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 최소 가격
        min_price_layout = QHBoxLayout()
        min_label = QLabel("최소 주가:")
        min_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
            min-width: 80px;
        """)
        min_price_layout.addWidget(min_label)

        self.price_min_spinbox = QSpinBox()
        self.price_min_spinbox.setRange(0, 999_999_999)
        self.price_min_spinbox.setValue(self.settings['price_min'])
        self.price_min_spinbox.setSuffix(" 원")
        self.price_min_spinbox.setSingleStep(1000)
        self.price_min_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.price_min_spinbox.valueChanged.connect(
            lambda value: self._update_setting('price_min', value)
        )
        min_price_layout.addWidget(self.price_min_spinbox)
        params_layout.addLayout(min_price_layout)

        # 최대 가격
        max_price_layout = QHBoxLayout()
        max_label = QLabel("최대 주가:")
        max_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
            min-width: 80px;
        """)
        max_price_layout.addWidget(max_label)

        self.price_max_spinbox = QSpinBox()
        self.price_max_spinbox.setRange(0, 999_999_999)
        self.price_max_spinbox.setValue(self.settings['price_max'])
        self.price_max_spinbox.setSuffix(" 원")
        self.price_max_spinbox.setSingleStep(1000)
        self.price_max_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.price_max_spinbox.setEnabled(not self.settings['price_unlimited_max'])
        self.price_max_spinbox.valueChanged.connect(
            lambda value: self._update_setting('price_max', value)
        )
        max_price_layout.addWidget(self.price_max_spinbox)
        params_layout.addLayout(max_price_layout)

        # 무제한 체크박스
        self.price_unlimited_checkbox = QCheckBox("최대 가격 무제한")
        self.price_unlimited_checkbox.setChecked(self.settings['price_unlimited_max'])
        self.price_unlimited_checkbox.toggled.connect(
            lambda checked: self._on_price_unlimited_changed(checked)
        )
        params_layout.addWidget(self.price_unlimited_checkbox)

        setting = SettingItem(
            label="가격 범위 필터",
            description="주가 범위 지정 (최소: {:,}원 ~ 최대: {})".format(
                self.settings['price_min'],
                "무제한" if self.settings['price_unlimited_max'] else f"{self.settings['price_max']:,}원"
            ),
            control_widget=params_widget,
            checked=self.settings['price_range_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('price_range_enabled', checked)
        )

        self.add_widget(setting)

    def _add_market_cap_setting(self):
        """시가총액 필터"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 최소 시가총액 입력
        market_cap_layout = QHBoxLayout()
        market_cap_label = QLabel("최소 시가총액:")
        market_cap_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 12px;
            min-width: 100px;
        """)
        market_cap_layout.addWidget(market_cap_label)

        self.market_cap_spinbox = QSpinBox()
        self.market_cap_spinbox.setRange(0, 999_999)
        self.market_cap_spinbox.setValue(self.settings['market_cap_min'] // 100_000_000)
        self.market_cap_spinbox.setSuffix(" 억원")
        self.market_cap_spinbox.setSingleStep(100)
        self.market_cap_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.market_cap_spinbox.valueChanged.connect(
            lambda value: self._update_setting('market_cap_min', value * 100_000_000)
        )
        market_cap_layout.addWidget(self.market_cap_spinbox)
        params_layout.addLayout(market_cap_layout)

        # 빠른 선택 버튼
        quick_select_layout = QHBoxLayout()
        quick_values = [
            ("100억", 100),
            ("500억", 500),
            ("1000억", 1000),
            ("5000억", 5000),
            ("1조", 10000)
        ]

        for label, value in quick_values:
            btn = QPushButton(label)
            btn.setFixedWidth(60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {theme_manager.colors['bg_layer_3']};
                    color: {theme_manager.colors['text_secondary']};
                    border: 1px solid {theme_manager.colors['border']};
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background: {theme_manager.colors['primary_subtle']};
                    border-color: {theme_manager.colors['primary']};
                }}
            """)
            btn.clicked.connect(
                lambda checked, v=value: self.market_cap_spinbox.setValue(v)
            )
            quick_select_layout.addWidget(btn)

        quick_select_layout.addStretch()
        params_layout.addLayout(quick_select_layout)

        setting = SettingItem(
            label="시가총액 필터",
            description="최소 시가총액 기준 (현재: {:,}억원)".format(
                self.settings['market_cap_min'] // 100_000_000
            ),
            control_widget=params_widget,
            checked=self.settings['market_cap_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('market_cap_enabled', checked)
        )

        self.add_widget(setting)

    def _create_comparison_widget(self) -> QWidget:
        """비교 방식 라디오 버튼"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        from PySide6.QtWidgets import QLabel
        label = QLabel("최대 거래량 탐지 조건")
        label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 11px;
        """)
        layout.addWidget(label)

        button_group = QButtonGroup(widget)

        rb1 = QRadioButton("기간 내 최대 거래량 포함 (추천)")
        rb1.setToolTip("해당 날짜가 기간 내 최대 거래량과 같거나 큰 경우 탐지")
        rb1.setChecked(self.settings['max_volume_comparison'] == '>=')
        rb1.toggled.connect(
            lambda checked: checked and self._update_setting('max_volume_comparison', '>=')
        )
        button_group.addButton(rb1)
        layout.addWidget(rb1)

        rb2 = QRadioButton("신기록 경신만 (엄격)")
        rb2.setToolTip("해당 날짜가 기간 내 최대 거래량을 초과하는 경우만 탐지 (같은 값 제외)")
        rb2.setChecked(self.settings['max_volume_comparison'] == '>')
        rb2.toggled.connect(
            lambda checked: checked and self._update_setting('max_volume_comparison', '>')
        )
        button_group.addButton(rb2)
        layout.addWidget(rb2)

        rb3 = QRadioButton("정확히 동일한 값만")
        rb3.setToolTip("해당 날짜가 기간 내 최대 거래량과 정확히 같은 경우만 탐지 (거의 사용 안함)")
        rb3.setChecked(self.settings['max_volume_comparison'] == '==')
        rb3.toggled.connect(
            lambda checked: checked and self._update_setting('max_volume_comparison', '==')
        )
        button_group.addButton(rb3)
        layout.addWidget(rb3)

        return widget

    def _create_calculation_widget(self) -> QWidget:
        """계산 방식 라디오 버튼"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        from PySide6.QtWidgets import QLabel
        label = QLabel("계산 방식")
        label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 11px;
        """)
        layout.addWidget(label)

        button_group = QButtonGroup(widget)

        rb1 = QRadioButton("종가 × 거래량")
        rb1.setChecked(self.settings['trading_value_calculation'] == 'close_volume')
        rb1.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_calculation', 'close_volume')
        )
        button_group.addButton(rb1)
        layout.addWidget(rb1)

        rb2 = QRadioButton("평균가 × 거래량")
        rb2.setChecked(self.settings['trading_value_calculation'] == 'avg_volume')
        rb2.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_calculation', 'avg_volume')
        )
        button_group.addButton(rb2)
        layout.addWidget(rb2)

        rb3 = QRadioButton("(시가+종가)/2 × 거래량")
        rb3.setChecked(self.settings['trading_value_calculation'] == 'mid_volume')
        rb3.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_calculation', 'mid_volume')
        )
        button_group.addButton(rb3)
        layout.addWidget(rb3)

        return widget

    def _on_price_unlimited_changed(self, checked: bool):
        """최대 가격 무제한 체크박스 변경"""
        self._update_setting('price_unlimited_max', checked)
        # 스핀박스 활성화/비활성화
        if hasattr(self, 'price_max_spinbox'):
            self.price_max_spinbox.setEnabled(not checked)

    def _update_setting(self, key: str, value):
        """설정 업데이트"""
        self.settings[key] = value
        self.settingsChanged.emit(self.settings)
        print(f"[DEBUG] Block1 Setting changed: {key} = {value}")

    def get_settings(self) -> dict:
        """현재 설정 반환"""
        return self.settings.copy()

    def apply_settings(self, settings: dict):
        """설정 적용"""
        self.settings.update(settings)
        # UI 업데이트는 생략 (복잡하므로 기본값으로 유지)

    def set_settings(self, settings: dict):
        """설정 적용"""
        self.settings.update(settings)
        # TODO: UI 업데이트
