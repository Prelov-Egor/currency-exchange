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
        """Сохранение курсов в БД с проверкой на дубликаты"""
        saved_count = 0
        skipped_count = 0

        for item in rates_data:
            # Обработка различных вариантов ключей в ответе API
            currency_code = (
                item.get("Cur_Abbr")
                or item.get("CurAbbr")
                or str(item.get("Cur_ID", "")).strip()
            )

            official_rate = item.get("Cur_OfficialRate")

            # Валидация входных данных
            if not currency_code or official_rate is None:
                logger.warning(f"Skipping record with missing data: ID {item.get('Cur_ID')}")
                skipped_count += 1
                continue

            try:
                rate_val = Decimal(str(official_rate))
                rate_date = date.fromisoformat(item["Date"][:10])
                code_upper = currency_code.upper()

                # Проверка наличия записи в базе для предотвращения дублирования
                stmt = select(CurrencyRate).where(
                    CurrencyRate.date == rate_date,
                    CurrencyRate.currency_code == code_upper,
                )
                result = await self.session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.rate = rate_val
                    existing.scale = item.get("Cur_Scale", 1)
                else:
                    new_rate = CurrencyRate(
                        date=rate_date,
                        currency_code=code_upper,
                        scale=item.get("Cur_Scale", 1),
                        rate=rate_val,
                    )
                    self.session.add(new_rate)

                saved_count += 1

            except Exception as e:
                logger.error(f"Error processing currency {currency_code}: {e}")
                skipped_count += 1

        await self.session.commit()
        logger.info(f"Sync complete. Saved: {saved_count}, Skipped: {skipped_count}")

    async def get_rates_by_date(self, target_date: date) -> list[CurrencyRate]:
        """Получение списка курсов на конкретную дату"""
        stmt = select(CurrencyRate).where(CurrencyRate.date == target_date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())