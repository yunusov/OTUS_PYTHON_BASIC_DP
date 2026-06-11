from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core import settings
from src.utils.loguru_config import AppLogger
from .async_session_wrapper import AsyncSessionWrapper


logger = AppLogger().get_logger()

class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool,
        echo_pool: bool,
        pool_size: int,
        max_overflow: int,
    ):
        self.engine: Engine = create_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=True,  # для совместимости с FastAPI_Users
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self):
        self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSessionWrapper]:
        with self.session_factory() as session:
            try:
                yield AsyncSessionWrapper(session)
                session.commit()
            except Exception as e:
                logger.error(e)
                session.rollback()
                raise


@lru_cache(maxsize=1)
def get_db_helper() -> DatabaseHelper:
    return DatabaseHelper(
        url=settings.DATABASE_URL,
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
