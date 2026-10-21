from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import logging
from app.core.config import get_settings

_settings = get_settings()
logger = logging.getLogger(__name__)

logger.info("creating db engine")
engine = create_engine(
    str(_settings.app_db_url),
    pool_pre_ping=True,
    pool_size=_settings.app_db_pool_size,
    max_overflow=_settings.app_db_max_overflow,
    connect_args={"connect_timeout": _settings.app_db_connect_timeout_seconds},
)

logger.info("Initialising session maker")
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    logger.info("Opening database session for request")
    with SessionLocal() as db:
        try:
            yield db
        finally:
            logger.info("Closing database session")