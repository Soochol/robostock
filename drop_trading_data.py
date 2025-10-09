"""
Drop trading_data table
레거시 테이블 삭제 스크립트
"""

import sys
sys.path.insert(0, 'src')

from infrastructure.database import get_session
from sqlalchemy import text

def drop_trading_data_table():
    """trading_data 테이블 삭제"""
    with get_session() as session:
        # 테이블 존재 여부 확인
        result = session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trading_data'"
        ))

        if result.fetchone():
            print("[INFO] Dropping trading_data table...")
            session.execute(text("DROP TABLE trading_data"))
            session.commit()
            print("[SUCCESS] trading_data table dropped successfully")
        else:
            print("[INFO] trading_data table does not exist")

if __name__ == "__main__":
    drop_trading_data_table()
