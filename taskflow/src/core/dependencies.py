from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from src.repositories.user_repository import UserRepository
from .database import session_factory


def get_db_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db_session)]


def get_user_repository(session: DbSession):
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
