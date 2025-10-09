"""
Data Package (Backward Compatibility)
하위 호환성을 위한 re-export

Note: 실제 구현은 infrastructure.database로 이동됨
"""

# 하위 호환성을 위해 infrastructure에서 re-export
from infrastructure.database import db_manager, init_database, get_session, reset_database
from infrastructure.database.models import (
    Stock, PriceData, VolumeBlock, SupportLevel,
    Case, FactorScore, PredictionResult,
    FinancialData, BacktestResult
)

__all__ = [
    'db_manager',
    'init_database',
    'get_session',
    'reset_database',
    'Stock',
    'PriceData',
    'VolumeBlock',
    'SupportLevel',
    'Case',
    'FactorScore',
    'PredictionResult',
    'FinancialData',
    'BacktestResult',
]
