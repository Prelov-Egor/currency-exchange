import logging
from datetime import date, datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import AsyncSessionLocal
from models.exchange_services.exchange_service import ExchangeService
from repositories.deal_repo import DealRepository
from repositories.rate_repo import RateRepository
from schemas.exchange import (
    DealHistoryResponse,  # ← новая схема
    ExchangeConfirmRequest,
    ExchangeConfirmResponse,
    ExchangeQuoteRequest,
    ExchangeQuoteResponse,
    PendingDealResponse,
    ReportResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["exchange"])
frontend_router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="templates")



CURRENCY_NAMES = {
    "431": "USD — Доллар США",
    "451": "EUR — Евро",
    "456": "RUB — Российский рубль",
    "371": "UAH — Украинская гривна",
    "421": "PLN — Польский злотый",
    "426": "GBP — Фунт стерлингов",
    "429": "JPY — Японская иена",
    "440": "CHF — Швейцарский франк",
    "449": "CNY — Китайский юань",
    "450": "TRY — Турецкая лира",
    "453": "CZK — Чешская крона",
    "454": "SEK — Шведская крона",
    "455": "NOK — Норвежская крона",
    "457": "DKK — Датская крона",
    "458": "HUF — Венгерский форинт",
    "460": "KZT — Казахстанский тенге",
    "508": "CAD — Канадский доллар",
    "510": "AUD — Австралийский доллар",
    "511": "NZD — Новозеландский доллар",
    "394": "AMD — Армянский драм",
    "448": "GEL — Грузинский лари",
    "452": "AZN — Азербайджанский манат",
    "461": "BYN — Белорусский рубль",
    "462": "MDL — Молдавский лей",
    "463": "TJS — Таджикский сомони",
    "464": "KGS — Киргизский сом",
    "459": "BYN — Белорусский рубль",
}


@router.get("/currencies")
async def get_currencies():
    async with AsyncSessionLocal() as session:
        repo = RateRepository(session)
        today = datetime.utcnow().date()
        rates = await repo.get_rates_by_date(today)

        currencies = []
        for r in rates:
            name = CURRENCY_NAMES.get(r.currency_code, f"{r.currency_code} — Валюта")
            currencies.append({"code": r.currency_code, "name": name})

        currencies.sort(key=lambda x: x["name"])
        return currencies


@router.post("/exchange/quote", response_model=ExchangeQuoteResponse)
async def create_quote(request: ExchangeQuoteRequest):
    service = ExchangeService()
    return await service.create_quote(
        source=request.source_currency, target=request.target_currency, amount=request.amount
    )


@router.post("/exchange/confirm", response_model=ExchangeConfirmResponse)
async def confirm_deal(request: ExchangeConfirmRequest):
    service = ExchangeService()
    return await service.confirm_deal(request.deal_id, request.action)


# === ОТЧЁТ ПО СДЕЛКАМ ===
@router.get("/reports/deals", response_model=ReportResponse)
async def get_report(from_date: date, to_date: date, currency: str | None = None):
    async with AsyncSessionLocal() as session:
        deal_repo = DealRepository(session)
        items = await deal_repo.get_report(from_date, to_date, currency)
        total_deals = sum(item["deals_count"] for item in items)

        return {
            "from_date": from_date,
            "to_date": to_date,
            "total_deals": total_deals,
            "items": items,
        }


#незавешённые
@router.get("/deals/pending", response_model=list[PendingDealResponse])
async def get_pending_deals():
    async with AsyncSessionLocal() as session:
        deal_repo = DealRepository(session)
        return await deal_repo.get_pending_deals()


#все сделки
@router.get("/deals/history", response_model=list[DealHistoryResponse])
async def get_all_deals():
    async with AsyncSessionLocal() as session:
        deal_repo = DealRepository(session)
        return await deal_repo.get_all_deals()


@frontend_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
