import os
from pathlib import Path
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import init_db
from models.exchange_services.rate_service import RateService
from routers.exchange_router import frontend_router
from routers.exchange_router import router as api_router

# --- НАСТРОЙКА ПУТЕЙ ---
# Определяем базовую директорию проекта (где лежит этот файл main.py)
BASE_DIR = Path(__file__).resolve().parent
# Формируем полный путь к папке static
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Автоматическое создание папки, если её нет, чтобы избежать RuntimeError
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
# -----------------------

async def daily_rates_update():
    """Ежедневная задача обновления курсов"""
    try:
        rate_service = RateService()
        count = await rate_service.fetch_and_save_rates()
        print(f"Ежедневное обновление курсов выполнено. Загружено {count} записей.")
    except Exception as e:
        print(f"Ошибка ежедневного обновления курсов: {e}")


scheduler: AsyncIOScheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler  # noqa: PLW0603

    print("Запуск сервиса обмена валют...")

    await init_db()
    print("База данных инициализирована")

    try:
        rate_service = RateService()
        count = await rate_service.fetch_and_save_rates()
        print(f"Загружено {count} курсов")
    except Exception as e:
        print(f"Не удалось загрузить курсы при старте: {e}")

    scheduler = AsyncIOScheduler()
    scheduler.start()

    scheduler.add_job(
        daily_rates_update,
        "cron",
        hour=0,
        minute=5,
        id="daily_rates_update",
        replace_existing=True
    )

    print("Планировщик запущен: ежедневное обновление курсов в 00:05")

    yield

    print("Остановка сервиса...")
    if scheduler:
        scheduler.shutdown()


app = FastAPI(
    title="Сервис обмена валют (НБ РБ)",
    version="1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)
app.include_router(frontend_router)

# Используем STATIC_DIR (абсолютный путь) вместо относительной строки "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}