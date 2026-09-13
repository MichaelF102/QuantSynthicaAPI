from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
YFINANCE_PATH = PROJECT_ROOT / "yfinance"
TRADINGVIEW_PATH = PROJECT_ROOT / "TradingView-Screener" / "src"

class Settings(BaseSettings):
    API_TITLE: str = "QuantSynthica Market API"
    API_VERSION: str = "1.0.0"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # Security
    API_KEY: str = "qs_live_dev_secret_key_12345"
    API_KEY_REQUIRED: bool = False

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300
    CACHE_QUOTE_TTL: int = 60
    CACHE_FUNDAMENTALS_TTL: int = 86400
    CACHE_QUANT_TTL: int = 900
    CACHE_SCREENER_TTL: int = 300

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/quantsynthica"
    SQLITE_FALLBACK_URL: str = "sqlite:///./quantsynthica.db"

    # Rate Limiting & Throttling
    GLOBAL_RATE_LIMIT: int = 100
    SCREENER_MIN_INTERVAL: float = 1.5
    YFINANCE_MIN_INTERVAL: float = 0.5

    # Path Settings
    PROJECT_ROOT_PATH: Path = PROJECT_ROOT
    YFINANCE_DIR: Path = YFINANCE_PATH
    TRADINGVIEW_DIR: Path = TRADINGVIEW_PATH

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
