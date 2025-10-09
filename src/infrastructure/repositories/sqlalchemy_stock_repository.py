"""
SQLAlchemy Stock Repository Implementation
종목 Repository 구현체
"""

from typing import Optional, List
from datetime import datetime

from domain.repositories.stock_repository import StockRepository
from domain.entities.stock import Stock as StockEntity
from infrastructure.database.models import Stock as StockORM
from infrastructure.database.connection import get_session
from core.enums import MarketType
from core.exceptions import EntityNotFoundException, DuplicateEntityException


class SQLAlchemyStockRepository(StockRepository):
    """SQLAlchemy 기반 Stock Repository 구현"""

    def _to_entity(self, orm: StockORM) -> StockEntity:
        """ORM 모델 → Domain Entity 변환"""
        if orm is None:
            return None

        return StockEntity(
            id=orm.id,
            code=orm.code,
            name=orm.name,
            market=orm.market,
            sector=orm.sector,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    def _to_orm(self, entity: StockEntity) -> StockORM:
        """Domain Entity → ORM 모델 변환"""
        return StockORM(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            market=entity.market,
            sector=entity.sector,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def get_by_id(self, stock_id: int) -> Optional[StockEntity]:
        """ID로 종목 조회"""
        with get_session() as session:
            orm = session.query(StockORM).filter_by(id=stock_id).first()
            return self._to_entity(orm) if orm else None

    def get_by_code(self, code: str) -> Optional[StockEntity]:
        """종목 코드로 조회"""
        with get_session() as session:
            orm = session.query(StockORM).filter_by(code=code).first()
            return self._to_entity(orm) if orm else None

    def get_all(self, market: Optional[MarketType] = None) -> List[StockEntity]:
        """전체 종목 조회 (시장 필터링 가능)"""
        with get_session() as session:
            query = session.query(StockORM)

            if market is not None:
                query = query.filter_by(market=market)

            orms = query.all()
            return [self._to_entity(orm) for orm in orms]

    def save(self, stock: StockEntity) -> StockEntity:
        """종목 저장 (생성 또는 업데이트)"""
        with get_session() as session:
            if stock.id:
                # 업데이트
                orm = session.query(StockORM).filter_by(id=stock.id).first()
                if not orm:
                    raise EntityNotFoundException("Stock", str(stock.id))

                orm.code = stock.code
                orm.name = stock.name
                orm.market = stock.market
                orm.sector = stock.sector
                orm.updated_at = datetime.now()
            else:
                # 신규 생성
                # 중복 체크
                existing = session.query(StockORM).filter_by(code=stock.code).first()
                if existing:
                    # 기존 데이터 업데이트
                    existing.name = stock.name
                    existing.market = stock.market
                    existing.sector = stock.sector
                    existing.updated_at = datetime.now()
                    orm = existing
                else:
                    orm = self._to_orm(stock)
                    session.add(orm)

            session.flush()
            return self._to_entity(orm)

    def delete(self, stock_id: int) -> bool:
        """종목 삭제"""
        with get_session() as session:
            orm = session.query(StockORM).filter_by(id=stock_id).first()
            if not orm:
                return False

            session.delete(orm)
            return True

    def exists(self, code: str) -> bool:
        """종목 코드 존재 여부 확인"""
        with get_session() as session:
            count = session.query(StockORM).filter_by(code=code).count()
            return count > 0

    def count(self, market: Optional[MarketType] = None) -> int:
        """종목 수 카운트"""
        with get_session() as session:
            query = session.query(StockORM)

            if market is not None:
                query = query.filter_by(market=market)

            return query.count()
