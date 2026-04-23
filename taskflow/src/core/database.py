from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker
import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from taskflow.src.core.config import settings


# asyncio.run(get_version_async())

sync_engine = create_engine(url=settings.DATABASE_URL, echo=True)
#async_engine = create_async_engine(url=settings.DATABASE_URL_ASYNC, echo=True)

session_factory = sessionmaker(sync_engine)
#async_session_factory = async_sessionmaker(async_engine)


int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

created_at = Annotated[
    datetime.datetime, mapped_column(server_default=func.now())
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda *args: datetime.datetime.now(datetime.UTC),
    ),
]

def get_db_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()

DbSession = Annotated[Session, Depends(get_db_session)]


class BaseOrm(DeclarativeBase):
    id: Mapped[int_pk]