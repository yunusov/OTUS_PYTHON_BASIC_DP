from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from src.core.database import get_db_helper
from src.repositories import (
    UserRepository,
    TaskRepository,
    ProjectRepository,
)
from src.utils.loguru_config import AppLogger
logger = AppLogger().get_logger()

db_helper = get_db_helper()

def get_db_session():
    yield db_helper.get_session()

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
