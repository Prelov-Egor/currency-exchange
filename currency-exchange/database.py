from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings  # ← исправлено

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Создаёт все таблицы"""
    from models.deal import Base as DealBase
    from models.rate import Base as RateBase

    async with engine.begin() as conn:
        await conn.run_sync(RateBase.metadata.create_all)
        await conn.run_sync(DealBase.metadata.create_all)
    print(" Все таблицы БД созданы")
