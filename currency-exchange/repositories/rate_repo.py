import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.rate import CurrencyRate

logger = logging.getLogger(__name__)


class RateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_rates(self, rates_data: list[dict]) -> None:
        """Сохраняет курсы в БД (идемпотентно) с улучшенной защитой"""
        saved_count = 0
        skipped_count = 0

        for item in rates_data:
            # Улучшенная защита от отсутствующих полей
            currency_code = (
                item.get("Cur_Abbr") or item.get("CurAbbr") or str(item.get("Cur_ID", "")).strip()
            )

            official_rate = item.get("Cur_OfficialRate")

            # Пропускаем некорректные записи
            if not currency_code or currency_code == "" or official_rate is None:
                logger.warning(f"Пропущена запись без кода валюты: {item.get('Cur_ID')}")
                skipped_count += 1
                continue

            try:
                rate_obj = CurrencyRate(
                    date=date.fromisoformat(item["Date"][:10]),
                    currency_code=currency_code.upper(),
                    scale=item.get("Cur_Scale", 1),
                    rate=Decimal(str(official_rate)),
                )

                # Проверяем существование
                stmt = select(CurrencyRate).where(
                    CurrencyRate.date == rate_obj.date,
                    CurrencyRate.currency_code == rate_obj.currency_code,
                )
                result = await self.session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.rate = rate_obj.rate
                    existing.scale = rate_obj.scale
                else:
                    self.session.add(rate_obj)

                saved_count += 1

            except Exception as e:
                logger.error(f"Ошибка при обработке валюты {currency_code}: {e}")
                skipped_count += 1

        await self.session.commit()
        logger.info(f"✅ Сохранено {saved_count} курсов | Пропущено {skipped_count} записей")

    async def get_rates_by_date(self, target_date: date) -> list[CurrencyRate]:
        """Возвращает все курсы на указанную дату"""
        stmt = select(CurrencyRate).where(CurrencyRate.date == target_date)
        result = await self.session.execute(stmt)
        return result.scalars().all()
