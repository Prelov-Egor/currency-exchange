from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.deal import Deal, DealStatus


class DealRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, deal: Deal) -> Deal:
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        return deal

    async def get_by_id(self, deal_id: int) -> Deal | None:
        stmt = select(Deal).where(Deal.id == deal_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, deal_id: int, status: DealStatus) -> Deal | None:
        deal = await self.get_by_id(deal_id)
        if not deal:
            return None
        deal.status = status
        if status in (DealStatus.CONFIRMED, DealStatus.REJECTED):
            deal.completed_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(deal)
        return deal

    async def get_pending(self) -> list[Deal]:
        stmt = select(Deal).where(Deal.status == DealStatus.PENDING)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # === ОТЧЁТ ПО СДЕЛКАМ ЗА ПЕРИОД ===
    async def get_report(
        self, from_date: date, to_date: date, currency: str | None = None
    ) -> list[dict]:
        stmt = select(
            Deal.source_currency.label("currency"),
            func.sum(Deal.source_amount).label("cash_in"),
            func.sum(Deal.target_amount).label("cash_out"),
            func.count(Deal.id).label("deals_count"),
        ).where(
            Deal.created_at >= from_date,
            Deal.created_at <= to_date,
            Deal.status == DealStatus.CONFIRMED,
        )

        if currency:
            stmt = stmt.where(
                (Deal.source_currency == currency) | (Deal.target_currency == currency)
            )

        stmt = stmt.group_by(Deal.source_currency)
        result = await self.session.execute(stmt)
        return [row._mapping for row in result]

    # === СПИСОК НЕЗАВЕРШЁННЫХ СДЕЛОК ===
    async def get_pending_deals(self) -> list[dict]:
        stmt = (
            select(Deal).where(Deal.status == DealStatus.PENDING).order_by(Deal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        deals = result.scalars().all()

        return [
            {
                "deal_id": d.id,
                "source_currency": d.source_currency,
                "target_currency": d.target_currency,
                "source_amount": d.source_amount,
                "target_amount": d.target_amount,
                "exchange_rate": d.exchange_rate,
                "created_at": d.created_at,
            }
            for d in deals
        ]

    # === ИСТОРИЯ ВСЕХ СДЕЛОК ===
    async def get_all_deals(self) -> list[dict]:
        """История всех сделок (confirmed + rejected)"""
        stmt = select(Deal).order_by(Deal.created_at.desc())
        result = await self.session.execute(stmt)
        deals = result.scalars().all()

        return [
            {
                "deal_id": d.id,
                "source_currency": d.source_currency,
                "target_currency": d.target_currency,
                "source_amount": d.source_amount,
                "target_amount": d.target_amount,
                "exchange_rate": d.exchange_rate,
                "status": d.status.value,
                "created_at": d.created_at,
                "completed_at": d.completed_at,
            }
            for d in deals
        ]
