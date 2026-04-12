from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings


# asyncio.run(get_version_async())

sync_engine = create_engine(url=settings.DATABASE_URL, echo=True)
async_engine = create_async_engine(url=settings.DATABASE_URL_ASYNC, echo=True)

session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)
