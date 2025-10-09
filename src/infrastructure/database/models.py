"""
Database Models
SQLAlchemy ORM 모델 정의
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean,
    ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base, relationship
from core.enums import BlockType, ReturnLevel, MarketType, NewHighGrade, PatternType

Base = declarative_base()


class Stock(Base):
    """종목 정보"""
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # 종목코드
    name = Column(String(100), nullable=False)  # 종목명
    market = Column(SQLEnum(MarketType), nullable=False)  # 시장구분
    sector = Column(String(50))  # 업종
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    price_data = relationship("PriceData", back_populates="stock", cascade="all, delete-orphan")
    blocks = relationship("VolumeBlock", back_populates="stock", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Stock(code='{self.code}', name='{self.name}')>"


class PriceData(Base):
    """일별 주가 데이터 (OHLCV)"""
    __tablename__ = 'price_data'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    trading_value = Column(Float)  # 거래대금 (원)
    market_cap = Column(Float)  # 시가총액 (원)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    stock = relationship("Stock", back_populates="price_data")

    def __repr__(self):
        return f"<PriceData(stock_id={self.stock_id}, date={self.date}, close={self.close})>"


class InvestorTrading(Base):
    """투자자별 거래 데이터 (기관/외국인/개인 일별 매매)"""
    __tablename__ = 'investor_trading'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # 순매수 금액 (원)
    institutional_net_buy = Column(Float)  # 기관 순매수
    foreign_net_buy = Column(Float)  # 외국인 순매수
    individual_net_buy = Column(Float)  # 개인 순매수
    program_net_buy = Column(Float)  # 프로그램 순매수

    # 매수/매도 금액 (원)
    institutional_buy = Column(Float)  # 기관 매수
    institutional_sell = Column(Float)  # 기관 매도
    foreign_buy = Column(Float)  # 외국인 매수
    foreign_sell = Column(Float)  # 외국인 매도
    individual_buy = Column(Float)  # 개인 매수
    individual_sell = Column(Float)  # 개인 매도

    # 순매수 거래량 (주)
    institutional_net_volume = Column(Integer)  # 기관 순매수 거래량
    foreign_net_volume = Column(Integer)  # 외국인 순매수 거래량
    individual_net_volume = Column(Integer)  # 개인 순매수 거래량

    # 매수강세 지수 (%)
    institutional_buying_strength = Column(Float)
    foreign_buying_strength = Column(Float)
    individual_buying_strength = Column(Float)
    foreign_institutional_buying_strength = Column(Float)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<InvestorTrading(stock_id={self.stock_id}, date={self.date})>"


class VolumeBlock(Base):
    """거래량 블록"""
    __tablename__ = 'volume_blocks'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    block_type = Column(SQLEnum(BlockType), nullable=False, index=True)  # 1번/2번/3번/4번
    date = Column(Date, nullable=False, index=True)  # 블록 발생일

    # 블록 정보
    volume = Column(Integer, nullable=False)  # 거래량
    trading_value = Column(Float, nullable=False)  # 거래대금
    close_price = Column(Float, nullable=False)  # 종가

    # 1번 블록 전용 필드
    new_high_grade = Column(SQLEnum(NewHighGrade))  # 신고가 등급
    max_volume_period_days = Column(Integer)  # 최대거래량 기간(일)

    # 2번 블록 전용 필드
    parent_block_id = Column(Integer, ForeignKey('volume_blocks.id'))
    days_from_parent = Column(Integer)
    volume_ratio = Column(Float)
    pattern_type = Column(SQLEnum(PatternType))

    # Range 정보 (블록 기간: D일 ~ 60이평선 회귀일)
    range_end_date = Column(Date)
    range_duration_days = Column(Integer)
    range_high = Column(Float)
    range_high_date = Column(Date)
    range_low = Column(Float)
    range_low_date = Column(Date)
    range_avg_volume = Column(Integer)
    ma60_at_start = Column(Float)
    ma60_at_end = Column(Float)
    range_end_reason = Column(String(20))

    # 시장 대비 성과
    market_index = Column(String(10))
    range_return = Column(Float)
    index_return = Column(Float)
    relative_return = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)
    outperformance = Column(Boolean)

    # 지지선 정보
    support_levels = relationship(
        "SupportLevel",
        back_populates="block",
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    stock = relationship("Stock", back_populates="blocks")
    parent_block = relationship("VolumeBlock", remote_side=[id])
    cases = relationship("Case", back_populates="first_block")

    def __repr__(self):
        return f"<VolumeBlock(stock_id={self.stock_id}, type={self.block_type}, date={self.date})>"


class BlockPatternData(Base):
    """2번 블록 D+1, D+2 패턴 상세 데이터"""
    __tablename__ = 'block_pattern_data'

    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('volume_blocks.id'), nullable=False)
    day_offset = Column(Integer, nullable=False)

    # 가격 데이터
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    trading_value = Column(Float)

    # D일 대비 비율
    volume_ratio_vs_d = Column(Float)

    # 수급 데이터
    institutional_net_buy = Column(Float)
    foreign_net_buy = Column(Float)
    individual_net_buy = Column(Float)
    program_net_buy = Column(Float)
    institutional_buying_strength = Column(Float)
    foreign_buying_strength = Column(Float)
    foreign_institutional_buying_strength = Column(Float)

    # 조건 만족 여부
    is_qualified = Column(Boolean)
    is_high_breakout = Column(Boolean)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<BlockPatternData(block_id={self.block_id}, D+{self.day_offset})>"


class SupportLevel(Base):
    """지지선 (2번 블록 기준)"""
    __tablename__ = 'support_levels'

    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('volume_blocks.id'), nullable=False)
    level_number = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    label = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    block = relationship("VolumeBlock", back_populates="support_levels")

    def __repr__(self):
        return f"<SupportLevel(block_id={self.block_id}, level={self.level_number}, price={self.price})>"


class Case(Base):
    """케이스 (1번 블록 발생 시점)"""
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    first_block_id = Column(Integer, ForeignKey('volume_blocks.id'), nullable=False, index=True)

    # 케이스 정보
    case_date = Column(Date, nullable=False, index=True)  # 케이스 생성일 (1번 블록 날짜)
    status = Column(String(20), default='active')  # active/completed/failed

    # 수익 정보
    entry_price = Column(Float)  # 진입가 (2번 블록 종가)
    peak_price = Column(Float)  # 최고가
    peak_date = Column(Date)  # 최고가 날짜
    max_return = Column(Float)  # 최대 수익률 (%)
    return_level = Column(SQLEnum(ReturnLevel))  # 수익 Level (0-4)

    # 분석 결과
    factor_scores = relationship("FactorScore", back_populates="case", cascade="all, delete-orphan")
    prediction = relationship("PredictionResult", back_populates="case", uselist=False, cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    stock = relationship("Stock", back_populates="cases")
    first_block = relationship("VolumeBlock", back_populates="cases")

    def __repr__(self):
        return f"<Case(id={self.id}, stock_id={self.stock_id}, date={self.case_date}, level={self.return_level})>"


class FactorScore(Base):
    """팩터 스코어"""
    __tablename__ = 'factor_scores'

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'), nullable=False, index=True)

    # 팩터별 점수 (0-100)
    technical_score = Column(Float, default=0)  # 기술적 분석
    financial_score = Column(Float, default=0)  # 재무 분석
    supply_score = Column(Float, default=0)  # 수급 분석
    industry_score = Column(Float, default=0)  # 산업 분석
    pattern_score = Column(Float, default=0)  # 패턴 분석

    # 종합 점수
    total_score = Column(Float, default=0)

    # 상세 정보 (JSON)
    details = Column(Text)  # JSON 형식으로 저장

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    case = relationship("Case", back_populates="factor_scores")

    def __repr__(self):
        return f"<FactorScore(case_id={self.case_id}, total={self.total_score})>"


class PredictionResult(Base):
    """예측 결과"""
    __tablename__ = 'prediction_results'

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'), nullable=False, unique=True, index=True)

    # Level별 확률 (0-1)
    prob_level_0 = Column(Float, default=0)  # 실패 확률
    prob_level_1 = Column(Float, default=0)  # 저수익 확률
    prob_level_2 = Column(Float, default=0)  # 중수익 확률
    prob_level_3 = Column(Float, default=0)  # 고수익 확률
    prob_level_4 = Column(Float, default=0)  # 초고수익 확률

    # 예측 결과
    predicted_level = Column(SQLEnum(ReturnLevel))  # 예측 Level
    confidence = Column(Float)  # 신뢰도 (0-1)

    # 모델 정보
    model_version = Column(String(50))
    features_used = Column(Text)  # JSON 형식

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    case = relationship("Case", back_populates="prediction")

    def __repr__(self):
        return f"<PredictionResult(case_id={self.case_id}, level={self.predicted_level})>"


class FinancialData(Base):
    """재무제표 데이터"""
    __tablename__ = 'financial_data'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)  # 보고서 기준일

    # 재무비율
    per = Column(Float)  # PER
    pbr = Column(Float)  # PBR
    roe = Column(Float)  # ROE (%)
    roa = Column(Float)  # ROA (%)
    debt_ratio = Column(Float)  # 부채비율 (%)

    # 손익
    revenue = Column(Float)  # 매출액 (억원)
    operating_profit = Column(Float)  # 영업이익 (억원)
    net_income = Column(Float)  # 당기순이익 (억원)

    # 성장성
    revenue_growth = Column(Float)  # 매출 성장률 (%)
    profit_growth = Column(Float)  # 이익 성장률 (%)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<FinancialData(stock_id={self.stock_id}, date={self.report_date})>"


class BacktestResult(Base):
    """백테스팅 결과"""
    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 백테스트 이름
    description = Column(Text)

    # 기간
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # 성과
    total_cases = Column(Integer)  # 총 케이스 수
    win_rate = Column(Float)  # 승률 (%)
    avg_return = Column(Float)  # 평균 수익률 (%)
    max_return = Column(Float)  # 최대 수익률 (%)
    min_return = Column(Float)  # 최소 수익률 (%)

    # Level별 분포
    level_0_count = Column(Integer, default=0)
    level_1_count = Column(Integer, default=0)
    level_2_count = Column(Integer, default=0)
    level_3_count = Column(Integer, default=0)
    level_4_count = Column(Integer, default=0)

    # 상세 결과 (JSON)
    details = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<BacktestResult(name='{self.name}', win_rate={self.win_rate})>"
