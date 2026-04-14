from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Основные настройки приложения"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # FastAPI
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # База данных
    DATABASE_URL: str = "sqlite+aiosqlite:///./currency_exchange.db"

    # Настройки НБ РБ
    NBRB_BASE_URL: str = "https://api.nbrb.by"


settings = Settings()
