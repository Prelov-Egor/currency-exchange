from datetime import date

from database import AsyncSessionLocal
from repositories.rate_repo import RateRepository
from utils.nbrb_client import NBRBClient


class RateService:
    """Сервис для работы с курсами валют"""

    async def fetch_and_save_rates(self, on_date: date | None = None) -> int:
        async with AsyncSessionLocal() as session:
            client = NBRBClient()
            repo = RateRepository(session)

            try:
                rates_data = await client.get_daily_rates(on_date)
                await repo.save_rates(rates_data)
                print(f"✅ Курсы успешно сохранены. Получено {len(rates_data)} записей.")
                return len(rates_data)
            except Exception as e:
                print(f"❌ Ошибка при загрузке/сохранении курсов: {e}")
                await session.rollback()
                raise
            finally:
                await client.close()
