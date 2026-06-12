from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from src.core.database import get_db_helper
from src.repositories import (
    UserRepository,
    TaskRepository,
    ProjectRepository,
    CommentRepository,
    EmailRepository,
)
from src.utils.loguru_config import AppLogger


logger = AppLogger().get_logger()

db_helper = get_db_helper()


def get_db_session():
    session = db_helper.session_factory()
    try:
        yield session
    finally:
        logger.debug(f"Closing session {id(session)}")
        session.close()


DbSession = Annotated[Session, Depends(get_db_session)]


def get_user_repository(session: DbSession):
    return UserRepository(session)


UserRepo = Annotated["UserRepository", Depends(get_user_repository)]


def get_task_repository(session: DbSession):
    return TaskRepository(session)


TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]


def get_project_repository(session: DbSession):
    return ProjectRepository(session)


ProjectRepo = Annotated[ProjectRepository, Depends(get_project_repository)]


def get_comment_repository(session: DbSession):
    return CommentRepository(session)


CommentRepo = Annotated[CommentRepository, Depends(get_comment_repository)]


def get_email_repository(session: DbSession):
    return EmailRepository(session)


EmailRepo = Annotated[EmailRepository, Depends(get_email_repository)]
