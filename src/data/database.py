"""
Database Module (Backward Compatibility)
하위 호환성을 위한 re-export

실제 구현: infrastructure.database.connection
"""

from infrastructure.database.connection import (
    DatabaseManager,
    db_manager,
    get_session,
    init_database,
    reset_database
)

__all__ = [
    'DatabaseManager',
    'db_manager',
    'get_session',
    'init_database',
    'reset_database',
]
