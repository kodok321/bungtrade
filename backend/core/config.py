import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "BungTrade AI Trading Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/bungtrade"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@db:5432/bungtrade"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Encryption
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long!"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Binance defaults
    BINANCE_TESTNET: bool = False

    # Risk defaults
    DEFAULT_RISK_PER_TRADE: float = 2.0
    DEFAULT_MAX_DAILY_LOSS: float = 5.0
    DEFAULT_MAX_DRAWDOWN: float = 10.0
    DEFAULT_MAX_CONCURRENT_TRADES: int = 5

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
