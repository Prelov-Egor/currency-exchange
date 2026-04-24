import logging
from datetime import date

from database import AsyncSessionLocal
from repositories.rate_repo import RateRepository
from utils.nbrb_client import NBRBClient

# Настройка базового логирования
logger = logging.getLogger(__name__)


class RateService:
    """Сервис для управления курсами валют"""

    async def fetch_and_save_rates(self, on_date: date | None = None) -> int:
        async with AsyncSessionLocal() as session:
            client = NBRBClient()
            repo = RateRepository(session)

            try:
                rates_data = await client.get_daily_rates(on_date)
                await repo.save_rates(rates_data)

                logger.info(f"Rates saved successfully. Total records: {len(rates_data)}")
                return len(rates_data)

            except Exception as e:
                logger.error(f"Failed to fetch or save rates: {e}")
                await session.rollback()
                raise
            finally:
                await client.close()