from sqlalchemy import Column, Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CurrencyRate(Base):
    """Модель для хранения курсов валют от НБ РБ"""

    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    currency_code = Column(String(10), nullable=False)
    scale = Column(Integer, nullable=False, default=1)
    rate = Column(Numeric(10, 4), nullable=False)  # Курс с точностью до 4 знаков

    # Уникальность: на одну дату не может быть двух одинаковых валют
    __table_args__ = (UniqueConstraint("date", "currency_code", name="uq_date_currency"),)

    def __repr__(self):
        return f"<CurrencyRate({self.currency_code}={self.rate} на {self.date})>"
