"""
Database Manager
SQLAlchemy 데이터베이스 연결 및 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging

from infrastructure.database.models import Base
from core.config import DB_PATH

logger = logging.getLogger(__name__)


class DatabaseManager:
    """데이터베이스 관리자 (싱글톤)"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize()

    def _initialize(self):
        """데이터베이스 초기화"""
        # core.config에서 DB 경로 가져오기
        db_path = DB_PATH

        # 디렉토리 확인 (이미 config에서 생성되지만 안전을 위해)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLite 엔진 생성
        database_url = f'sqlite:///{db_path}'
        logger.info(f"Initializing database at: {db_path}")
        self._engine = create_engine(
            database_url,
            echo=False,  # SQL 쿼리 로그 (개발 시 True)
            pool_pre_ping=True,
            connect_args={'check_same_thread': False}  # SQLite용
        )

        # 세션 팩토리 생성
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
        )

    def create_all_tables(self):
        """모든 테이블 생성"""
        Base.metadata.create_all(self._engine)
        logger.info("Database tables created successfully")

    def drop_all_tables(self):
        """모든 테이블 삭제 (주의!)"""
        Base.metadata.drop_all(self._engine)
        logger.warning("Database tables dropped")

    @contextmanager
    def get_session(self):
        """
        세션 컨텍스트 매니저

        Usage:
            with db_manager.get_session() as session:
                stock = session.query(Stock).first()
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_scoped_session(self):
        """스코프드 세션 반환 (직접 관리용)"""
        return self._session_factory()

    def remove_session(self):
        """현재 스레드의 세션 제거"""
        self._session_factory.remove()

    @property
    def engine(self):
        """엔진 반환"""
        return self._engine


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


# 편의 함수들
def init_database():
    """데이터베이스 초기화 (테이블 생성)"""
    db_manager.create_all_tables()


def get_session():
    """세션 컨텍스트 매니저 반환"""
    return db_manager.get_session()


def reset_database():
    """데이터베이스 리셋 (모든 데이터 삭제 후 재생성)"""
    logger.warning("Resetting database...")
    db_manager.drop_all_tables()
    db_manager.create_all_tables()
    logger.info("Database reset complete")
