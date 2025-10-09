"""
Block 2 Settings Section
2번 블록 조건 설정 섹션
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QButtonGroup, QCheckBox, QHBoxLayout
)
from PySide6.QtCore import Signal

from core.config import BLOCK_CRITERIA
from styles.theme import theme_manager
from .collapsible_section import CollapsibleSection
from .setting_item import SettingItem
from .parameter_slider import ParameterSlider


class Block2SettingsSection(CollapsibleSection):
    """
    2번 블록 조건 설정 섹션

    조건:
    - 거래량 비율 (1번 블록 대비)
    - 발생 기간 (최소/최대 일수)
    - 패턴 매칭 (D, D+D+1, D+D+2)
    - 거래대금 조건 (선택)
    """

    settingsChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(
            title="2번 블록 조건 (후속 대량 거래일 탐지)",
            icon="🔄",
            expanded=True,
            parent=parent
        )

        self.settings = self._default_settings()
        self._setup_content()

    def _default_settings(self) -> dict:
        """기본 설정값"""
        return {
            # 거래량 비율
            'volume_ratio_enabled': True,
            'volume_ratio_min': BLOCK_CRITERIA['block_2']['volume_ratio_min'],
            'volume_ratio_calculation': 'simple',  # simple, normalized
            'volume_ratio_comparison': 'block1',  # block1, avg_20days, total_avg

            # 발생 기간
            'period_enabled': True,
            'min_days_from_block1': 1,
            'max_days_from_block1': BLOCK_CRITERIA['block_2']['max_days_from_block1'],
            'use_business_days': False,

            # 패턴 매칭
            'pattern_enabled': True,
            'pattern_types': {
                'D': True,
                'D_D1': True,
                'D_D2': True,
                'D_D1_D2': True,
            },
            'pattern_threshold_pct': 80,  # D+1/D+2 거래량 임계값
            'pattern_avg_period': 20,  # 평균 계산 기간

            # 거래대금
            'trading_value_enabled': False,
            'min_trading_value': BLOCK_CRITERIA['block_2']['high_trading_value'],
            'trading_value_min_days': 1,  # 최소 N일 이상

            # 고점 돌파 조건 (NEW)
            'price_breakthrough_enabled': True,
            'price_breakthrough_pct': 30,  # 1번 블록 고점 대비 30% 이상
        }

    def _setup_content(self):
        """컨텐츠 구성"""
        # 1. 거래량 비율 조건
        self._add_volume_ratio_setting()

        # 2. 발생 기간 조건
        self._add_period_setting()

        # 3. 고점 돌파 조건 (NEW)
        self._add_price_breakthrough_setting()

        # 4. 패턴 매칭
        self._add_pattern_setting()

        # 5. 거래대금 조건
        self._add_trading_value_setting()

    def _add_volume_ratio_setting(self):
        """거래량 비율 조건"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 최소 거래량 비율 입력
        volume_ratio_slider = ParameterSlider(
            label="최소 거래량 비율 (%)",
            min_value=10,
            max_value=200,
            default_value=int(self.settings['volume_ratio_min'] * 100),
            suffix="%"
        )
        volume_ratio_slider.valueChanged.connect(
            lambda value: self._update_setting('volume_ratio_min', value / 100)
        )
        params_layout.addWidget(volume_ratio_slider)

        # 계산 방식
        calc_widget = self._create_calculation_widget()
        params_layout.addWidget(calc_widget)

        # 비교 대상
        comparison_widget = self._create_comparison_widget()
        params_layout.addWidget(comparison_widget)

        setting = SettingItem(
            label="거래량 비율 조건",
            description="1번 블록 대비 최소 비율 (현재: {}%)".format(
                int(self.settings['volume_ratio_min'] * 100)
            ),
            control_widget=params_widget,
            checked=self.settings['volume_ratio_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('volume_ratio_enabled', checked)
        )

        self.add_widget(setting)

    def _add_period_setting(self):
        """발생 기간 조건"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 최소 일수 입력
        min_days_slider = ParameterSlider(
            label="최소 일수 (1번 블록 이후)",
            min_value=1,
            max_value=30,
            default_value=self.settings['min_days_from_block1'],
            suffix="일"
        )
        min_days_slider.valueChanged.connect(
            lambda value: self._update_setting('min_days_from_block1', int(value))
        )
        params_layout.addWidget(min_days_slider)

        # 최대 일수 입력
        max_days_slider = ParameterSlider(
            label="최대 일수 (1번 블록 이후)",
            min_value=30,
            max_value=365,
            default_value=self.settings['max_days_from_block1'],
            suffix="일"
        )
        max_days_slider.valueChanged.connect(
            lambda value: self._update_setting('max_days_from_block1', int(value))
        )
        params_layout.addWidget(max_days_slider)

        # 영업일 기준 체크박스
        business_days_cb = QCheckBox("영업일 기준 (주말/공휴일 제외)")
        business_days_cb.setChecked(self.settings['use_business_days'])
        business_days_cb.toggled.connect(
            lambda checked: self._update_setting('use_business_days', checked)
        )
        business_days_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {theme_manager.colors['text_secondary']};
                font-size: 11px;
            }}
        """)
        params_layout.addWidget(business_days_cb)

        setting = SettingItem(
            label="발생 기간 조건",
            description="1번 블록 이후 발생 기간 범위 ({} ~ {}일)".format(
                self.settings['min_days_from_block1'],
                self.settings['max_days_from_block1']
            ),
            control_widget=params_widget,
            checked=self.settings['period_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('period_enabled', checked)
        )

        self.add_widget(setting)

    def _add_price_breakthrough_setting(self):
        """고점 돌파 조건"""
        # 돌파 비율 슬라이더
        breakthrough_slider = ParameterSlider(
            label="고점 돌파 비율 (%)",
            min_value=0,
            max_value=100,
            default_value=self.settings.get('price_breakthrough_pct', 30),
            suffix="%"
        )
        breakthrough_slider.valueChanged.connect(
            lambda value: self._update_setting('price_breakthrough_pct', value)
        )

        setting = SettingItem(
            label="고점 돌파 조건",
            description="D, D+1, D+2 중 하나가 1번 블록 고점 대비 {}% 이상 돌파".format(
                self.settings.get('price_breakthrough_pct', 30)
            ),
            control_widget=breakthrough_slider,
            checked=self.settings.get('price_breakthrough_enabled', True)
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('price_breakthrough_enabled', checked)
        )

        self.add_widget(setting)

    def _add_pattern_setting(self):
        """패턴 매칭"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 패턴 유형 선택
        from PySide6.QtWidgets import QLabel
        pattern_label = QLabel("패턴 유형 선택")
        pattern_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 11px;
        """)
        params_layout.addWidget(pattern_label)

        # 패턴 체크박스들 (3개로 수정)
        self.pattern_checkboxes = {}
        for pattern_key, pattern_name in [
            ('D_D1', 'D / D+1 (D 조건 AND D+1 조건)'),
            ('D_D2', 'D / D+2 (D 조건 AND D+2 조건)'),
            ('D_D1_D2', 'D / D+1, D+2 (D AND D+1 AND D+2)')
        ]:
            cb = QCheckBox(pattern_name)
            cb.setChecked(self.settings['pattern_types'].get(pattern_key, True))
            cb.toggled.connect(
                lambda checked, key=pattern_key: self._update_pattern_type(key, checked)
            )
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {theme_manager.colors['text_primary']};
                    font-size: 12px;
                    padding: 4px 0;
                }}
            """)
            params_layout.addWidget(cb)
            self.pattern_checkboxes[pattern_key] = cb

        # D+1 임계값 슬라이더
        self.pattern_d1_threshold_slider = ParameterSlider(
            label="D+1 거래량 임계값",
            min_value=50,
            max_value=100,
            default_value=self.settings.get('pattern_threshold_pct', 80),
            suffix="%"
        )
        self.pattern_d1_threshold_slider.valueChanged.connect(
            lambda value: self._update_setting('pattern_threshold_pct', value)
        )
        params_layout.addWidget(self.pattern_d1_threshold_slider)

        # D+2 임계값 슬라이더 (동일한 값 사용)
        self.pattern_d2_threshold_slider = ParameterSlider(
            label="D+2 거래량 임계값",
            min_value=50,
            max_value=100,
            default_value=self.settings.get('pattern_threshold_pct', 80),
            suffix="%"
        )
        self.pattern_d2_threshold_slider.valueChanged.connect(
            lambda value: self._update_setting('pattern_threshold_pct', value)
        )
        params_layout.addWidget(self.pattern_d2_threshold_slider)


        setting = SettingItem(
            label="패턴 매칭",
            description="연속 거래량 패턴 감지",
            control_widget=params_widget,
            checked=self.settings['pattern_enabled']
        )
        setting.toggled.connect(self._on_pattern_enabled_changed)

        self.add_widget(setting)

    def _add_trading_value_setting(self):
        """거래대금 조건"""
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(0, 8, 0, 0)
        params_layout.setSpacing(12)

        # 거래대금 입력
        from PySide6.QtWidgets import QLabel, QSpinBox
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

        # 조건 만족 일수
        days_label = QLabel("조건 만족 일수")
        days_label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 11px;
        """)
        params_layout.addWidget(days_label)

        button_group = QButtonGroup(params_widget)

        rb1 = QRadioButton("최소 1일")
        rb1.setChecked(self.settings['trading_value_min_days'] == 1)
        rb1.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_min_days', 1)
        )
        button_group.addButton(rb1)
        params_layout.addWidget(rb1)

        rb2 = QRadioButton("최소 2일")
        rb2.setChecked(self.settings['trading_value_min_days'] == 2)
        rb2.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_min_days', 2)
        )
        button_group.addButton(rb2)
        params_layout.addWidget(rb2)

        rb3 = QRadioButton("3일 전체")
        rb3.setChecked(self.settings['trading_value_min_days'] == 3)
        rb3.toggled.connect(
            lambda checked: checked and self._update_setting('trading_value_min_days', 3)
        )
        button_group.addButton(rb3)
        params_layout.addWidget(rb3)

        setting = SettingItem(
            label="거래대금 조건 (D/D+1/D+2 중 N일)",
            description="D/D+1/D+2 중 최소 N일 이상 조건 만족 (현재: {:,.0f}억원)".format(
                self.settings['min_trading_value'] / 100_000_000
            ),
            control_widget=params_widget,
            checked=self.settings['trading_value_enabled']
        )
        setting.toggled.connect(
            lambda checked: self._update_setting('trading_value_enabled', checked)
        )

        self.add_widget(setting)

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

        rb1 = QRadioButton("단순 비율 (V2/V1)")
        rb1.setChecked(self.settings['volume_ratio_calculation'] == 'simple')
        rb1.toggled.connect(
            lambda checked: checked and self._update_setting('volume_ratio_calculation', 'simple')
        )
        button_group.addButton(rb1)
        layout.addWidget(rb1)

        rb2 = QRadioButton("정규화 비율 ((V2-avg)/std)")
        rb2.setChecked(self.settings['volume_ratio_calculation'] == 'normalized')
        rb2.toggled.connect(
            lambda checked: checked and self._update_setting('volume_ratio_calculation', 'normalized')
        )
        button_group.addButton(rb2)
        layout.addWidget(rb2)

        return widget

    def _create_comparison_widget(self) -> QWidget:
        """비교 대상 라디오 버튼"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        from PySide6.QtWidgets import QLabel
        label = QLabel("비교 대상")
        label.setStyleSheet(f"""
            color: {theme_manager.colors['text_secondary']};
            font-size: 11px;
        """)
        layout.addWidget(label)

        button_group = QButtonGroup(widget)

        rb1 = QRadioButton("1번 블록 거래량")
        rb1.setChecked(self.settings['volume_ratio_comparison'] == 'block1')
        rb1.toggled.connect(
            lambda checked: checked and self._update_setting('volume_ratio_comparison', 'block1')
        )
        button_group.addButton(rb1)
        layout.addWidget(rb1)

        rb2 = QRadioButton("1번 블록 이전 20일 평균")
        rb2.setChecked(self.settings['volume_ratio_comparison'] == 'avg_20days')
        rb2.toggled.connect(
            lambda checked: checked and self._update_setting('volume_ratio_comparison', 'avg_20days')
        )
        button_group.addButton(rb2)
        layout.addWidget(rb2)

        rb3 = QRadioButton("전체 기간 평균")
        rb3.setChecked(self.settings['volume_ratio_comparison'] == 'total_avg')
        rb3.toggled.connect(
            lambda checked: checked and self._update_setting('volume_ratio_comparison', 'total_avg')
        )
        button_group.addButton(rb3)
        layout.addWidget(rb3)

        return widget


    def _update_pattern_type(self, pattern_key: str, checked: bool):
        """패턴 타입 업데이트"""
        self.settings['pattern_types'][pattern_key] = checked
        self.settingsChanged.emit(self.settings)
        print(f"[DEBUG] Block2 Pattern {pattern_key}: {checked}")

    def _update_setting(self, key: str, value):
        """설정 업데이트"""
        self.settings[key] = value
        self.settingsChanged.emit(self.settings)
        print(f"[DEBUG] Block2 Setting changed: {key} = {value}")

    def _on_pattern_enabled_changed(self, checked: bool):
        """패턴 매칭 활성화/비활성화"""
        self._update_setting('pattern_enabled', checked)

        # 하위 위젯들 활성화/비활성화
        for cb in self.pattern_checkboxes.values():
            cb.setEnabled(checked)
            # 비활성화 시 시각적 표현 강화
            if checked:
                cb.setStyleSheet(f"""
                    QCheckBox {{
                        color: {theme_manager.colors['text_primary']};
                        font-size: 12px;
                        padding: 4px 0;
                    }}
                """)
            else:
                cb.setStyleSheet(f"""
                    QCheckBox {{
                        color: {theme_manager.colors['text_tertiary']};
                        font-size: 12px;
                        padding: 4px 0;
                    }}
                    QCheckBox::indicator {{
                        opacity: 0.3;
                    }}
                """)

        self.pattern_d1_threshold_slider.setEnabled(checked)
        self.pattern_d2_threshold_slider.setEnabled(checked)

        # 슬라이더 투명도 조절
        opacity = 1.0 if checked else 0.4
        self.pattern_d1_threshold_slider.setStyleSheet(f"opacity: {opacity};")
        self.pattern_d2_threshold_slider.setStyleSheet(f"opacity: {opacity};")

    def get_settings(self) -> dict:
        """현재 설정 반환"""
        return self.settings.copy()

    def apply_settings(self, settings: dict):
        """설정 적용"""
        self.settings.update(settings)

    def set_settings(self, settings: dict):
        """설정 적용"""
        self.settings.update(settings)
        # TODO: UI 업데이트
