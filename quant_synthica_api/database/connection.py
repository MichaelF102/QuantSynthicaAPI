import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger

settings = get_settings()

Base = declarative_base()

def get_engine():
    # Try connecting to PostgreSQL, fallback to SQLite if PostgreSQL fails
    db_url = settings.DATABASE_URL
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info(f"Database connected using primary URL: {db_url.split('@')[-1]}")
        return engine
    except Exception as e:
        logger.warning(f"Failed to connect to PostgreSQL ({e}). Falling back to SQLite: {settings.SQLITE_FALLBACK_URL}")
        sqlite_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
