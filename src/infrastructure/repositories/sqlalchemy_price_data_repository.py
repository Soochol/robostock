"""
SQLAlchemy Price Data Repository Implementation
주가 데이터 Repository 구현체
"""

from typing import Optional, List
from datetime import date, datetime

from domain.repositories.price_data_repository import PriceDataRepository
from domain.entities.price_data import PriceData as PriceDataEntity
from infrastructure.database.models import PriceData as PriceDataORM
from infrastructure.database.connection import get_session
from sqlalchemy import func


class SQLAlchemyPriceDataRepository(PriceDataRepository):
    """SQLAlchemy 기반 PriceData Repository 구현"""

    def _to_entity(self, orm: PriceDataORM) -> PriceDataEntity:
        """ORM → Entity 변환"""
        if orm is None:
            return None

        return PriceDataEntity(
            id=orm.id,
            stock_id=orm.stock_id,
            date=orm.date,
            open=orm.open,
            high=orm.high,
            low=orm.low,
            close=orm.close,
            volume=orm.volume,
            trading_value=orm.trading_value,
            market_cap=orm.market_cap,
            created_at=orm.created_at
        )

    def _to_orm(self, entity: PriceDataEntity) -> PriceDataORM:
        """Entity → ORM 변환"""
        return PriceDataORM(
            id=entity.id,
            stock_id=entity.stock_id,
            date=entity.date,
            open=entity.open,
            high=entity.high,
            low=entity.low,
            close=entity.close,
            volume=entity.volume,
            trading_value=entity.trading_value,
            market_cap=entity.market_cap,
            created_at=entity.created_at
        )

    def get_by_stock_and_date(
        self,
        stock_id: int,
        target_date: date
    ) -> Optional[PriceDataEntity]:
        """특정 날짜의 주가 데이터 조회"""
        with get_session() as session:
            orm = session.query(PriceDataORM).filter_by(
                stock_id=stock_id,
                date=target_date
            ).first()
            return self._to_entity(orm) if orm else None

    def get_by_stock_range(
        self,
        stock_id: int,
        start_date: date,
        end_date: date
    ) -> List[PriceDataEntity]:
        """기간별 주가 데이터 조회"""
        with get_session() as session:
            orms = session.query(PriceDataORM).filter(
                PriceDataORM.stock_id == stock_id,
                PriceDataORM.date >= start_date,
                PriceDataORM.date <= end_date
            ).order_by(PriceDataORM.date).all()

            return [self._to_entity(orm) for orm in orms]

    def get_latest(self, stock_id: int) -> Optional[PriceDataEntity]:
        """최신 주가 데이터 조회"""
        with get_session() as session:
            orm = session.query(PriceDataORM).filter_by(
                stock_id=stock_id
            ).order_by(PriceDataORM.date.desc()).first()

            return self._to_entity(orm) if orm else None

    def get_latest_date(self, stock_id: int) -> Optional[date]:
        """최신 데이터 날짜 조회"""
        with get_session() as session:
            result = session.query(
                func.max(PriceDataORM.date)
            ).filter_by(stock_id=stock_id).scalar()

            return result

    def save(self, price_data: PriceDataEntity) -> PriceDataEntity:
        """주가 데이터 저장"""
        with get_session() as session:
            # 기존 데이터 확인
            existing = session.query(PriceDataORM).filter_by(
                stock_id=price_data.stock_id,
                date=price_data.date
            ).first()

            if existing:
                # 업데이트
                existing.open = price_data.open
                existing.high = price_data.high
                existing.low = price_data.low
                existing.close = price_data.close
                existing.volume = price_data.volume
                existing.trading_value = price_data.trading_value
                existing.market_cap = price_data.market_cap
                orm = existing
            else:
                # 신규 생성
                orm = self._to_orm(price_data)
                session.add(orm)

            session.flush()
            return self._to_entity(orm)

    def save_bulk(self, price_data_list: List[PriceDataEntity]) -> int:
        """대량 주가 데이터 저장"""
        saved_count = 0

        with get_session() as session:
            for price_data in price_data_list:
                # 기존 데이터 확인
                existing = session.query(PriceDataORM).filter_by(
                    stock_id=price_data.stock_id,
                    date=price_data.date
                ).first()

                if existing:
                    # 업데이트
                    existing.open = price_data.open
                    existing.high = price_data.high
                    existing.low = price_data.low
                    existing.close = price_data.close
                    existing.volume = price_data.volume
                    existing.trading_value = price_data.trading_value
                    existing.market_cap = price_data.market_cap
                else:
                    # 신규 생성
                    orm = self._to_orm(price_data)
                    session.add(orm)
                    saved_count += 1

        return saved_count

    def exists(self, stock_id: int, target_date: date) -> bool:
        """특정 날짜 데이터 존재 여부"""
        with get_session() as session:
            count = session.query(PriceDataORM).filter_by(
                stock_id=stock_id,
                date=target_date
            ).count()
            return count > 0

    def delete_by_stock(self, stock_id: int) -> int:
        """종목의 모든 주가 데이터 삭제"""
        with get_session() as session:
            deleted = session.query(PriceDataORM).filter_by(
                stock_id=stock_id
            ).delete()
            return deleted
