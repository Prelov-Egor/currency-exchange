import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DealStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_currency = Column(String(10), nullable=False)
    target_currency = Column(String(10), nullable=False)

    source_amount = Column(Numeric(18, 4), nullable=False)
    target_amount = Column(Numeric(18, 4), nullable=False)
    exchange_rate = Column(Numeric(18, 6), nullable=False)

    status = Column(SQLEnum(DealStatus), default=DealStatus.PENDING, nullable=False)
    completed_at = Column(DateTime, nullable=True)
