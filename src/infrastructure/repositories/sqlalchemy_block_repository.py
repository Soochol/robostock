"""
SQLAlchemy Block Repository Implementation
거래량 블록 Repository 구현체
"""

from typing import Optional, List
from datetime import date, datetime

from domain.repositories.block_repository import BlockRepository
from domain.entities.volume_block import VolumeBlock as BlockEntity
from infrastructure.database.models import VolumeBlock as BlockORM
from infrastructure.database.connection import get_session
from core.enums import BlockType


class SQLAlchemyBlockRepository(BlockRepository):
    """SQLAlchemy 기반 Block Repository 구현"""

    def _to_entity(self, orm: BlockORM) -> BlockEntity:
        """ORM → Entity 변환"""
        if orm is None:
            return None

        return BlockEntity(
            id=orm.id,
            stock_id=orm.stock_id,
            block_type=orm.block_type,
            date=orm.date,
            volume=orm.volume,
            trading_value=orm.trading_value,
            close_price=orm.close_price,
            new_high_grade=orm.new_high_grade,
            max_volume_period_days=orm.max_volume_period_days,
            parent_block_id=orm.parent_block_id,
            days_from_parent=orm.days_from_parent,
            volume_ratio=orm.volume_ratio,
            pattern_type=orm.pattern_type,
            range_end_date=orm.range_end_date,
            range_duration_days=orm.range_duration_days,
            range_high=orm.range_high,
            range_high_date=orm.range_high_date,
            range_low=orm.range_low,
            range_low_date=orm.range_low_date,
            range_avg_volume=orm.range_avg_volume,
            ma60_at_start=orm.ma60_at_start,
            ma60_at_end=orm.ma60_at_end,
            range_end_reason=orm.range_end_reason,
            market_index=orm.market_index,
            range_return=orm.range_return,
            index_return=orm.index_return,
            relative_return=orm.relative_return,
            beta=orm.beta,
            alpha=orm.alpha,
            outperformance=orm.outperformance,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    def _to_orm(self, entity: BlockEntity) -> BlockORM:
        """Entity → ORM 변환"""
        return BlockORM(
            id=entity.id,
            stock_id=entity.stock_id,
            block_type=entity.block_type,
            date=entity.date,
            volume=entity.volume,
            trading_value=entity.trading_value,
            close_price=entity.close_price,
            new_high_grade=entity.new_high_grade,
            max_volume_period_days=entity.max_volume_period_days,
            parent_block_id=entity.parent_block_id,
            days_from_parent=entity.days_from_parent,
            volume_ratio=entity.volume_ratio,
            pattern_type=entity.pattern_type,
            range_end_date=entity.range_end_date,
            range_duration_days=entity.range_duration_days,
            range_high=entity.range_high,
            range_high_date=entity.range_high_date,
            range_low=entity.range_low,
            range_low_date=entity.range_low_date,
            range_avg_volume=entity.range_avg_volume,
            ma60_at_start=entity.ma60_at_start,
            ma60_at_end=entity.ma60_at_end,
            range_end_reason=entity.range_end_reason,
            market_index=entity.market_index,
            range_return=entity.range_return,
            index_return=entity.index_return,
            relative_return=entity.relative_return,
            beta=entity.beta,
            alpha=entity.alpha,
            outperformance=entity.outperformance,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def get_by_id(self, block_id: int) -> Optional[BlockEntity]:
        """ID로 블록 조회"""
        with get_session() as session:
            orm = session.query(BlockORM).filter_by(id=block_id).first()
            return self._to_entity(orm) if orm else None

    def get_by_stock(
        self,
        stock_id: int,
        block_type: Optional[BlockType] = None
    ) -> List[BlockEntity]:
        """종목별 블록 조회 (타입 필터링 가능)"""
        with get_session() as session:
            query = session.query(BlockORM).filter_by(stock_id=stock_id)

            if block_type is not None:
                query = query.filter_by(block_type=block_type)

            orms = query.order_by(BlockORM.date).all()
            return [self._to_entity(orm) for orm in orms]

    def get_by_stock_and_date(
        self,
        stock_id: int,
        target_date: date,
        block_type: Optional[BlockType] = None
    ) -> Optional[BlockEntity]:
        """특정 날짜의 블록 조회"""
        with get_session() as session:
            query = session.query(BlockORM).filter_by(
                stock_id=stock_id,
                date=target_date
            )

            if block_type is not None:
                query = query.filter_by(block_type=block_type)

            orm = query.first()
            return self._to_entity(orm) if orm else None

    def get_by_date_range(
        self,
        stock_id: int,
        start_date: date,
        end_date: date,
        block_type: Optional[BlockType] = None
    ) -> List[BlockEntity]:
        """기간별 블록 조회"""
        with get_session() as session:
            query = session.query(BlockORM).filter(
                BlockORM.stock_id == stock_id,
                BlockORM.date >= start_date,
                BlockORM.date <= end_date
            )

            if block_type is not None:
                query = query.filter_by(block_type=block_type)

            orms = query.order_by(BlockORM.date).all()
            return [self._to_entity(orm) for orm in orms]

    def save(self, block: BlockEntity) -> BlockEntity:
        """블록 저장"""
        with get_session() as session:
            # 기존 블록 확인
            existing = session.query(BlockORM).filter_by(
                stock_id=block.stock_id,
                block_type=block.block_type,
                date=block.date
            ).first()

            if existing:
                # 업데이트
                existing.volume = block.volume
                existing.trading_value = block.trading_value
                existing.close_price = block.close_price
                existing.new_high_grade = block.new_high_grade
                existing.max_volume_period_days = block.max_volume_period_days
                existing.parent_block_id = block.parent_block_id
                existing.days_from_parent = block.days_from_parent
                existing.volume_ratio = block.volume_ratio
                existing.pattern_type = block.pattern_type
                existing.updated_at = datetime.now()
                orm = existing
            else:
                # 신규 생성
                orm = self._to_orm(block)
                session.add(orm)

            session.flush()
            return self._to_entity(orm)

    def save_bulk(self, blocks: List[BlockEntity]) -> int:
        """대량 블록 저장"""
        saved_count = 0

        with get_session() as session:
            for block in blocks:
                existing = session.query(BlockORM).filter_by(
                    stock_id=block.stock_id,
                    block_type=block.block_type,
                    date=block.date
                ).first()

                if not existing:
                    orm = self._to_orm(block)
                    session.add(orm)
                    saved_count += 1

        return saved_count

    def exists(
        self,
        stock_id: int,
        target_date: date,
        block_type: BlockType
    ) -> bool:
        """블록 존재 여부 확인"""
        with get_session() as session:
            count = session.query(BlockORM).filter_by(
                stock_id=stock_id,
                date=target_date,
                block_type=block_type
            ).count()
            return count > 0

    def delete(self, block_id: int) -> bool:
        """블록 삭제"""
        with get_session() as session:
            orm = session.query(BlockORM).filter_by(id=block_id).first()
            if not orm:
                return False

            session.delete(orm)
            return True

    def delete_by_stock(self, stock_id: int) -> int:
        """종목의 모든 블록 삭제"""
        with get_session() as session:
            deleted = session.query(BlockORM).filter_by(
                stock_id=stock_id
            ).delete()
            return deleted

    def count_by_type(
        self,
        stock_id: int,
        block_type: BlockType
    ) -> int:
        """타입별 블록 수 카운트"""
        with get_session() as session:
            count = session.query(BlockORM).filter_by(
                stock_id=stock_id,
                block_type=block_type
            ).count()
            return count
