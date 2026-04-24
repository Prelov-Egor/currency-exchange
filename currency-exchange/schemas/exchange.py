from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExchangeQuoteRequest(BaseModel):
    source_currency: str = Field(..., description="Исходная валюта")
    target_currency: str = Field(..., description="Целевая валюта")
    amount: Decimal = Field(..., gt=0, description="Сумма для обмена")


class ExchangeQuoteResponse(BaseModel):
    deal_id: int
    source_currency: str
    source_amount: Decimal
    target_currency: str
    target_amount: Decimal
    exchange_rate: Decimal
    message: str = "Обмен рассчитан. Подтвердите сделку."


class ExchangeConfirmRequest(BaseModel):
    deal_id: int
    action: str = Field(..., pattern="^(confirm|reject)$")


class ExchangeConfirmResponse(BaseModel):
    deal_id: int
    status: str
    message: str



class ReportItem(BaseModel):
    currency: str
    cash_in: Decimal
    cash_out: Decimal
    deals_count: int


class ReportResponse(BaseModel):
    from_date: date
    to_date: date
    total_deals: int
    items: list[ReportItem]


#незавершенные сделки
class PendingDealResponse(BaseModel):
    deal_id: int
    source_currency: str
    target_currency: str
    source_amount: Decimal
    target_amount: Decimal
    exchange_rate: Decimal
    created_at: datetime


#история
class DealHistoryResponse(BaseModel):
    deal_id: int
    source_currency: str
    target_currency: str
    source_amount: Decimal
    target_amount: Decimal
    exchange_rate: Decimal
    status: str
    created_at: datetime
    completed_at: datetime | None = None
