import logging
from datetime import datetime
from decimal import Decimal

from database import AsyncSessionLocal
from models.deal import Deal, DealStatus
from repositories.deal_repo import DealRepository
from repositories.rate_repo import RateRepository

logger = logging.getLogger(__name__)


# Маппинг: внутренний код НБ РБ → понятный код валюты
CODE_TO_ABBR = {
    "431": "USD",
    "451": "EUR",
    "456": "RUB",
    "371": "UAH",
    "421": "PLN",
    "426": "GBP",
    "429": "JPY",
    "440": "CHF",
    "449": "CNY",
    "450": "TRY",
    "453": "CZK",
    "454": "SEK",
    "455": "NOK",
    "457": "DKK",
    "458": "HUF",
    "460": "KZT",
    "508": "CAD",
    "510": "AUD",
    "511": "NZD",
    "461": "BYN",
    "459": "BYN",
    "394": "AMD",
    "448": "GEL",
    "452": "AZN",
    "462": "MDL",
    "463": "TJS",
    "464": "KGS",
}


class ExchangeService:
    """Основная бизнес-логика обмена валют"""

    async def create_quote(self, source: str, target: str, amount: Decimal) -> dict:
        """1 этап — расчёт котировки"""
        logger.info(f"Получен запрос: {source} → {target}, сумма={amount}")

        async with AsyncSessionLocal() as session:
            rate_repo = RateRepository(session)

            today = datetime.utcnow().date()
            rates = await rate_repo.get_rates_by_date(today)

            source_rate = next((r for r in rates if r.currency_code == source), None)
            target_rate = next((r for r in rates if r.currency_code == target), None)

            if not source_rate or not target_rate:
                raise ValueError("Курс для одной из валют не найден")

            # Правильный кросс-курс
            cross_rate = (source_rate.rate / source_rate.scale) / (
                target_rate.rate / target_rate.scale
            )
            amount_in_byn = amount * source_rate.rate / source_rate.scale
            target_amount = amount_in_byn * target_rate.scale / target_rate.rate

            # Преобразуем внутренние коды в понятные (USD, EUR и т.д.)
            source_abbr = CODE_TO_ABBR.get(source, source)
            target_abbr = CODE_TO_ABBR.get(target, target)

            # Создаём сделку
            deal_repo = DealRepository(session)
            deal = Deal(
                source_currency=source_abbr,
                target_currency=target_abbr,
                source_amount=amount,
                target_amount=target_amount,
                exchange_rate=cross_rate,
            )

            deal = await deal_repo.create(deal)

            return {
                "deal_id": deal.id,
                "source_currency": source_abbr,  # теперь USD, EUR
                "source_amount": float(amount),
                "target_currency": target_abbr,  # теперь USD, EUR
                "target_amount": round(float(target_amount), 4),
                "exchange_rate": round(float(cross_rate), 6),
                "message": "Обмен рассчитан",
            }

    async def confirm_deal(self, deal_id: int, action: str) -> dict:
        async with AsyncSessionLocal() as session:
            deal_repo = DealRepository(session)
            status = DealStatus.CONFIRMED if action == "confirm" else DealStatus.REJECTED

            deal = await deal_repo.update_status(deal_id, status)

            if not deal:
                raise ValueError(f"Сделка {deal_id} не найдена")

            return {
                "deal_id": deal.id,
                "status": deal.status.value,
                "message": (
                    "Сделка подтверждена" if status == DealStatus.CONFIRMED else "Сделка отклонена"
                ),
            }
