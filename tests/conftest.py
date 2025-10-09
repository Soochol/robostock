"""
Pytest Configuration
테스트 픽스처 및 설정
"""

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pytest
from data.database import DatabaseManager


@pytest.fixture(scope="session")
def db_manager():
    """테스트용 데이터베이스 매니저"""
    manager = DatabaseManager()
    yield manager
    # 테스트 후 정리
    manager.remove_session()


@pytest.fixture(scope="function")
def db_session(db_manager):
    """각 테스트마다 새로운 세션"""
    with db_manager.get_session() as session:
        yield session
